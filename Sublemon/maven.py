import re
import Sublemon.chimney

DASHES_PATTERN        = re.compile(r'\[INFO\] -+')
SUMMARY_PATTERN       = re.compile(r'\[ERROR\] Failed to execute goal.*')
SKIPPED_LINES_PATTERN = re.compile(r'\[[EIW]\w+\].*')

class MavenPipe(Sublemon.chimney.Pipe):
    def __init__(self):
        super().__init__()
        self.skip = False

    def output(self, line):
        if DASHES_PATTERN.match(line):
            return

        if SUMMARY_PATTERN.match(line):
            self.skip = True

        if self.skip and SKIPPED_LINES_PATTERN.match(line):
            return

        self.next_pipe.output(line)

class MavenCommand(Sublemon.chimney.ChimneyCommand):
    def get_pipe(self, options):
        return MavenPipe()
