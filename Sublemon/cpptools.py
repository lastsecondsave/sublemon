from .chimney import ChimneyBuildListener, ChimneyCommand
from .pytools import setup_python_exec


class CpplintCommand(ChimneyCommand):
    def setup(self, build):
        setup_python_exec(build, "cpplint", allow_venv=False)

        build.file_regex = r"(.+?):(\d+)(): (.*)"
        build.syntax = "cpplint"
        build.listener = CpplintBuildListener()


class CpplintBuildListener(ChimneyBuildListener):
    def __init__(self):
        self.output_lines = [""]

    def on_output(self, line, ctx):
        if not line.startswith("Done processing"):
            self.output_lines.append(line)

    def on_error(self, line, ctx):
        if line.startswith(ctx.working_dir):
            line = line[len(ctx.working_dir) + 1 :]

        line = line.replace("  ", " ")

        return line

    def on_complete(self, ctx):
        ctx.print_lines(self.output_lines)
