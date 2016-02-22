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
        while hasattr(link_point, "next_pipe"):
            link_point = link_point.next_pipe
        link_point.next_pipe = next_pipe

class OutputBuffer:
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

        self.buffer += chunk[b:]

    def flush_buffer(self):
        if len(self.buffer) > 0:
            self.write_to_pipe(self.buffer)
            self.buffer = ""

    def write_to_pipe(self, text):
        self.pipe.output(text)

    def flush(self):
        self.flush_buffer()
        self.pipe.flush()

class ErrorBuffer(OutputBuffer):
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
        self.on_close()

    def on_close(self):
        pass

## OUTPUT PANEL ##

class OutputPanel:
    def __init__(self, window):
        self.window = window
        self.view = window.create_output_panel("exec")

        self.line_buffer_lock = threading.Lock()
        self.line_buffer = collections.deque()

        self.set_settings(gutter="False", scroll_past_end="False")
        self.autoshow = False

    def reset(self):
        self.view.run_command('erase_view')
        self.line_buffer.clear()

    def set_settings(self, syntax=None, **settings):
        for k, v in settings.items():
            if v:
                self.view.settings().set(k, v)

        if syntax:
            self.view.assign_syntax(syntax)

        self.window.create_output_panel("exec")

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
        if self.autoshow and self.window.active_panel() != "exec":
            self.show()

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

class Options:
    def __init__(self, options_dict):
        self.original_dict = options_dict

        option = lambda x, y=None: options_dict.get(x, y)

        self.cmd         = option("cmd")
        self.file_regex  = option("file_regex", "")
        self.kill        = option("kill", False)
        self.line_regex  = option("line_regex", "")
        self.show_output = option("show_output", "text").lower()
        self.shell_cmd   = option("shell_cmd")
        self.syntax      = option("syntax", "Packages/Text/Plain text.tmLanguage")
        self.working_dir = option("working_dir")

    def __getitem__(self, arg):
        return self.original_dict.get(arg, None)

class State:
    pass

class Executor:
    def __init__(self, window):
        self.window = window
        self.output_panel = OutputPanel(window)
        self.running_state = None
        _log("Created executor for #{}", window.id())

    def run(self, options, pipe, on_complete):
        if self.running_state:
            self.kill_process()

        if options.kill:
            return

        self.set_working_dir(options)
        proc = self.start_process(options)
        sublime.status_message("Build started")

        # Prepare output panel

        self.output_panel.reset()
        self.output_panel.set_settings(**self.map_output_panel_settings(options))

        if options.show_output == "always":
            self.output_panel.show()

        self.output_panel.autoshow = options.show_output == "text";

        # Start pipes

        final_pipe = OutputPanelPipe(self.output_panel)
        if pipe:
            pipe.attach(final_pipe)
        else:
            pipe = final_pipe

        output_consumer = AsyncStreamConsumer(proc.stdout, OutputBuffer(pipe))
        output_consumer.on_close = self.finish;
        output_consumer.start()

        AsyncStreamConsumer(proc.stderr, ErrorBuffer(pipe)).start()

        self.running_state = State()
        self.running_state.proc = proc
        self.running_state.on_complete = on_complete
        self.running_state.options = options

    def set_working_dir(self, opt):
        if not opt.working_dir:
            view = self.window.active_view()
            if (view and view.file_name()):
                opt.working_dir = os.path.dirname(view.file_name())
            return

        if not os.path.isabs(opt.working_dir):
            base_path = _var(self.window, "project_path")
            opt.working_dir = os.path.join(base_path, opt.working_dir)


    def start_process(self, opt):
        if opt.shell_cmd and sys.platform == "win32":
            opt.cmd = ["powershell.exe", "-Command", opt.shell_cmd]
            message = "[ps:{}] " + opt.shell_cmd
        elif opt.shell_cmd:
            opt.cmd = [os.environ["SHELL"], "-i", "-c", opt.shell_cmd]
            message = "[sh:{}] " + opt.shell_cmd
        else:
            message = "[{}] " + " ".join(opt.cmd)

        os.chdir(opt.working_dir)
        proc = subprocess.Popen(opt.cmd, startupinfo=_get_startupinfo(),
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.DEVNULL)

        _log("Running " + message, proc.pid)
        return proc

    def finish(self):
        errors_count = len(self.output_panel.view.find_all_results())
        self.running_state.on_complete(errors_count)

        if self.running_state.options.show_output == "error" and errors_count > 0:
            self.output_panel.show()

        self.mark_process_terminated()
        self.running_state = None

    def kill_process(self):
        pid = str(self.running_state.proc.pid)

        if sys.platform == "win32":
            cmd = ["taskkill", "/PID", pid]
        elif self.running_state.options.shell_cmd != None:
            cmd = ["pkill", "-P", pid]
        else:
            cmd = ["kill", pid]

        _log("Killing {}", pid)
        subprocess.Popen(cmd, startupinfo=_get_startupinfo())

    def mark_process_terminated(self):
        proc = self.running_state.proc
        proc.poll()
        _log("Terminated [{}], exit code: {}", proc.pid, proc.returncode)

    def map_output_panel_settings(self, options):
        return dict(
            result_base_dir = options.working_dir,
            result_file_regex = options.file_regex,
            result_line_regex = options.line_regex,
            syntax = options.syntax
        )

## COMMANDS ##

class EraseViewCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.erase(edit, sublime.Region(0, self.view.size()))

class ChimneyCommand(sublime_plugin.WindowCommand):
    def __init__(self, window):
        super().__init__(window)
        _get_executor(window)

    def run(self, **args):
        options = Options(args)
        self.preprocess_options(options)
        pipe=self.get_pipe(options)
        _get_executor(self.window).run(options, pipe, self.finish)

    def get_pipe(self, options):
        pass

    def preprocess_options(self, options):
        pass

    def finish(self, errors_count):
        message = "Build finished"
        if errors_count > 0:
            message += " with {} error{}".format(errors_count, "s" if errors_count > 1 else "")

        sublime.status_message(message)

    def var(self, name) :
        return _var(self.window, name)

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

def _log(message, *params):
    print("Chimney: " + message.format(*params))

def _var(window, name, default=None):
    return window.extract_variables().get(name, default)
