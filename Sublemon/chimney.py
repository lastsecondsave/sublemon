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

from . import RUNNING_ON_WINDOWS, listify, sad_message
from .opener import find_project_folder


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
        ctx.window.status_message(f"Running {ctx.cmd.preview} …")

    def on_output(self, line, ctx):
        return line

    def on_error(self, line, ctx):
        return line

    def on_complete(self, ctx):
        pass


class BuildSetupError(Exception):
    def __init__(self, message):
        super().__init__(self)
        self.message = message


class Cmd:
    PREVIEW = re.compile(r"\S+( [^-/][\w-]+)?(?=\s|$)")

    def __init__(self, cmd=None, variables=None, **options):
        self.args = deque()
        self.cmdline = None
        self.shell = options.get("shell", False)

        if shell_cmd := options.get("shell_cmd"):
            self.shell = True
            self.cmdline = (
                shell_cmd if isinstance(shell_cmd, str) else " ".join(shell_cmd)
            )

            if base := options.get("shell_cmd_base"):
                base = sublime.expand_variables(base, variables or {})
                self.cmdline = f"{base} {self.cmdline}"

        elif cmd:
            self.args.extend(listify(cmd))

        self._preview = options.get("cmd_preview")
        if self._preview and variables:
            self._preview = sublime.expand_variables(self._preview, variables)

    def verify_editable(self):
        if self.cmdline:
            raise ValueError("Cmd with cmdline is not editable")

    def append(self, *args):
        self.verify_editable()
        self.args.extend(args)

    def appendleft(self, *args):
        self.verify_editable()
        self.args.extendleft(reversed(args))

    @property
    def preview(self):
        if self._preview:
            return self._preview

        return Cmd.PREVIEW.match(str(self)).group(0)

    @preview.setter
    def preview(self, value):
        self._preview = value

    def __str__(self):
        if self.cmdline:
            return self.cmdline
        if RUNNING_ON_WINDOWS:
            return subprocess.list2cmdline(self.args)
        return shlex.join(self.args)

    def __bool__(self):
        return bool(self.args or self.cmdline)


class BuildSetup:
    def __init__(self, options, window):
        self.options = options
        self.window = window

        self.listener = ChimneyBuildListener()
        self.initializer = None
        self.cmd = Cmd(variables=window.extract_variables(), **options)

        self.env = options.get("env", {})
        self.file_regex = options.get("file_regex", "")
        self.line_regex = options.get("line_regex", "")
        self.active_file = window.active_view().file_name()
        self.working_dir = options.get("working_dir")

        if not self.working_dir and self.active_file:
            self.working_dir = os.path.dirname(self.active_file)

        self.syntax = options.get("syntax", "Packages/Text/Plain text.tmLanguage")

    def cancel(self, message):
        raise BuildSetupError(message)

    def opt(self, key, default=None, expand=True, required=False):
        value = self.options.get(key, default)

        if required and not value:
            self.cancel(f"'{key}' is not set")

        if expand and isinstance(value, str):
            value = sublime.expand_variables(value, self.window.extract_variables())

        return value

    @property
    def syntax(self):
        return self._syntax

    @syntax.setter
    def syntax(self, value):
        if not value.endswith((".sublime-syntax", ".tmLanguage")):
            value = f"Packages/Sublemon/syntaxes/{value}.sublime-syntax"

        self._syntax = value


class ChimneyCommand(WindowCommand):
    BUILDS = {}
    PANELS = {}

    last_command = ""

    @property
    def wid(self):
        return self.window.id()

    @property
    def active_build(self):
        return ChimneyCommand.BUILDS.get(self.wid)

    @active_build.setter
    def active_build(self, value):
        ChimneyCommand.BUILDS[self.wid] = value

    @property
    def panel(self):
        panel = ChimneyCommand.PANELS.get(self.wid)
        if not panel:
            return ChimneyCommand.PANELS.setdefault(self.wid, OutputPanel(self.window))
        return panel

    def setup(self, build):
        pass

    # pylint: disable=arguments-differ
    def run(self, kill=False, interactive=None, **options):
        if self.active_build:
            self.active_build.cancel()

        if kill:
            return

        build = BuildSetup(options, self.window)

        if not interactive:
            self.run_build(build)
            return

        prompt = "$ " + (interactive if isinstance(interactive, str) else "")

        def on_done(cmd):
            if cmd:
                self.last_command = cmd
                self.set_cmd(build, cmd)

            self.run_build(build)

        input_view = self.window.show_input_panel(
            prompt, self.last_command, on_done, None, None
        )

        input_view.sel().add(sublime.Region(0, len(self.last_command)))

    def set_cmd(self, build, cmd):
        if cmd.startswith("@"):
            cmd = cmd[1:]
            if project_folder := find_project_folder(self.window):
                build.working_dir = str(project_folder)

        cmd = cmd.replace("$$", f'"{build.active_file}"')
        cmd = cmd.replace("@@", f'"{build.working_dir}"')

        if build.cmd:
            build.cmd.append(*(shlex.split(cmd, posix=(not RUNNING_ON_WINDOWS))))
        elif RUNNING_ON_WINDOWS:
            build.cmd = Cmd(["pwsh", "-NoProfile", "-Command", cmd])
        else:
            build.cmd = Cmd(shell_cmd=cmd)

    def run_build(self, build):
        try:
            self.setup(build)
        except BuildSetupError as err:
            self.window.status_message(err.message)
            return

        if not build.cmd:
            self.window.status_message("No command")
            return

        if not build.initializer:
            self.start_build(build)
            return

        def init_and_start():
            build.initializer(build)
            self.start_build(build)

        sublime.set_timeout_async(init_and_start, 0)

    def start_build(self, build):
        self.panel.reset(
            syntax=build.syntax,
            result_base_dir=build.working_dir,
            result_file_regex=build.file_regex,
            result_line_regex=build.line_regex,
        )

        self.active_build = start_build(build, self.window, self.panel)

        marker = "⭭" if build.cmd.shell else "⭍"
        print(f"{marker} [{self.active_build.process.pid}] {build.cmd}")

    def __del__(self):
        ChimneyCommand.BUILDS.pop(self.wid, None)
        ChimneyCommand.PANELS.pop(self.wid, None)


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
            if line := self.process_line(self.get_buffered_line(), self.ctx):
                lines.append(line)

            begin = end + 1

        if begin < len(chunk):
            self.bufferize(chunk, begin, len(chunk))

        self.ctx.print_lines(lines)

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
            if line := self.process_line(self.get_buffered_line(), self.ctx):
                self.ctx.print_lines([line])


def read_to_pipe(stream, pipe, on_close=None):
    fileno = stream.fileno()

    while chunk := os.read(fileno, 2**16):
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
        self.cmd = build.cmd

        self.on_complete = build.listener.on_complete
        self.on_complete_message = f"Complete: {build.cmd.preview}"

        build.listener.on_startup(self)

    def print_lines(self, lines):
        self.panel.append(lines)

    def print_line(self, line):
        self.panel.append((line,))

    def complete(self):
        if not self.cancelled:
            self.on_complete(self)

            returncode = self.process.wait()

            if not self.panel.empty:
                self.panel.finalize()
            elif returncode:
                self.print_line(f"Exited with {returncode}")
            else:
                self.print_line("OK")

            self.window.status_message(self.on_complete_message)
            print(f"✔ [{self.process.pid}] {returncode}")
        else:
            self.window.status_message("Build cancelled")
            self.print_lines(("", "*** Terminated ***"))
            print(f"✘ [{self.process.pid}]")

        self.process = None

    def cancel(self):
        self.cancelled = True
        self.window.status_message("Cancelling build...")
        kill_process(self.process)

    def __bool__(self):
        return bool(self.process and not self.process.poll())


def start_build(build, window, panel):
    process = start_process(build.cmd, build.env, build.working_dir)
    ctx = BuildContext(window, panel, process, build)

    Thread(
        target=read_to_pipe,
        args=(
            process.stdout,
            BufferedPipe(build.listener.on_output, ctx),
            ctx.complete,
        ),
    ).start()

    Thread(
        target=read_to_pipe,
        args=(
            process.stderr,
            BufferedPipe(build.listener.on_error, ctx),
        ),
    ).start()

    return ctx


def start_process(cmd, env, cwd):
    process_params = {
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "stdin": subprocess.DEVNULL,
        "shell": cmd.shell,
    }

    if RUNNING_ON_WINDOWS:
        process_params["creationflags"] = subprocess.CREATE_NO_WINDOW
    else:
        process_params["start_new_session"] = True

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

    args = cmd.args or cmd.cmdline

    try:
        # pylint: disable=consider-using-with
        return subprocess.Popen(args, **process_params)
    except:
        sad_message(f"Failed to run program: {cmd}")
        raise


def kill_process(process):
    if RUNNING_ON_WINDOWS:
        cmd = f"taskkill /T /F /PID {process.pid}"
        # pylint: disable=consider-using-with
        subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        try:
            os.killpg(process.pid, signal.SIGTERM)  # pylint: disable=no-member
            process.terminate()
        except ProcessLookupError:
            sad_message(f"Process {process.pid} doesn't exist")

    process.wait()
