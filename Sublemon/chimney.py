import os
import re
import shlex
import signal
import subprocess
from collections import deque
from itertools import chain, dropwhile
from threading import Lock, Thread

import sublime
from sublime_plugin import WindowCommand

from . import RUNNING_ON_WINDOWS


class OutputPanel:
    DEFAULTS = {
        "gutter": False,
        "scroll_past_end": False,
        "word_wrap": True,
        "draw_indent_guides": False,
    }

    def __init__(self, window):
        self.window = window
        self.view = window.create_output_panel("exec")
        self.lock = Lock()
        self.empty = True

    def reset(self, syntax, **settings):
        for key, val in {**self.DEFAULTS, **settings}.items():
            if val is not None:
                self.view.settings().set(key, val)

        self.view.assign_syntax(syntax)

        self.empty = True

        self.window.create_output_panel("exec")
        self.window.run_command("show_panel", {"panel": "output.exec"})

    def append(self, lines):
        with self.lock:
            if not self.empty:
                lines = chain(("",), lines)
            else:
                lines = dropwhile("".__eq__, lines)

            text = "\n".join(lines)

            if self.empty and text:
                self.empty = False

        if text:
            self.view.run_command("append", {"characters": text})

    def finalize(self):
        self.view.find_all_results()


# pylint: disable=unused-argument
class ChimneyBuildListener:
    def on_startup(self, ctx):
        ctx.window.status_message("Build started")

    def on_output(self, line, ctx):
        return line

    def on_error(self, line, ctx):
        return line

    def on_complete(self, ctx):
        pass


class BuildError(Exception):
    def __init__(self, message):
        super().__init__(self)
        self.message = message


class Cmd:
    def __init__(self, options):
        self.args = deque()
        self.cmdline = ""
        self.shell = options.get("shell", False)

        if shell_cmd := options.get("shell_cmd"):
            self.shell = True
            self.cmdline = (
                shell_cmd if isinstance(shell_cmd, str) else " ".join(shell_cmd)
            )
        elif cmd := options.get("cmd"):
            self.args.extend(cmd)

    def split_args(self):
        if not self.args and self.cmdline:
            self.args = deque(shlex.split(self.cmdline))

    def append(self, *chunks):
        self.split_args()
        self.args.extend(chunks)

    def appendleft(self, *chunks):
        self.split_args()
        self.args.extendleft(reversed(chunks))

    def __str__(self):
        return shlex.join(self.args) if self.args else self.cmdline

    def __bool__(self):
        return bool(self.args or self.cmdline)


class Build:
    def __init__(self, options, window):
        self.options = options
        self.window = window

        self.listener = ChimneyBuildListener()
        self.cmd = Cmd(options)

        self.env = options.get("env", {})
        self.file_regex = options.get("file_regex", "")
        self.line_regex = options.get("line_regex", "")
        self.working_dir = options.get("working_dir")

        if not self.working_dir and self.active_file:
            self.working_dir = os.path.dirname(self.active_file)

        self._syntax = options.get("syntax", "Packages/Text/Plain text.tmLanguage")

    @staticmethod
    def cancel(message):
        raise BuildError(message)

    def opt(self, key, default=None, expand=True):
        value = self.options.get(key, default)

        if expand and isinstance(value, str):
            value = sublime.expand_variables(value, self.window.extract_variables())

        return value

    @property
    def syntax(self):
        if not self._syntax.endswith((".sublime-syntax", ".tmLanguage")):
            return f"Packages/Sublemon/syntaxes/{self._syntax}.sublime-syntax"

        return self._syntax

    @syntax.setter
    def syntax(self, value):
        self._syntax = value

    @property
    def active_file(self):
        return self.window.active_view().file_name()


BUILDS = {}
PANELS = {}


class ChimneyCommand(WindowCommand):
    @property
    def wid(self):
        return self.window.id()

    @property
    def active_build(self):
        return BUILDS.get(self.wid)

    @active_build.setter
    def active_build(self, value):
        BUILDS[self.wid] = value

    @property
    def panel(self):
        panel = PANELS.get(self.wid)
        if not panel:
            return PANELS.setdefault(self.wid, OutputPanel(self.window))
        return panel

    def setup(self, build):
        pass

    # pylint: disable=arguments-differ
    def run(self, kill=False, interactive=None, **options):
        if self.active_build:
            self.active_build.cancel()

        if kill:
            return

        build = Build(options, self.window)

        if interactive:
            prompt = "$ " + (interactive if isinstance(interactive, str) else "")

            def on_done(cmd):
                self.run_build_interactive(build, cmd)

            self.window.show_input_panel(prompt, "", on_done, None, None)
        else:
            self.run_build(build)

    def run_build_interactive(self, build, cmd):
        if cmd.startswith("@"):
            cmd = cmd[1:]
            if project_file := self.window.project_file_name():
                build.working_dir = os.path.dirname(project_file)

        cmd = cmd.replace("$$", f'"{build.active_file}"')
        cmd = cmd.replace("@@", f'"{build.working_dir}"')

        if build.cmd:
            build.cmd.append(*(shlex.split(cmd)))
        elif RUNNING_ON_WINDOWS:
            build.cmd = Cmd({"cmd": ("pwsh", "-NoProfile", "-Command", cmd)})
        else:
            build.cmd = Cmd({"shell_cmd": cmd})

        self.run_build(build)

    def run_build(self, build):
        try:
            self.setup(build)

            if not build.cmd:
                build.cancel("No command")
        except BuildError as err:
            self.window.status_message(err.message)
            return

        self.panel.reset(
            syntax=build.syntax,
            result_base_dir=build.working_dir,
            result_file_regex=build.file_regex,
            result_line_regex=build.line_regex,
        )

        self.active_build = start_build(build, self.window, self.panel)

        print("⭍ [{}] {}".format(self.active_build.process.pid, build.cmd))

    def __del__(self):
        BUILDS.pop(self.wid, None)
        PANELS.pop(self.wid, None)


class BufferedPipe:
    ESCAPE_CHARACTER = re.compile(r"\x1b.*?\[\d*m")

    def __init__(self, process_line, ctx):
        self.process_line = process_line
        self.ctx = ctx

        self.line_buffer = []

    def write(self, chunk):
        lines = []
        begin = 0

        while (end := chunk.find("\n", begin)) != -1:
            self.bufferize(chunk, begin, end)
            lines.append(self.get_buffered_line())

            begin = end + 1

        if begin < len(chunk):
            self.bufferize(chunk, begin, len(chunk))

        lines = (self.process_line(line, self.ctx) for line in lines)

        self.ctx.print_lines(filter(None.__ne__, lines))

    def bufferize(self, chunk, begin, end):
        while end > 0 and chunk[end - 1] == "\r":
            end -= 1

        line = self.ESCAPE_CHARACTER.sub("", chunk[begin:end])
        self.line_buffer.append(line)

    def get_buffered_line(self):
        content = "".join(self.line_buffer)
        self.line_buffer.clear()
        return content

    def flush(self):
        if self.line_buffer:
            line = self.process_line(self.get_buffered_line())
            if line:
                self.ctx.print_lines((line,))


def read_to_pipe(stream, pipe, on_close=None):
    fileno = stream.fileno()

    while chunk := os.read(fileno, 2 ** 16):
        pipe.write(chunk.decode("utf-8"))

    pipe.flush()
    stream.close()

    if on_close:
        on_close()


class BuildContext:
    def __init__(self, window, panel, process, build):
        self.window = window
        self.panel = panel
        self.process = process
        self.cancelled = False

        self.working_dir = build.working_dir
        self.on_complete = build.listener.on_complete
        self.on_complete_message = "Build finished"

        build.listener.on_startup(self)

    def print_lines(self, lines):
        self.panel.append(lines)

    def complete(self):
        if not self.cancelled:
            self.on_complete(self)
            self.panel.finalize()
            self.window.status_message(self.on_complete_message)
        else:
            self.window.status_message("Build cancelled")
            self.print_lines(("", "[Process Terminated]"))

        print("{} [{}]".format("✘" if self.cancelled else "✔", self.process.pid))

        self.process = None

    def cancel(self):
        self.cancelled = True
        self.window.status_message("Cancelling build...")
        kill_process(self.process)

    def __bool__(self):
        """True if process is active."""
        return bool(self.process and not self.process.poll())


def start_build(build, window, panel):
    process = start_process(build.cmd, build.env, build.working_dir)
    listener = build.listener

    ctx = BuildContext(window, panel, process, build)

    stdout_args = (process.stdout, BufferedPipe(listener.on_output, ctx), ctx.complete)
    stderr_args = (process.stderr, BufferedPipe(listener.on_error, ctx))

    Thread(target=read_to_pipe, args=stdout_args).start()
    Thread(target=read_to_pipe, args=stderr_args).start()

    return ctx


def start_process(cmd, env, cwd):
    process_params = {
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "stdin": subprocess.DEVNULL,
        "shell": cmd.shell,
    }

    if RUNNING_ON_WINDOWS:
        process_params["startupinfo"] = startupinfo()
    else:
        process_params["preexec_fn"] = os.setsid  # pylint: disable=no-member

    if cwd:
        process_params["cwd"] = cwd

    if env:
        os_env = os.environ.copy()
        process_params["env"] = os_env

        for key, val in env.items():
            if val is None:
                os_env.pop(key, None)
            else:
                os_env[key] = os.path.expandvars(val)

    args = cmd.args if not cmd.shell else str(cmd)

    return subprocess.Popen(args, **process_params)


def kill_process(process):
    if RUNNING_ON_WINDOWS:
        cmd = f"taskkill /T /F /PID {process.pid}"
        subprocess.Popen(cmd, startupinfo=startupinfo())
    else:
        try:
            os.killpg(process.pid, signal.SIGTERM)  # pylint: disable=no-member
            process.terminate()
        except ProcessLookupError:
            print(f"[WARN] Process {process.pid} doesn't exist")

    process.wait()


def startupinfo():
    sinfo = subprocess.STARTUPINFO()
    sinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    return sinfo
