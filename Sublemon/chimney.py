import collections
import os
import sublime, sublime_plugin
import subprocess
import sys
import threading

## PIPES ##

class Pipe:
    def output(self, line):
        self.next_pipe.output(line)

    def error(self, line):
        self.next_pipe.error(line)

    def flush(self):
        self.next_pipe.flush()

    def attach(self, next_pipe):
        link_point = self
        while link_point.next_pipe:
            link_point = link_point.next_pipe
        link_point.next_pipe = next_pipe

class OutputPipeBuffer:
    def __init__(self, pipe, encoding="utf-8"):
        self.buffer = ""
        self.encoding = encoding
        self.pipe = pipe

    def next(self, chunk):
        try:
            chunk = chunk.decode(self.encoding)
        except:
            chunk = "[DECODE ERROR]"

        b = 0
        e = chunk.find('\n')

        while e != -1:
            cutoff = chunk[b:e]
            if len(cutoff) > 0 and cutoff[-1] == '\r':
                cutoff = cutoff[:-1]

            self.buffer += cutoff
            self.flush_buffer()

            b = e + 1
            e = chunk.find('\n', b)

        self.buffer = chunk[b:]

    def flush_buffer(self):
        if len(self.buffer) > 0:
            self.write_to_pipe(self.buffer)
            self.buffer = ""

    def write_to_pipe(self, text):
        self.pipe.output(text)

    def flush(self):
        self.flush_buffer()
        self.pipe.flush()

class ErrorPipeBuffer(OutputPipeBuffer):
    def write_to_pipe(self, text):
        self.pipe.error(text)

class AsyncStreamConsumer(threading.Thread):
    def __init__(self, stream, consumer):
        super().__init__(self)
        self.stream = stream
        self.consumer = consumer

    def run(self):
        while True:
            chunk = os.read(self.stream.fileno(), 2**15)
            if len(chunk) == 0:
                break
            self.consumer.next(chunk)
        self.consumer.flush()
        self.stream.close()

## OUTPUT PANEL ##

class OutputPanel:
    def __init__(self, window):
        self.window = window
        self.view = window.create_output_panel("exec")

        self.line_buffer_lock = threading.Lock()
        self.line_buffer = collections.deque()

    def reset(self):
        self.view.run_command('erase_view')
        self.line_buffer.clear()
        self.set_settings(
            line_numbers="False",
            gutter="False",
            scroll_past_end="False",
            result_base_dir="",
            result_file_regex="",
            result_line_regex="",
            syntax="Packages/Text/Plain text.tmLanguage"
        )

    def set_settings(self, syntax=None, **settings):
        for k, v in settings.items():
            if v:
                self.view.settings().set(k, v)

        if syntax:
            self.view.assign_syntax(syntax)

    def append_line(self, line):
        with self.line_buffer_lock:
            reinvalidate = len(self.line_buffer) == 0
            self.line_buffer.append(line)

        if reinvalidate:
            self.invalidate()

    def invalidate(self):
        sublime.set_timeout(self.paint, 0)

    def paint(self):
        with self.line_buffer_lock:
            if len(self.line_buffer) == 0:
                return
            characters = '\n'.join(self.line_buffer) + '\n'
            self.line_buffer.clear()

        self.view.run_command('append', {'characters': characters, 'force': True, 'scroll_to_end': True})

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

## EXECUTOR ##

class Executor:
    def __init__(self, window):
        self.window = window
        self.output_panel = OutputPanel(window)
        print("Created executor for #" + str(window.id()))

    def run(self, options, pipe=None):
        option = lambda x: self.get_option(x, options)

        shell_cmd = option("shell_cmd")
        cmd = option("shell_cmd")

        working_dir = self.get_option("working_dir", options, default=self.get_working_dir())
        options["result_base_dir"] = working_dir

        if shell_cmd and sys.platform == "win32":
            cmd = ["powershell.exe", "-Command", shell_cmd]
        elif shell_cmd:
            cmd = [os.environ["SHELL"], "-c", shell_cmd]

        print("Running " + shell_cmd if shell_cmd else " ".join(cmd))

        os.chdir(working_dir)
        self.proc = subprocess.Popen(cmd, startupinfo=_get_startupinfo(),
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL)

        # Prepare output panel

        self.output_panel.reset()
        output_settings = dict()
        self.copy_output_settings(options, output_settings)
        self.output_panel.set_settings(**output_settings)

        if not self.get_option('no_output', options):
            self.output_panel.show()

        # Start pipes

        final_pipe = OutputPanelPipe(self.output_panel)
        if pipe:
            pipe.attach(final_pipe)
        else:
            pipe = final_pipe

        AsyncStreamConsumer(self.proc.stdout, OutputPipeBuffer(pipe)).start()
        AsyncStreamConsumer(self.proc.stderr, ErrorPipeBuffer(pipe)).start()

    def copy_output_settings(self, options, output_settings):
        copy = lambda x, y: self.copy_output_setting(x, y, options, output_settings)

        direct_copies = ["syntax", "result_base_dir"]

        for o in direct_copies:
            copy(o, o)

        copy("file_regex", "result_file_regex")
        copy("line_regex", "result_line_regex")

    def copy_output_setting(self, src_name, dst_name, options, output_settings):
        value = self.get_option(src_name, options)
        if value:
            output_settings[dst_name] = value

    def get_option(self, name, options, expand=False, default=None):
        if not name in options:
            return default
        result = options[name]
        if expand:
            result = sublime.expand_variables(result, self.window.extract_variables())
        return result

    def get_working_dir(self):
        view = self.window.active_view()
        if (view and view.file_name()):
            return os.path.dirname(view.file_name())

## COMMANDS ##

class EraseViewCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.erase(edit, sublime.Region(0, self.view.size()))

class ChimneyCommand(sublime_plugin.WindowCommand):
    def __init__(self, window):
        super().__init__(window)
        _get_executor(window)

    def get_pipe(self, args):
        return None

    def run(self, **args):
        executor = _get_executor(self.window)
        executor.run(args, self.get_pipe(args))

## STARTUP ##

_executors = {}

def _get_executor(window):
    if not window and not hasattr(window, 'id'):
        raise ValueError("invalid Window object")

    wid = window.id()
    if not wid in _executors:
        _executors[wid] = Executor(window)

    return _executors[wid]

def _get_startupinfo():
    startupinfo = None
    if sys.platform == "win32":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    return startupinfo
