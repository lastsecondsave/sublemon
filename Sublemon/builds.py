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


class GolangCommand(ChimneyCommand):
    def setup(self, build):
        if build.cmd:
            build.cmd.appendleft("go")
        else:
            build.cmd.append("go", build.opt("action", "build"), build.working_dir)

        build.syntax = "Generic Build Output"
        build.file_regex = r"(.+?):(\d+):(\d+): (.*)"


class StaticcheckCommand(ChimneyCommand):
    def setup(self, build):
        if build.cmd:
            build.cmd.appendleft("staticcheck")
        else:
            build.cmd.append("staticcheck", build.working_dir)

        build.syntax = "Generic Build Output"
        build.file_regex = r"(.+?):(\d+):(\d+): (.*)"
