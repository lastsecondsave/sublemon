from .chimney import ChimneyBuildListener, ChimneyCommand


class RsyncCommand(ChimneyCommand):
    def setup(self, build):
        build.cmd.appendleft("rsync", "-e", "ssh", "-avr")

        host = build.opt("host", required=True)
        destination = build.opt("destination", required=True)
        sources = build.opt("sources", required=True)

        build.cmd.append(*sources)
        build.cmd.append(f"{host}:{destination}")

        build.listener = RsyncBuildListener()


class RsyncBuildListener(ChimneyBuildListener):
    def on_output(self, line, ctx):
        if line.startswith("sent "):
            ctx.on_complete_message = line.replace("  ", "; ")
        return line
