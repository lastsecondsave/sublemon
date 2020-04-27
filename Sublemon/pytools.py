import re
import sublime

from Sublemon.chimney import ChimneyCommand, ChimneyBuildListener


def setup_python_exec(ctx, module=None):
    module = ctx.opt('module') or module
    if module:
        ctx.cmd.appendleft('-m', module)

    settings = sublime.load_settings("Preferences.sublime-settings")
    ctx.cmd.appendleft(settings.get('python_binary', 'python'))

    ctx.env['PYTHONIOENCODING'] = 'utf-8'
    ctx.env['PYTHONUNBUFFERED'] = '1'


class PythonCommand(ChimneyCommand):
    def setup(self, ctx):
        setup_python_exec(ctx)


class PylintCommand(ChimneyCommand):
    def setup(self, ctx):
        if disable := ctx.opt("disable"):
            ctx.cmd.append(f"--disable={','.join(disable)}")

        if pylintrc := ctx.opt("pylintrc"):
            ctx.cmd.append(f"--rcfile={pylintrc}")

        setup_python_exec(ctx, 'pylint')
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
