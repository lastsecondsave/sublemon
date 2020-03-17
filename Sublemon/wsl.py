import re
from Sublemon.chimney import ChimneyCommand, ChimneyBuildListener

ESCAPE_CHARACTER = re.compile(r'\x1b.*?\[\d*m')
SHEBANG = re.compile(r'\s*#!(.+)')
WIN_PATH = re.compile(r'([A-Za-z]):\\(.*)')


class WslCommand(ChimneyCommand):
    def setup(self, ctx):
        for i, val in enumerate(ctx.cmd.args):
            match = WIN_PATH.match(val)
            if match:
                ctx.cmd.args[i] = ("/{}/{}".format(match.group(1).lower(),
                                                   match.group(2).replace('\\', '/')))

        ctx.cmd.appendleft("wsl")
        ctx.set(listener=WslBuildListener())


class WslBuildListener(ChimneyBuildListener):
    def on_output(self, line, ctx):
        ctx.print(ESCAPE_CHARACTER.sub('', line))
