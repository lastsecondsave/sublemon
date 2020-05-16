import re

from .chimney import ChimneyBuildListener, ChimneyCommand

ESCAPE_CHARACTER = re.compile(r"\x1b.*?\[\d*m")
WIN_PATH = re.compile(r"([A-Za-z]):\\(.*)")


class WslCommand(ChimneyCommand):
    def setup(self, build):
        for i, val in enumerate(build.cmd.args):
            if match := WIN_PATH.match(val):
                drive = match.group(1).lower()
                path = match.group(2).replace("\\", "/")
                build.cmd.args[i] = f"/{drive}/{path}"

        build.cmd.appendleft("wsl")
        build.listener = WslBuildListener()


class WslBuildListener(ChimneyBuildListener):
    def on_output(self, line, ctx):
        ctx.print(ESCAPE_CHARACTER.sub("", line))
