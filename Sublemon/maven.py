import re
import Sublemon.chimney

DASHES_PATTERN        = re.compile(r'\[INFO\] -+')
SUMMARY_PATTERN       = re.compile(r'\[ERROR\] Failed to execute goal.*')
SKIPPED_LINES_PATTERN = re.compile(r'\[[EIW]\w+\].*')

class MavenPipe(Sublemon.chimney.Pipe):
    def __init__(self):
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

    def preprocess_options(self, options):
        cmd = ["mvn"]

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
            window_vars = self.window.extract_variables()

            if window_vars["file_name"] == "pom.xml":
                options.working_dir = window_vars["file_path"]
            else:
                options.working_dir = window_vars['folder']
