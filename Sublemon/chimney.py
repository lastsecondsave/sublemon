import collections
import copy
import os
import subprocess

from threading import Lock, Thread

import sublime
from sublime_plugin import TextCommand, WindowCommand

import Sublemon.lib.util as util


class Pipe(object):
    def output(self, line):
        self.next_pipe.output(line)

    def error(self, line):
        self.next_pipe.error(line)

    def flush(self):
        self.next_pipe.flush()

    def attach(self, next_pipe):
        link_point = self
        while hasattr(link_point, 'next_pipe'):
            link_point = link_point.next_pipe
        link_point.next_pipe = next_pipe


class CleanEmptyLinesPipe(Pipe):
    def __init__(self):
        self.output_was_empty = False
        self.error_was_empty = False

    def output(self, line):
        if line.strip():
            if self.output_was_empty:
                self.output_was_empty = False
                self.next_pipe.output('')
            self.next_pipe.output(line)
        else:
            self.output_was_empty = True

    def error(self, line):
        if line.strip():
            if self.error_was_empty:
                self.error_was_empty = False
                self.next_pipe.error('')
            self.next_pipe.error(line)
        else:
            self.error_was_empty = True


class Buffer(object):
    def __init__(self, output, encoding='utf-8'):
        self.buffer = []
        self.encoding = encoding
        self.output = output

    def write(self, chunk):
        try:
            chunk = chunk.decode(self.encoding)
        except:
            chunk = "[DECODE ERROR]"

        b = 0
        e = chunk.find('\n')

        while e != -1:
            self.buffer.append(chunk[b:e])
            self.flush()

            b = e + 1
            e = chunk.find('\n', b)

        self.buffer.append(chunk[b:])

    def flush(self):
        if self.buffer:
            self.output(''.join(self.buffer))
            self.buffer.clear()


class AsyncStreamConsumer(Thread):
    def __init__(self, stream, output, on_close=None):
        super().__init__()
        self.stream = stream
        self.output = output
        self.on_close = on_close

    def run(self):
        while True:
            chunk = os.read(self.stream.fileno(), 2**15)
            if not chunk:
                break
            self.output.write(chunk)

        self.output.flush()
        self.stream.close()

        if self.on_close:
            self.on_close()


class OutputPanel:
    def __init__(self, window):
        self.window = window
        self.view = window.create_output_panel('exec')

        self.line_buffer_lock = Lock()
        self.line_buffer = collections.deque()

        self.set_settings(gutter='False', scroll_past_end='False')

    def reset(self):
        self.view.run_command('erase_view')
        self.line_buffer.clear()

    def set_settings(self,
                     syntax=None, scroll_to_end=False, show_on_text=False,
                     **settings):
        for k, v in settings.items():
            if v:
                self.view.settings().set(k, v)

        if syntax:
            self.view.assign_syntax(syntax)

        self.show_on_text = show_on_text
        self.scroll_to_end = scroll_to_end

    def append_line(self, line):
        with self.line_buffer_lock:
            invalidate = len(self.line_buffer) == 0
            self.line_buffer.append(line)

        if invalidate:
            sublime.set_timeout(self.paint, 0)

    def paint(self):
        with self.line_buffer_lock:
            if len(self.line_buffer) == 0:
                return
            lines = copy.copy(self.line_buffer)
            self.line_buffer.clear()

        characters = ''.join(line.replace('\r', '') + '\n' for line in lines)

        self.view.run_command('append', {
            'characters': characters,
            'force': True,
            'scroll_to_end': self.scroll_to_end
        })

        if self.show_on_text:
            self.show()
            self.show_on_text = False

    def show(self):
        self.window.run_command("show_panel", {"panel": "output.exec"})


class OutputPanelPipe(Pipe):
    def __init__(self, output_panel):
        self.output_panel = output_panel

    def output(self, line):
        self.output_panel.append_line(line)

    def error(self, line):
        self.output_panel.append_line(line)

    def flush(self):
        pass


class Options(object):
    def __init__(self, options_dict):
        self.originals = options_dict

        def option(x, y=None): return options_dict.get(x, y)

        self.kill          = option("kill", False)
        self.cmd           = option("cmd")
        self.shell_cmd     = option("shell_cmd")
        self.file_regex    = option("file_regex", "")
        self.line_regex    = option("line_regex", "")
        self.syntax        = option("syntax", "Packages/Text/Plain text.tmLanguage")
        self.working_dir   = option("working_dir")
        self.show_output   = option("show_output", "text")
        self.scroll_to_end = option("scroll_to_end", True)

    def get(self, arg, default=None):
        return self.originals.get(arg, default)

    def __getitem__(self, arg):
        return self.get(arg)


class Executor(object):
    def __init__(self, window):
        self.window = window
        self.output_panel = OutputPanel(window)
        self.running_state = None
        _log('Created executor for window #{}', window.id())

    def run(self, options, pipe):
        if self.running_state:
            self.kill_process()

        if options.kill:
            return

        self.set_working_dir(options)
        proc = self.start_process(options)

        output_panel_settings = dict(
            result_base_dir   = options.working_dir,
            result_file_regex = options.file_regex,
            result_line_regex = options.line_regex,
            syntax            = options.syntax,
            scroll_to_end     = options.scroll_to_end,
            show_on_text      = options.show_output == "text"
        )

        self.output_panel.reset()
        self.output_panel.set_settings(**output_panel_settings)

        if options.show_output == "always":
            self.output_panel.show()

        output_pipe = OutputPanelPipe(self.output_panel)

        if pipe:
            pipe.attach(output_pipe)
        else:
            pipe = output_pipe

        AsyncStreamConsumer(proc.stdout, Buffer(pipe.output), on_close=self.finish).start()
        AsyncStreamConsumer(proc.stderr, Buffer(pipe.error)).start()

        self.running_state = {'proc': proc, 'options': options, 'pipe': pipe}

    def set_working_dir(self, options):
        if not options.working_dir:
            view = self.window.active_view()
            if view and view.file_name():
                options.working_dir = os.path.dirname(view.file_name())
            return

        if not os.path.isabs(options.working_dir):
            base_path = self.window.extract_variables().get('project_path')
            options.working_dir = os.path.join(base_path, options.working_dir)

    def start_process(self, options):
        if options.shell_cmd and util.RUNNING_ON_WINDOWS:
            options.cmd = ["powershell.exe", "-Command", options.shell_cmd]
        elif options.shell_cmd:
            options.cmd = [os.environ["SHELL"], "-c", options.shell_cmd]

        os.chdir(options.working_dir)
        proc = subprocess.Popen(options.cmd,
                                startupinfo=_get_startupinfo(),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                stdin=subprocess.DEVNULL)

        _log('→ [{}] {}', proc.pid, ' '.join(options.cmd))
        return proc

    def finish(self):
        self.running_state['pipe'].flush()

        show_output = self.running_state['options'].show_output
        errors_count = len(self.output_panel.view.find_all_results())

        if show_output == 'error' and errors_count > 0:
            self.output_panel.show()

        proc = self.running_state['proc']
        proc.poll()

        if proc.returncode:
            _log('✗ [{}] {}', proc.pid, proc.returncode)
        else:
            _log('✓ [{}]', proc.pid)

        self.running_state = None

    def kill_process(self):
        pid = str(self.running_state['proc'].pid)
        _log("Killing {}", pid)

        if util.RUNNING_ON_WINDOWS:
            cmd = ["taskkill", "/PID", pid]
            subprocess.Popen(cmd, startupinfo=_get_startupinfo())
            return

        subprocess.Popen(["kill", pid])
        if self.running_state['options'].shell_cmd is not None:
            subprocess.Popen(["pkill", "-P", pid])


class EraseViewCommand(TextCommand):
    def run(self, edit):
        self.view.erase(edit, sublime.Region(0, self.view.size()))


class ChimneyCommand(WindowCommand):
    def __init__(self, window):
        super().__init__(window)
        _get_executor(window)

    def create_pipe(self, options):
        pass

    def preprocess_options(self, options):
        pass

    def source_file(self):
        return self.window.extract_variables()['file']

    def run(self, **args):
        options = Options(args)
        self.preprocess_options(options)

        pipe = self.create_pipe(options)

        _get_executor(self.window).run(options, pipe)


# TODO: Some sorf of GC?
_executors = {}


def _get_executor(window):
    if not window and not hasattr(window, 'id'):
        raise ValueError("invalid Window object")

    wid = window.id()
    if wid not in _executors:
        _executors[wid] = Executor(window)

    return _executors[wid]


def _get_startupinfo():
    startupinfo = None
    if util.RUNNING_ON_WINDOWS:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    return startupinfo


def _log(message, *params):
    print('Chimney:', message.format(*params))
