import re
import shlex
import subprocess

from Sublemon.chimney import ChimneyCommand, ChimneyCommandListener, ChimneyBuildError, STARTUPINFO

ESCAPE_CHARACTER = re.compile(r'\x1b.*?\[\d*m')


class WslCommand(ChimneyCommand):
    def preprocess_options(self, options):
        view = self.window.active_view()
        file_name = view.file_name()
        if not file_name:
            raise ChimneyBuildError("No file")

        cmd = ['wsl']

        match = re.match(r"\s*#!(.+)", view.substr(view.line(0)))
        if match:
            cmd.extend(shlex.split(match.group(1)))

        file_name = subprocess.check_output(['wsl', 'wslpath', file_name], startupinfo=STARTUPINFO)
        file_name = str(file_name, 'utf-8').strip()

        cmd.append(file_name)
        options.cmd = cmd

    def get_listener(self):
        return WslCommandListener()


class WslCommandListener(ChimneyCommandListener):
    def on_output(self, line, ctx):
        ctx.print(ESCAPE_CHARACTER.sub('', line))
