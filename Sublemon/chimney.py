import copy
import os
import signal
import subprocess

from collections import deque
from itertools import chain
from threading import Lock, Thread

import sublime
from sublime_plugin import WindowCommand

RUNNING_ON_WINDOWS = sublime.platform() == 'windows'

STARTUPINFO = subprocess.STARTUPINFO()
if RUNNING_ON_WINDOWS:
    STARTUPINFO.dwFlags |= subprocess.STARTF_USESHOWWINDOW

RUNNING_BUILDS = {}

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
        self.view.run_command('append', {'characters': '\n'.join(lines)})

    def show(self):
        self.window.run_command('show_panel', {'panel': 'output.exec'})


def format_command(command):
    if isinstance(command, str):
        return command

    def chunks():
        for c in command:
            if "'" in c or ' ' in c:
                yield '"' + c + '"'
            else:
                yield c

    return ' '.join(chunks())


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
        self.message = message


class BuildContext:
    def __init__(self, options):
        self.options = options
        self.listener = ChimneyBuildListener()

    def cancel_build(self, message=None):
        raise BuildError(message)

    def opt(self, name):
        return self.options.get(name)

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
        if value != None:
            self.options[option] = value


def log(message, *params):
    print(message.format(*params))


class ChimneyCommand(WindowCommand):
    def __init__(self, window):
        super().__init__(window)
        self.panel = OutputPanel(window)

    def setup(self, ctx):
        pass

    def run(self, kill=False, **options):
        build = RUNNING_BUILDS.get(self.window.id())

        if build:
            self.window.status_message('Cancelling build...')
            build.cancelled = True
            kill_process(build.process)

        if kill:
            return

        ctx = BuildContext(options)

        try:
            self.setup(ctx)
            if not 'cmd' in options and not 'shell_cmd' in options:
                ctx.cancel_build('No command')

        except BuildError as err:
            self.window.status_message(': '.join(filter(None, ('Build error', err.message))))
            return

        self.panel.reset(
            result_base_dir=self.change_working_dir(options.get('working_dir')),
            result_file_regex=options.get('file_regex'),
            result_line_regex=options.get('line_regex'),
            syntax=options.get('syntax')
        )

        self.panel.show()

        build = start_build(self.panel, options, ctx.listener)
        RUNNING_BUILDS[self.window.id()] = build
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
        self.cancelled = False

        self.listener.on_startup(self)

    def print(self, line):
        self.panel.append(line)

    def complete(self):
        RUNNING_BUILDS.pop(self.window.id(), None)

        if self.cancelled:
            self.window.status_message('Build cancelled')
            self.print('\n💀 Terminated 💀')
            log('✘ [{}]', self.process.pid)
        else:
            self.listener.on_complete(self)
            log('✔ [{}]', self.process.pid)


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
        startupinfo=STARTUPINFO,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.DEVNULL)

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
        subprocess.Popen(cmd, startupinfo=STARTUPINFO)
    else:
        os.killpg(process.pid, signal.SIGTERM)
        process.terminate()

    process.wait()
