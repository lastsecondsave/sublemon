import subprocess
from pathlib import Path

from . import sad_message, RUNNING_ON_WINDOWS
from .chimney import ChimneyBuildListener, ChimneyCommand
from .pytools import setup_python_exec


class CpplintCommand(ChimneyCommand):
    def setup(self, build):
        setup_python_exec(build, "cpplint", allow_venv=False)

        build.file_regex = r"(.+?):(\d+)(): (.*)"
        build.syntax = "Cpplint Output"
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


class MakeCommand(ChimneyCommand):
    def setup(self, build):
        build.cmd.appendleft("make", "-j")

        build.file_regex = r"(.+?):(\d+):(\d+): (.*)"
        build.syntax = "GCC Output"


class VcvarsCommand(ChimneyCommand):
    env = None

    def capture_env(self, build):
        vs_path = Path("C:/Program Files/Microsoft Visual Studio/2022/Community")
        vcvars_path = vs_path / "VC/Auxiliary/Build/vcvarsall.bat"

        variables = ["LIB", "INCLUDE", "PATH"]
        echo_cmd = " ".join(f'"""!{var} $env:{var}"""' for var in variables)
        pwsh_cmd = f"pwsh -NoProfile -NoLogo -Command Write-Output {echo_cmd}"

        cmd = f'"{vcvars_path}" x64 && {pwsh_cmd}'
        process = subprocess.run(cmd, shell=True, capture_output=True)

        if process.returncode != 0:
            sad_message(f"Failed to run program: {cmd}")
            build.cancel("Failed to capture variables from vcvars")

        captures = {}

        for line in process.stdout.decode("utf-8").splitlines():
            if not line.startswith("!"):
                continue

            key, value = line.strip("! ").split(maxsplit=1)
            captures[key] = value

        return captures

    def setup(self, build):
        if not RUNNING_ON_WINDOWS:
            build.cancel("MSVC only works on Windows")

        if not self.env:
            print("Capturing variables from vcvars")
            self.env = self.capture_env(build)

        build.env = self.env
