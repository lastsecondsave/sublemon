import re
from Sublemon.chimney import Pipe, ChimneyCommand

DASHES_PATTERN        = re.compile(r'\[INFO\] -+')
SUMMARY_PATTERN       = re.compile(r'\[ERROR\] Failed to execute goal.*')
SKIPPED_LINES_PATTERN = re.compile(r'\[[EIW]\w+\].*')

class MavenPipe(Pipe):
    def __init__(self):
        self.skip = False

    def output(self, line):
        if DASHES_PATTERN.match(line):
            return

        if SUMMARY_PATTERN.match(line):
            self.skip = True

        if self.skip and SKIPPED_LINES_PATTERN.match(line):
            return

        i = line.rfind('\r')
        if i != -1:
            line = line[i+1:]

        self.next_pipe.output(line)

class MavenCommand(ChimneyCommand):
    def get_pipe(self, options):
        return MavenPipe()

    def preprocess_options(self, options):
        cmd = [self.conf("mvn_exec", "mvn")]

        if options["offline"]:
            cmd.append("-o")

        if options["quiet"]:
            cmd.append("-q")

        if options["errors"]:
            cmd.append("-e")

        cmd.append(options["mvn_cmd"])

        options.shell_cmd = " ".join(cmd)
        options.syntax = "Packages/Sublemon/maven_spec/maven_build.sublime-syntax"
        options.file_regex = r"^(?:\[(?:ERROR|WARNING)\] )?(\S.*):\[(\d+),(\d+)\](?: error:)? (.*)"

        if not options.working_dir:
            is_pom = self.var("file_name") == "pom.xml"
            options.working_dir = self.var("file_path") if is_pom else self.var("folder")
