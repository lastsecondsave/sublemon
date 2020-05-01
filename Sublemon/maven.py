import re
import shlex

from . import RUNNING_ON_WINDOWS
from .chimney import ChimneyBuildListener, ChimneyCommand

DASHES_PATTERN = re.compile(r'\[INFO\] -{5,}.*')
COMPILATION_FAILURE_PATTERN = re.compile(r'\[ERROR\] Failed to execute goal.*Compilation failure')
SKIPPED_LINES_PATTERN = re.compile(r'\[[EIW]\w+\].*')
DRIVE_LETTER_PATTERN = re.compile(r'\[(?:ERROR|WARNING)\] /[A-Z]:')

STATUS_PATTERN = re.compile(r'\[INFO\] BUILD (FAILURE|SUCCESS)$')
TIME_PATTERN = re.compile(r'\[INFO\] Total time:')

FILE_REGEX = r'^\[ERROR\] (\S.*):\[(\d+),(\d+)\](?: error:)? (.*)'


class MavenCommand(ChimneyCommand):
    def setup(self, build):
        if build.opt('offline'):
            build.cmd.appendleft('-o')

        if build.opt('quiet'):
            build.cmd.appendleft('-q', '-e')

        build.cmd.appendleft("mvn", "-B")

        if opts := build.opt("mvn_opts"):
            build.cmd.append(*shlex.split(opts))

        build.cmd.shell = True

        build.listener = MavenBuildListener()
        build.syntax = "maven_build"
        build.file_regex = FILE_REGEX


class MavenBuildListener(ChimneyBuildListener):
    def __init__(self):
        self.skip = False
        self.status = None
        self.time = None

    def on_output(self, line, ctx):
        if COMPILATION_FAILURE_PATTERN.match(line):
            self.skip = True

        if self.skip and SKIPPED_LINES_PATTERN.match(line):
            return

        if DASHES_PATTERN.match(line):
            return

        if STATUS_PATTERN.match(line):
            self.status = line[7:]

        if TIME_PATTERN.match(line):
            self.time = line[7:]

        if RUNNING_ON_WINDOWS:
            match = DRIVE_LETTER_PATTERN.match(line)
            if match:
                line = line[:match.end()-1] + line[match.end():]

        ctx.print(line)

    def on_complete(self, ctx):
        if self.status:
            info = (self.status, self.time)
            ctx.window.status_message(', '.join(info))
