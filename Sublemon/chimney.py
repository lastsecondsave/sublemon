import copy
import os
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


def format_command(command):
    if isinstance(command, str):
        return command

    chunks = ('"' + c + '"' if ("'" in c) or (' ' in c) else c
              for c in command)

    return ' '.join(chunks)


# pylint: disable=no-self-use
class ChimneyBuildListener:
    def on_startup(self, ctx):
        ctx.window.status_message('Build started: ' + format_command(ctx.process.args))

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


class BuildContext:
    def __init__(self, options, window):
        self.options = options
        self.window = window
        self.listener = ChimneyBuildListener()

    @staticmethod
    def cancel_build(message=None):
        raise BuildError(message)

    def opt(self, name):
        return self.options.get(name, None)

    def file_name(self):
        return self.window.active_view().file_name()

    # pylint: disable=too-many-arguments
    def set(self,
            cmd=None,
            working_dir=None,
            syntax=None,
            file_regex=None,
            line_regex=None,
            env=None,
            listener=None):

        self.listener = listener or self.listener

        self.set_option('file_regex', file_regex, '')
        self.set_option('line_regex', line_regex, '')
        self.set_option('env', env)
        self.set_option('working_dir', working_dir)

        if syntax and not syntax.endswith(('.sublime-syntax', '.tmLanguage')):
            syntax = 'Packages/Sublemon/syntaxes/{}.sublime-syntax'.format(syntax)
        self.set_option('syntax', syntax, 'Packages/Text/Plain text.tmLanguage')

        if isinstance(cmd, str):
            self.set_option('shell_cmd', cmd)
        elif isinstance(cmd, list):
            self.set_option('cmd', cmd)

    def set_option(self, option, value, default=None):
        value = value or self.options.get(option, default)
        if value is not None:
            self.options[option] = value


def log(message, *params):
    print(message.format(*params))


class ChimneyCommand(WindowCommand):
    builds = {}
    panels = {}

    def __init__(self, window):
        super().__init__(window)

        if not window.id() in self.panels:
            self.panels[window.id()] = OutputPanel(window)

    def setup(self, ctx):
        pass

    def run(self, kill=False, **options):
        wid = self.window.id()

        if self.builds.get(wid, None):
            self.window.status_message('Cancelling build...')
            self.builds[wid].cancel(kill)

        if kill:
            return

        ctx = BuildContext(options, self.window)

        try:
            self.setup(ctx)
            if 'cmd' not in options and 'shell_cmd' not in options:
                ctx.cancel_build('No command')

        except BuildError as err:
            self.window.status_message(': '.join(filter(None, ('Build error', err.message))))
            return

        panel = self.panels[wid]

        panel.reset(
            result_base_dir=self.change_working_dir(options.get('working_dir')),
            result_file_regex=options.get('file_regex'),
            result_line_regex=options.get('line_regex'),
            syntax=options.get('syntax')
        )

        panel.show()

        build = start_build(panel, options, ctx.listener)
        self.builds[wid] = build

        log('→ [{}] {}', build.process.pid, format_command(build.process.args))

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

    def cancel(self, kill):
        self.cancelled = 'kill' if kill else 'restart'
        kill_process(self.process)

    def __bool__(self):
        '''True if process is active.'''
        return bool(self.process and not self.process.poll())


def start_build(panel, options, listener):
    process = start_process(options)
    ctx = RunningBuildContext(panel, process, listener)

    output_buffer = OutputBuffer(lambda line: listener.on_output(line, ctx))
    error_buffer = OutputBuffer(lambda line: listener.on_error(line, ctx))

    AsyncStreamConsumer(process.stdout, output_buffer,
                        on_close=ctx.complete).start()
    AsyncStreamConsumer(process.stderr, error_buffer).start()

    return ctx


def start_process(options):
    process_params = dict(
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.DEVNULL)

    if RUNNING_ON_WINDOWS:
        process_params['startupinfo'] = startupinfo()
    else:
        process_params['preexec_fn'] = os.setsid  # pylint: disable=no-member

    if 'shell_cmd' in options:
        cmd = options['shell_cmd']
        if RUNNING_ON_WINDOWS:
            process_params['shell'] = True
        else:
            cmd = [os.environ['SHELL'], '-c', cmd]
    else:
        cmd = options['cmd']

    if 'env' in options:
        env = os.environ.copy()
        env.update({k: os.path.expandvars(v) for k, v in options['env'].items()})
        process_params['env'] = env

    return subprocess.Popen(cmd, **process_params)


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
