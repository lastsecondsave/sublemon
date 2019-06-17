import re
import shlex

from Sublemon.chimney import ChimneyCommand, ChimneyBuildListener

ESCAPE_CHARACTER = re.compile(r'\x1b.*?\[\d*m')
SHEBANG = re.compile(r'\s*#!(.+)')


class WslCommand(ChimneyCommand):
    def setup(self, ctx):
        view = self.window.active_view()

        filename = view.file_name()
        if not filename:
            ctx.cancel_build("No file")

        cmd = ['wsl']

        match = SHEBANG.match(view.substr(view.line(0)))
        if match:
            cmd.extend(shlex.split(match.group(1)))

        cmd.append("$(wslpath '{}')".format(filename))

        ctx.set(cmd=cmd,
                listener=WslBuildListener())


class WslBuildListener(ChimneyBuildListener):
    def on_output(self, line, ctx):
        ctx.print(ESCAPE_CHARACTER.sub('', line))
