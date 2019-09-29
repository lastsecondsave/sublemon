import copy
import os
import shlex
import signal
import subprocess

from collections import deque
from threading import Lock, Thread

import sublime
from sublime_plugin import WindowCommand

from .utils import RUNNING_ON_WINDOWS


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

    def show(self):
        self.window.run_command('show_panel', {'panel': 'output.exec'})


# pylint: disable=no-self-use
class ChimneyBuildListener:
    def on_startup(self, ctx):
        ctx.window.status_message('Build started: ' + ' '.join(map(shlex.quote, ctx.process.args)))

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


def split_command(cmd):
    return shlex.split(cmd) if isinstance(cmd, str) else cmd


class BuildCommand:
    def __init__(self, options):
        cmd = options.get('cmd', None) or options.get('shell_cmd', [])
        self.cmd = deque(split_command(cmd))

    def append(self, *chunks):
        self.cmd.extend(chunks)

    def appendleft(self, *chunks):
        self.cmd.extendleft(reversed(chunks))

    def __str__(self):
        return ' '.join(map(shlex.quote, self.cmd))

    def __bool__(self):
        return bool(self.cmd)


class BuildSetup:
    def __init__(self, options, window):
        self.options = options
        self.window = window
        self.listener = ChimneyBuildListener()

        self.env = options.get('env', {})
        self.cmd = BuildCommand(options)

    @staticmethod
    def cancel_build(message=None):
        raise BuildError(message)

    def opt(self, name):
        return self.options.get(name, None)

    def opt_list(self, name):
        return split_command(self.opt(name))

    def file_name(self):
        return self.window.active_view().file_name()

    # pylint: disable=too-many-arguments
    def set(self,
            working_dir=None,
            syntax=None,
            file_regex=None,
            line_regex=None,
            listener=None):

        self.listener = listener or self.listener

        self.set_option('file_regex', file_regex, '')
        self.set_option('line_regex', line_regex, '')
        self.set_option('working_dir', working_dir)

        if syntax and not syntax.endswith(('.sublime-syntax', '.tmLanguage')):
            syntax = 'Packages/Sublemon/syntaxes/{}.sublime-syntax'.format(syntax)
        self.set_option('syntax', syntax, 'Packages/Text/Plain text.tmLanguage')

    def set_option(self, option, value, default=None):
        value = value or self.options.get(option, default)
        if value is not None:
            self.options[option] = value


def log(message, *params):
    print(message.format(*params))


class ChimneyBuildContainer():
    builds = {}
    panels = {}

    def panel(self, window):
        if not window.id() in self.panels:
            self.panels[window.id()] = OutputPanel(window)

        return self.panels[window.id()]

    def build(self, window):
        return self.builds.get(window.id(), None)

    def set_build(self, window, build):
        self.builds[window.id()] = build


class ChimneyCancelCommand(WindowCommand, ChimneyBuildContainer):
    def run(self, **_options):
        build = self.build(self.window)
        if build:
            build.cancel()


class ChimneyCommand(WindowCommand, ChimneyBuildContainer):
    def setup(self, ctx):
        pass

    def run(self, kill=False, **options):
        build = self.build(self.window)
        if build:
            build.cancel()

        if kill:
            return

        setup = BuildSetup(options, self.window)

        try:
            self.setup(setup)

            if not setup.cmd:
                setup.cancel_build('No command')
        except BuildError as err:
            self.window.status_message(': '.join(filter(None, ('Build error', err.message))))
            return

        panel = self.panel(self.window)

        panel.reset(
            result_base_dir=self.change_working_dir(options.get('working_dir')),
            result_file_regex=options.get('file_regex'),
            result_line_regex=options.get('line_regex'),
            syntax=options.get('syntax')
        )

        panel.show()

        build = start_build(panel, setup.cmd.cmd, setup.env, setup.listener)
        self.set_build(self.window, build)

        log('→ [{}] {}', build.process.pid, setup.cmd)

    def change_working_dir(self, working_dir):
        if not working_dir:
            view = self.window.active_view()
            if view and view.file_name():
                working_dir = os.path.dirname(view.file_name())

        if working_dir:
            os.chdir(working_dir)

        return working_dir


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


class RunningBuildContext:
    def __init__(self, panel, process, listener):
        self.panel = panel
        self.process = process
        self.listener = listener
        self.window = panel.window

        self.cancelled = None

        self.listener.on_startup(self)

    def print(self, line):
        self.panel.append(line)

    def complete(self):
        if not self.cancelled:
            self.listener.on_complete(self)
            self.panel.view.find_all_results()
            log('✔ [{}]', self.process.pid)
        else:
            log('✘ [{}]', self.process.pid)

        if self.cancelled == 'kill':
            self.window.status_message('Build cancelled')
            self.print('\n[Process Terminated]')

        self.process = None

    def cancel(self, kill=True):
        self.cancelled = 'kill' if kill else 'restart'
        self.window.status_message('Cancelling build...')
        kill_process(self.process)

    def __bool__(self):
        '''True if process is active.'''
        return bool(self.process and not self.process.poll())


def start_build(panel, cmd, env, listener):
    process = start_process(cmd, env)
    ctx = RunningBuildContext(panel, process, listener)

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
        'stdin': subprocess.DEVNULL
    }

    if RUNNING_ON_WINDOWS:
        process_params['startupinfo'] = startupinfo()
    else:
        process_params['preexec_fn'] = os.setsid  # pylint: disable=no-member

    if env:
        process_params['env'] = os.environ.copy().update(
            {k: os.path.expandvars(v) for k, v in env.items()})

    return subprocess.Popen(list(map(os.path.expandvars, cmd)),
                            **process_params)


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
