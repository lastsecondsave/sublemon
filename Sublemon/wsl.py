import re
import shlex
import subprocess

from Sublemon.chimney import ChimneyCommand, ChimneyCommandListener, ChimneyBuildError

ESCAPE_CHARACTER = re.compile(r'\x1b.*?\[\d*m')
SHEBANG = re.compile(r'\s*#!(.+)')


class WslCommand(ChimneyCommand):
    def preprocess_options(self, options):
        view = self.window.active_view()
        filename = view.file_name()
        if not filename:
            raise ChimneyBuildError("No file")

        cmd = ['wsl']

        match = SHEBANG.match(view.substr(view.line(0)))
        if match:
            cmd.extend(shlex.split(match.group(1)))

        cmd.append("$(wslpath '{}')".format(filename))
        options.cmd = cmd

    def get_listener(self):
        return WslCommandListener()


class WslCommandListener(ChimneyCommandListener):
    def on_output(self, line, ctx):
        ctx.print(ESCAPE_CHARACTER.sub('', line))
