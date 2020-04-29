import re
from .chimney import ChimneyCommand, ChimneyBuildListener

ESCAPE_CHARACTER = re.compile(r'\x1b.*?\[\d*m')
WIN_PATH = re.compile(r'([A-Za-z]):\\(.*)')


class WslCommand(ChimneyCommand):
    def setup(self, build):
        for i, val in enumerate(build.cmd.args):
            match = WIN_PATH.match(val)
            if match:
                build.cmd.args[i] = ("/{}/{}".format(match.group(1).lower(),
                                                     match.group(2).replace('\\', '/')))

        build.cmd.appendleft("wsl")
        build.listener = WslBuildListener()


class WslBuildListener(ChimneyBuildListener):
    def on_output(self, line, ctx):
        ctx.print(ESCAPE_CHARACTER.sub('', line))
