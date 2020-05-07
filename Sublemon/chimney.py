import copy
import os
import shlex
import signal
import subprocess
from collections import deque
from threading import Lock, Thread

import sublime
from sublime_plugin import WindowCommand

from . import RUNNING_ON_WINDOWS


class OutputPanel:
    def __init__(self, window):
        self.window = window
        self.view = window.create_output_panel('exec')

        self.line_buffer_lock = Lock()
        self.line_buffer = deque()

        self.lines_printed = 0

    def reset(self, syntax, **settings):
        view_settings = self.view.settings()

        view_settings.set('gutter', False)
        view_settings.set('scroll_past_end', False)
        view_settings.set('word_wrap', True)
        view_settings.set('draw_indent_guides', False)

        for key, val in settings.items():
            if val:
                view_settings.set(key, val)

        if syntax:
            self.view.assign_syntax(syntax)

        self.window.create_output_panel('exec')
        self.lines_printed = 0

        self.window.run_command('show_panel', {'panel': 'output.exec'})

    def append(self, line):
        with self.line_buffer_lock:
            invalidate = len(self.line_buffer) == 0
            self.line_buffer.append(line)

        if invalidate:
            sublime.set_timeout(self.paint, 0)

    def paint(self):
        with self.line_buffer_lock:
            if not self.line_buffer:
                return
            lines = copy.copy(self.line_buffer)
            self.line_buffer.clear()

        if self.lines_printed > 0:
            lines.appendleft('')

        self.lines_printed += len(lines)
        self.view.run_command(
            'append',
            {'characters': '\n'.join(lines), 'force': True, 'scroll_to_end': True})


# pylint: disable=no-self-use
class ChimneyBuildListener:
    def on_startup(self, ctx):
        ctx.window.status_message('Build started')

    def on_output(self, line, ctx):
        ctx.print(line)

    def on_error(self, line, ctx):
        ctx.print(line)

    def on_complete(self, ctx):
        ctx.window.status_message('Build finished')


class BuildError(Exception):
    def __init__(self, message):
        super().__init__(self)
        self.message = message


class Cmd:
    def __init__(self, options):
        cmd = options.get("shell_cmd") or options.get("cmd", [])
        if isinstance(cmd, str):
            cmd = shlex.split(cmd)
        self.args = deque(cmd)
        self.shell = 'shell_cmd' in options or options.get('shell', False)

    def append(self, *chunks):
        self.args.extend(chunks)

    def appendleft(self, *chunks):
        self.args.extendleft(reversed(chunks))

    def __str__(self):
        return ' '.join(map(shlex.quote, self.args))

    def __bool__(self):
        return bool(self.args)


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

        self._syntax = options.get("syntax",
                                   "Packages/Text/Plain text.tmLanguage")

    @staticmethod
    def cancel(message):
        raise BuildError(message)

    def opt(self, key, default=None, expand=True):
        value = self.options.get(key, default)

        if expand:
            value = sublime.expand_variables(value, self.window.extract_variables())

        return value

    @property
    def syntax(self):
        return self._syntax

    @syntax.setter
    def syntax(self, value):
        if not value.endswith(('.sublime-syntax', '.tmLanguage')):
            value = f"Packages/Sublemon/syntaxes/{value}.sublime-syntax"

        self._syntax = value

    @property
    def active_file(self):
        return self.window.active_view().file_name()


class ChimneyCommand(WindowCommand):
    builds = {}
    panels = {}

    @property
    def wid(self):
        return self.window.id()

    @property
    def active_build(self):
        return self.builds.get(self.wid)

    @active_build.setter
    def active_build(self, value):
        self.builds[self.wid] = value

    @property
    def panel(self):
        return self.panels.get(self.wid) or \
            self.panels.setdefault(self.wid, OutputPanel(self.window))

    def setup(self, build):
        pass

    def run(self, kill=False, interactive=None, **options):  # pylint: disable=arguments-differ
        if self.active_build:
            self.active_build.cancel()

        if kill:
            return

        build = Build(options, self.window)

        if interactive:
            self.window.show_input_panel(
                f"$ {interactive}", "",
                lambda cmd: self.run_build_custom_command(build, cmd),
                None, None)
        else:
            self.run_build(build)

    def run_build_custom_command(self, build, cmd):
        variables = self.window.extract_variables()
        cmd = (sublime.expand_variables(arg, variables) for arg in shlex.split(cmd))

        build.cmd.append(*cmd)
        build.cmd.shell = True

        self.run_build(build)

    def run_build(self, build):
        try:
            self.setup(build)

            if not build.cmd:
                build.cancel('No command')
        except BuildError as err:
            self.window.status_message(err.message)
            return

        self.panel.reset(
            result_base_dir=build.working_dir,
            result_file_regex=build.file_regex,
            result_line_regex=build.line_regex,
            syntax=build.syntax
        )

        self.active_build = start_build(build, self.panel)

        print('⌛ [{}] {}'.format(self.active_build.process.pid, build.cmd))

    def __del__(self):
        self.builds.pop(self.wid, None)
        self.panels.pop(self.wid, None)


class OutputBuffer:
    def __init__(self, output):
        self.buffer = deque()
        self.output = output

    def write(self, chunk):
        chunk = chunk.decode('utf-8')

        bgn = 0
        end = chunk.find('\n')

        while end != -1:
            self.append(chunk, bgn, end)
            self.flush()

            bgn = end + 1
            end = chunk.find('\n', bgn)

        end = len(chunk)
        if bgn < end:
            self.append(chunk, bgn, end)

    def append(self, chunk, bgn, end):
        while end > 0 and chunk[end-1] == '\r':
            end = end - 1

        self.buffer.append(chunk[bgn:end])

    def flush(self):
        if self.buffer:
            self.output(''.join(self.buffer))
            self.buffer.clear()


class AsyncStreamConsumer(Thread):
    def __init__(self, stream, output_buffer, on_close=None):
        super().__init__()
        self.stream = stream
        self.output_buffer = output_buffer
        self.on_close = on_close

    def run(self):
        fileno = self.stream.fileno()
        while True:
            chunk = os.read(fileno, 2**16)
            if not chunk:
                break
            self.output_buffer.write(chunk)

        self.output_buffer.flush()
        self.stream.close()

        if self.on_close:
            self.on_close()


class ActiveBuildContext:
    def __init__(self, panel, process, listener):
        self.panel = panel
        self.process = process
        self.listener = listener
        self.window = panel.window

        self.cancelled = False

        self.listener.on_startup(self)

    def print(self, line):
        self.panel.append(line)

    def complete(self):
        if not self.cancelled:
            self.panel.view.find_all_results()
            self.listener.on_complete(self)
        else:
            self.window.status_message('Build cancelled')
            self.print('\n[Process Terminated]')

        print('{} [{}]'.format('✘' if self.cancelled else '✔',
                               self.process.pid))

        self.process = None

    def cancel(self):
        self.cancelled = True
        self.window.status_message('Cancelling build...')
        kill_process(self.process)

    def __bool__(self):
        '''True if process is active.'''
        return bool(self.process and not self.process.poll())


def start_build(build, panel):
    listener = build.listener

    if build.working_dir:
        os.chdir(build.working_dir)

    process = start_process(build.cmd, build.env)
    ctx = ActiveBuildContext(panel, process, listener)

    output_buffer = OutputBuffer(lambda line: listener.on_output(line, ctx))
    error_buffer = OutputBuffer(lambda line: listener.on_error(line, ctx))

    AsyncStreamConsumer(process.stdout, output_buffer,
                        on_close=ctx.complete).start()
    AsyncStreamConsumer(process.stderr, error_buffer).start()

    return ctx


def start_process(cmd, env):
    process_params = {
        'stdout': subprocess.PIPE,
        'stderr': subprocess.PIPE,
        'stdin': subprocess.DEVNULL,
        'shell': cmd.shell
    }

    if RUNNING_ON_WINDOWS:
        process_params['startupinfo'] = startupinfo()
    else:
        process_params['preexec_fn'] = os.setsid  # pylint: disable=no-member

    if env:
        os_env = os.environ.copy()
        os_env.update({k: os.path.expandvars(v) for k, v in env.items()})
        process_params['env'] = os_env

    return subprocess.Popen(cmd.args, **process_params)


def kill_process(process):
    if RUNNING_ON_WINDOWS:
        cmd = 'taskkill /T /F /PID {}'.format(process.pid)
        subprocess.Popen(cmd, startupinfo=startupinfo())
    else:
        os.killpg(process.pid, signal.SIGTERM)  # pylint: disable=no-member
        process.terminate()

    process.wait()


def startupinfo():
    sinfo = subprocess.STARTUPINFO()
    sinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    return sinfo
