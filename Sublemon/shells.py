import re

from .chimney import ChimneyCommand, Cmd


class WslCommand(ChimneyCommand):
    WIN_PATH = re.compile(r"([A-Za-z]):\\(.*)")

    def setup(self, build):
        for i, val in enumerate(build.cmd.args):
            if match := self.WIN_PATH.match(val):
                drive = match.group(1).lower()
                path = match.group(2).replace("\\", "/")
                build.cmd.args[i] = f"/{drive}/{path}"

        build.cmd.appendleft("wsl")


class PwshCommand(ChimneyCommand):
    def setup(self, build):
        if file := build.opt("file"):
            build.cmd.appendleft("-File", file)
        elif cmdline := build.cmd.cmdline:
            build.cmd = Cmd(cmd=["-Command", cmdline])

        build.cmd.appendleft("pwsh", "-NoProfile")
