import os.path
import re

import sublime

from Sublemon.chimney import ChimneyCommand, ChimneyBuildListener, RUNNING_ON_WINDOWS

DASHES_PATTERN = re.compile(r'\[INFO\] -{5,}.*')
COMPILATION_FAILURE_PATTERN = re.compile(r'\[ERROR\] Failed to execute goal.*Compilation failure')
SKIPPED_LINES_PATTERN = re.compile(r'\[[EIW]\w+\].*')
DRIVE_LETTER_PATTERN = re.compile(r'\[(?:ERROR|WARNING)\] /[A-Z]:')

STATUS_PATTERN = re.compile(r'\[INFO\] BUILD (FAILURE|SUCCESS)$')
TIME_PATTERN = re.compile(r'\[INFO\] Total time:')

FILE_REGEX = r'^\[ERROR\] (\S.*):\[(\d+),(\d+)\](?: error:)? (.*)'


class MavenCommand(ChimneyCommand):
    def setup(self, ctx):
        cmd = ['mvn',
               ctx.opt('cmd'),
               '-B',
               ctx.opt('mvn_opts')]

        if ctx.opt('offline'):
            cmd.append('-o')

        if ctx.opt('no_info_messages'):
            cmd += append(['-q', '-e'])

        ctx.set(cmd=' '.join(filter(None, cmd)),
                syntax='maven_build',
                file_regex=FILE_REGEX,
                listener=MavenBuildListener())


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
