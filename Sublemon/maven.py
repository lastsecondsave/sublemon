import os.path
import re

import sublime

from Sublemon.chimney import Pipe, ChimneyCommand


RUNNING_ON_WINDOWS = sublime.platform() == 'windows'

DASHES_PATTERN = re.compile(r'\[INFO\] -+$')
COMPILATION_FAILURE_PATTERN = re.compile(r'\[ERROR\] Failed to execute goal.*Compilation failure')
SKIPPED_LINES_PATTERN = re.compile(r'\[[EIW]\w+\].*')
DRIVE_LETTER_PATTERN  = re.compile(r'\[(?:ERROR|WARNING)\] /[A-Z]:')

STATUS_PATTERN = re.compile(r'\[INFO\] BUILD (FAILURE|SUCCESS)$')
TIME_PATTERN = re.compile(r'\[INFO\] Total time:')

FILE_REGEX = r'^\[ERROR\] (\S.*):\[(\d+),(\d+)\](?: error:)? (.*)'


class MavenPipe(Pipe):
    def __init__(self, window):
        self.window = window
        self.skip = False
        self.status = None
        self.time = None

    def output(self, line):
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

        self.next_pipe.output(line)

    def close(self):
        if self.status:
            info = (self.status, self.time)
            self.window.status_message(', '.join(info))


class MavenCommand(ChimneyCommand):
    def create_pipe(self, options):
        return MavenPipe(self.window)

    def preprocess_options(self, options):
        if options.working_dir is None:
            variables = self.window.extract_variables()
            is_pom = variables['file_name'] == 'pom.xml'
            options.working_dir = variables['file_path' if is_pom else 'folder']

        cmd = []

        if os.path.exists(os.path.join(options.working_dir, '.jenv-version')):
            cmd.append('jenv exec')

        cmd.append('mvn')

        if options['offline']:
            cmd.append('-o')

        if options['quiet']:
            cmd.append('-q')

        if options['errors']:
            cmd.append('-e')

        if options['mvn_global_opts']:
            cmd.append(options['mvn_global_opts'])

        if options['mvn_opts']:
            cmd.append(options['mvn_opts'])

        cmd.append(options['mvn_cmd'])

        options.shell_cmd = ' '.join(cmd)
        options.syntax = 'Packages/Sublemon/maven_spec/maven_build.sublime-syntax'
        options.file_regex = FILE_REGEX

    def startup_message(self, options):
        return 'Started ' + options.shell_cmd
