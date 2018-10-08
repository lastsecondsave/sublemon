import os.path
import re

import sublime

from Sublemon.chimney import ChimneyCommand, ChimneyCommandListener, RUNNING_ON_WINDOWS

DASHES_PATTERN = re.compile(r'\[INFO\] -+$')
COMPILATION_FAILURE_PATTERN = re.compile(r'\[ERROR\] Failed to execute goal.*Compilation failure')
SKIPPED_LINES_PATTERN = re.compile(r'\[[EIW]\w+\].*')
DRIVE_LETTER_PATTERN = re.compile(r'\[(?:ERROR|WARNING)\] /[A-Z]:')

STATUS_PATTERN = re.compile(r'\[INFO\] BUILD (FAILURE|SUCCESS)$')
TIME_PATTERN = re.compile(r'\[INFO\] Total time:')

FILE_REGEX = r'^\[ERROR\] (\S.*):\[(\d+),(\d+)\](?: error:)? (.*)'


class MavenCommand(ChimneyCommand):
    def preprocess_options(self, options):
        if not options.working_dir:
            variables = self.window.extract_variables()
            is_pom = variables['file_name'] == 'pom.xml'
            options.working_dir = variables['file_path' if is_pom else 'folder']

        cmd = []

        cmd.append('mvn -B')

        if options['offline']:
            cmd.append('-o')

        if options['no_log']:
            cmd.append('-q')
            cmd.append('-e')

        if options['mvn_global_opts']:
            cmd.append(options['mvn_global_opts'])

        if options['mvn_opts']:
            cmd.append(options['mvn_opts'])

        cmd.append(options['mvn_cmd'])

        options.shell_cmd = ' '.join(cmd)
        options.syntax = 'Packages/Sublemon/maven_spec/maven_build.sublime-syntax'
        options.file_regex = FILE_REGEX

    def get_listener(self):
        return MavenCommandListener()


class MavenCommandListener(ChimneyCommandListener):
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
