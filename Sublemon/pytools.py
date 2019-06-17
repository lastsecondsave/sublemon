import re

from Sublemon.chimney import ChimneyCommand, ChimneyBuildListener

LINE_PATTERN = re.compile(r'(.+:\d+:)(\d+)(: .*)')


class PylintCommand(ChimneyCommand):
    def setup(self, ctx):
        cmd = ['python', '-m', 'pylint', self.window.active_view().file_name()]

        if ctx.opt('disable'):
            cmd.append('--disable=' + ','.join(ctx.opt('disable')))

        ctx.set(cmd=cmd,
                file_regex=r'(.+?):(\d+):(\d+): (.*)',
                syntax='pylint',
                listener=PylintBuildListener())


class PylintBuildListener(ChimneyBuildListener):
    def __init__(self):
        self.rank = None

    def on_output(self, line, ctx):
        match = LINE_PATTERN.match(line)
        if match:
            col = int(match.group(2)) + 1
            line = match.group(1) + str(col) + match.group(3)

        if line.startswith('Your code has been rated at'):
            self.rank = line

        ctx.print(line)

    def on_complete(self, ctx):
        if self.rank:
            ctx.window.status_message(self.rank)
