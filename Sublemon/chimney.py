import collections
import os
import sublime
import sublime_plugin
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
            self.flush_buffer(True)

            b = e + 1
            e = chunk.find('\n', b)

        self.buffer += chunk[b:]

    def flush_buffer(self, force=False):
        if len(self.buffer) > 0 or force:
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
    def __init__(self, stream, consumer, on_close=None):
        super().__init__(self)
        self.stream = stream
        self.consumer = consumer
        self.on_close = on_close

    def run(self):
        while True:
            chunk = os.read(self.stream.fileno(), 2**15)
            if len(chunk) == 0:
                break
            self.consumer.next(chunk)

        self.consumer.flush()
        self.stream.close()

        if self.on_close:
            self.on_close()

## OUTPUT PANEL ##

class OutputPanel:
    def __init__(self, window):
        self.window = window
        self.view = window.create_output_panel("exec")

        self.line_buffer_lock = threading.Lock()
        self.line_buffer = collections.deque()

        self.set_settings(gutter="False", scroll_past_end="False")

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

        self.view.run_command('append', dict(
            characters = characters,
            force = True,
            scroll_to_end = self.scroll_to_end
        ))

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

## EXECUTOR ##

class Options:
    def __init__(self, options_dict):
        self.original_dict = options_dict

        option = lambda x, y=None: options_dict.get(x, y)

        self.cmd           = option("cmd")
        self.file_regex    = option("file_regex", "")
        self.kill          = option("kill", False)
        self.line_regex    = option("line_regex", "")
        self.shell_cmd     = option("shell_cmd")
        self.syntax        = option("syntax", "Packages/Text/Plain text.tmLanguage")
        self.working_dir   = option("working_dir")
        self.show_output   = option("show_output", "text").lower()
        self.scroll_to_end = option("scroll_to_end", True)

    def get(self, arg, default=None):
        return self.original_dict.get(arg, default)

    def __getitem__(self, arg):
        return self.get(arg)

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

        # Start pipes

        final_pipe = OutputPanelPipe(self.output_panel)
        if pipe:
            pipe.attach(final_pipe)
        else:
            pipe = final_pipe

        AsyncStreamConsumer(proc.stdout, OutputBuffer(pipe), on_close=self.finish).start()
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
            base_path = self.window.extract_variables().get("project_path")
            opt.working_dir = os.path.join(base_path, opt.working_dir)


    def start_process(self, opt):
        if opt.shell_cmd and sys.platform == "win32":
            opt.cmd = ["powershell.exe", "-Command", opt.shell_cmd]
            message = "[ps:{}] " + opt.shell_cmd
        elif opt.shell_cmd:
            opt.cmd = [os.environ["SHELL"], "-c", opt.shell_cmd]
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
        _log("Killing {}", pid)

        if sys.platform == "win32":
            cmd = ["taskkill", "/PID", pid]
            subprocess.Popen(cmd, startupinfo=_get_startupinfo())
            return

        subprocess.Popen(["kill",  pid])
        if self.running_state.options.shell_cmd != None:
            subprocess.Popen(["pkill", "-P", pid])

    def mark_process_terminated(self):
        proc = self.running_state.proc
        proc.poll()
        _log("Terminated [{}], exit code: {}", proc.pid, proc.returncode)

## COMMANDS ##

class EraseViewCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.erase(edit, sublime.Region(0, self.view.size()))

class ChimneyCommand(sublime_plugin.WindowCommand):
    def __init__(self, window):
        super().__init__(window)
        _get_executor(window)

    def section(self):
        pass

    def create_pipe(self, options, variables):
        pass

    def preprocess_options(self, options, variables):
        pass

    def run(self, **args):
        options = self.create_options(args)
        variables = self.window.extract_variables()

        self.preprocess_options(options, variables)
        pipe = self.create_pipe(options, variables)

        _get_executor(self.window).run(options, pipe, self.on_complete)

    def create_options(self, args):
        options = args.copy()
        options_override = self.window.project_data()

        if not options_override:
            return Options(options)

        options_override = options_override.get("configuration", dict())
        options_override = options_override.get("chimney", None)

        if not options_override:
            return Options(options)

        if self.section() in options_override:
            options.append(options_override[self.section()])

        if "show_output" in options_override:
            options["show_output"] = options_override["show_output"]

        options = Options(options)

    def on_complete(self, errors_count):
        message = "Build finished"
        if errors_count > 0:
            message += " with {} error{}".format(errors_count, "s" if errors_count > 1 else "")

        sublime.status_message(message)

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
