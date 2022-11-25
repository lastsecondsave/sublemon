from .chimney import ChimneyCommand


class RsyncCommand(ChimneyCommand):
    def setup(self, build):
        build.cmd.appendleft("rsync", "-e", "ssh", "-avr")

        host = build.opt("host", required=True)
        destination = build.opt("destination", required=True)
        sources = build.opt("sources", required=True)

        build.cmd.append(*sources)
        build.cmd.append(f"{host}:{destination}")
