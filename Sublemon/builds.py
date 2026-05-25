import re

from .chimney import ChimneyCommand, Cmd

GENERIC_BUILD_FILE_REGEX = r"^ *(.+?):(\d+):(\d+): (.*)"
GENERIC_BUILD_SYNTAX = "Generic Build Output"


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
        if file := build.optx("file"):
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

        build.syntax = GENERIC_BUILD_SYNTAX
        build.file_regex = GENERIC_BUILD_FILE_REGEX


class StaticcheckCommand(ChimneyCommand):
    def setup(self, build):
        if build.cmd:
            build.cmd.appendleft("staticcheck")
        else:
            build.cmd.append("staticcheck", build.working_dir)

        build.syntax = GENERIC_BUILD_SYNTAX
        build.file_regex = GENERIC_BUILD_FILE_REGEX
