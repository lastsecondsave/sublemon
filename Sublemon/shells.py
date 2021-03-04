import re

from .chimney import ChimneyBuildListener, ChimneyCommand, Cmd

ESCAPE_CHARACTER = re.compile(r"\x1b.*?\[\d*m")
WIN_PATH = re.compile(r"([A-Za-z]):\\(.*)")


class TrimEscapeSequencesListener(ChimneyBuildListener):
    def on_output(self, line, ctx):
        return ESCAPE_CHARACTER.sub("", line)

    def on_error(self, line, ctx):
        return ESCAPE_CHARACTER.sub("", line)


class WslCommand(ChimneyCommand):
    def setup(self, build):
        for i, val in enumerate(build.cmd.args):
            if match := WIN_PATH.match(val):
                drive = match.group(1).lower()
                path = match.group(2).replace("\\", "/")
                build.cmd.args[i] = f"/{drive}/{path}"

        build.cmd.appendleft("wsl")
        build.listener = TrimEscapeSequencesListener()


class PwshCommand(ChimneyCommand):
    def setup(self, build):
        if file := build.opt("file"):
            build.cmd.appendleft("-File", file)
        elif cmdline := build.cmd.cmdline:
            build.cmd = Cmd({"cmd": ("-Command", cmdline)})

        build.cmd.appendleft("pwsh", "-NoProfile")
        build.listener = TrimEscapeSequencesListener()
