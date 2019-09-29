import re
import sublime

from Sublemon.chimney import ChimneyCommand, ChimneyBuildListener


def setup_python_exec(ctx):
    settings = sublime.load_settings("Preferences.sublime-settings")
    ctx.cmd.appendleft(settings.get('python_binary', 'python'))
    ctx.env['PYTHONIOENCODING'] = 'utf-8'
    ctx.env['PYTHONUNBUFFERED'] = '1'


class PythonCommand(ChimneyCommand):
    def setup(self, ctx):
        setup_python_exec(ctx)
        ctx.set(file_regex='^[ ]*File "(...*?)", line ([0-9]*)')


class PylintCommand(ChimneyCommand):
    def setup(self, ctx):
        ctx.cmd.appendleft('-m', 'pylint')

        if ctx.opt('disable'):
            ctx.cmd.append('--disable=' + ','.join(ctx.opt('disable')))

        setup_python_exec(ctx)
        ctx.set(file_regex=r'(.+?):(\d+):(\d+): (.*)',
                syntax='pylint',
                listener=PylintBuildListener())


class PylintBuildListener(ChimneyBuildListener):
    LINE_PATTERN = re.compile(r'(.+:\d+:)(\d+)(: .*)')

    def __init__(self):
        self.rank = None

    def on_output(self, line, ctx):
        match = self.LINE_PATTERN.match(line)
        if match:
            col = int(match.group(2)) + 1
            line = match.group(1) + str(col) + match.group(3)

        if line.startswith('Your code has been rated at'):
            self.rank = line

        ctx.print(line)

    def on_complete(self, ctx):
        if self.rank:
            ctx.window.status_message(self.rank)


class PycodestyleCommand(ChimneyCommand):
    def setup(self, ctx):
        ctx.cmd.appendleft('-m', 'pycodestyle')
        ctx.cmd.append('--max-line-length=120')

        if ctx.opt('ignore'):
            ctx.cmd.append('--ignore=' + ','.join(ctx.opt('ignore')))

        setup_python_exec(ctx)
        ctx.set(file_regex=r'(.+?):(\d+):(\d+): (.*)',
                syntax='pycodestyle')
