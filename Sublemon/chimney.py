import copy
import os
import signal
import subprocess

from collections import deque
from threading import Lock, Thread

import sublime
from sublime_plugin import WindowCommand

RUNNING_ON_WINDOWS = sublime.platform() == 'windows'

STARTUPINFO = subprocess.STARTUPINFO()
if RUNNING_ON_WINDOWS:
    STARTUPINFO.dwFlags |= subprocess.STARTF_USESHOWWINDOW


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


class OutputPanel:
    def __init__(self, window):
        self.window = window
        self.view = window.create_output_panel('exec')

        self.line_buffer_lock = Lock()
        self.line_buffer = deque()

        self.lines_printed = 0

    def reset(self, syntax=None, **settings):
        view_settings = self.view.settings()

        view_settings.set('gutter', False)
        view_settings.set('scroll_past_end', False)
        view_settings.set('word_wrap', True)

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

        if self.lines_printed:
            lines.appendleft('')

        self.lines_printed += 1

        characters = '\n'.join(lines)
        self.view.run_command('append', {'characters': characters})

    def show(self):
        self.window.run_command('show_panel', {'panel': 'output.exec'})


class Options:
    def __init__(self, options, window):
        self.originals = options

        self.kill = self.get('kill', False)
        self.cmd = self.get('cmd')
        self.shell_cmd = self.get('shell_cmd')
        self.file_regex = self.get('file_regex', '')
        self.line_regex = self.get('line_regex', '')
        self.syntax = self.get('syntax', 'Packages/Text/Plain text.tmLanguage')
        self.scroll_to_end = self.get('scroll_to_end', True)
        self.working_dir = self.get('working_dir')
        self.env = self.get("env")

        self.source_file = '"{}"'.format(window.extract_variables().get('file'))

    def get(self, arg, default=None):
        return self.originals.get(arg, default)

    def __getitem__(self, arg):
        return self.get(arg)


class ExecutorContext:
    def __init__(self, executor, options, process, listener):
        self.window = executor.window
        self.executor = executor
        self.options = options
        self.process = process
        self.listener = listener
        self.completed = False

    def print(self, line):
        self.executor.output_panel.append(line)

    def complete(self):
        self.window.status_message('Build finished')
        self.listener.on_complete(self)

        self.process.poll()

        if self.process.returncode:
            _log('✗ [{}] {}', self.process.pid, self.process.returncode)
        else:
            _log('✓ [{}]', self.process.pid)

        self.completed = True


class Executor:
    def __init__(self, window):
        self.window = window
        self.output_panel = OutputPanel(window)
        self.ctx = None

    def run(self, options, listener):
        if self.ctx and not self.ctx.completed:
            self.kill_process()

        if options.kill:
            return

        working_dir = self.get_working_dir(options.working_dir)

        self.output_panel.reset(
            syntax=options.syntax,
            result_base_dir=working_dir,
            result_file_regex=options.file_regex,
            result_line_regex=options.line_regex
        )

        process = self.start_process(options, working_dir)
        self.ctx = ExecutorContext(self, options, process, listener)

        listener.on_startup(self.ctx)

        output_buffer = OutputBuffer(lambda line: listener.on_output(line, self.ctx))
        error_buffer = OutputBuffer(lambda line: listener.on_error(line, self.ctx))

        AsyncStreamConsumer(process.stdout, output_buffer,
                            on_close=self.ctx.complete).start()
        AsyncStreamConsumer(process.stderr, error_buffer).start()

        self.output_panel.show()

    def get_working_dir(self, working_dir):
        if not working_dir:
            view = self.window.active_view()
            if view and view.file_name():
                return os.path.dirname(view.file_name())

        if not os.path.isabs(working_dir):
            base_path = self.window.extract_variables().get('project_path')
            working_dir = os.path.join(base_path, working_dir)

        return working_dir

    def start_process(self, options, working_dir):
        process_params = dict(
            startupinfo=STARTUPINFO,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL)

        if options.shell_cmd:
            if RUNNING_ON_WINDOWS:
                cmd = options.shell_cmd
                process_params['shell'] = True
            else:
                cmd = [os.environ['SHELL'], '-c', options.shell_cmd]
        else:
            cmd = options.cmd

        if options.env:
            env = os.environ.copy()
            env.update({k: os.path.expandvars(v) for k, v in options.env.items()})
            process_params['env'] = env

        os.chdir(working_dir)

        process = subprocess.Popen(cmd, **process_params)

        cmd = cmd if isinstance(cmd, str) else ' '.join(cmd)

        _log('→ [{}] {}', process.pid, cmd)
        self.window.status_message('Build started: {}'.format(cmd))

        return process

    def kill_process(self):
        process = self.ctx.process

        _log('Killing {}', process.pid)

        if RUNNING_ON_WINDOWS:
            cmd = 'taskkill /T /F /PID {}'.format(process.pid)
            subprocess.Popen(cmd, startupinfo=STARTUPINFO)
        else:
            os.killpg(process.pid, signal.SIGTERM)
            process.terminate()


class ChimneyCommandListener:
    def on_startup(self, ctx):
        pass

    def on_output(self, line, ctx):
        ctx.print(line)

    def on_error(self, line, ctx):
        ctx.print(line)

    def on_complete(self, ctx):
        pass


class ChimneyBuildError(Exception):
    def __init__(self, message=None):
        super().__init__()
        self.message = message


class ChimneyCommand(WindowCommand):
    def __init__(self, window):
        super().__init__(window)
        _get_executor(window)

    def get_listener(self):
        return ChimneyCommandListener()

    def preprocess_options(self, options):
        pass

    def run(self, **kwargs):
        if 'update_phantoms_only' in kwargs:
            return

        options = Options(kwargs, self.window)

        try:
            self.preprocess_options(options)
        except ChimneyBuildError as err:
            msg = list(filter(None, ['Build error', err.message]))
            self.window.status_message(': '.join(msg))
            return

        if not options.cmd and not options.shell_cmd and not options.kill:
            self.window.status_message('Build error: No command')
            return

        if '.sublime-syntax' not in options.syntax and '.tmLanguage' not in options.syntax:
            options.syntax = 'Packages/Sublemon/syntaxes/' + options.syntax + '.sublime-syntax'

        _get_executor(self.window).run(options, self.get_listener())


_EXECUTORS = {}


def _get_executor(window):
    wid = window.id()
    if wid not in _EXECUTORS:
        _EXECUTORS[wid] = Executor(window)
        _log('Created executor for window #{}', wid)

    return _EXECUTORS[wid]


def _log(message, *params):
    print('Chimney:', message.format(*params))
