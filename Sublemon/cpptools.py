import subprocess
from multiprocessing import cpu_count
from pathlib import Path

from . import RUNNING_ON_WINDOWS, listify, pref
from .chimney import ChimneyBuildListener, ChimneyCommand, Cmd
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

        build.file_regex = r"(.+?):(\d+):(?:(\d+):)? (.*)"
        build.syntax = "GCC Output"


class VcvarsCommand(ChimneyCommand):
    env = None

    def capture_env(self, build):
        self.window.status_message("Capturing variables from vcvars")

        vs_path = Path("C:/Program Files/Microsoft Visual Studio/2022/Community")
        vcvars_path = vs_path / "VC/Auxiliary/Build/vcvarsall.bat"

        variables = ["LIB", "INCLUDE", "PATH"]
        echo_cmd = " ".join(f'"""!{var} $env:{var}"""' for var in variables)
        pwsh_cmd = f"pwsh -NoProfile -NoLogo -Command Write-Output {echo_cmd}"

        cmd = f'"{vcvars_path}" x64 && {pwsh_cmd}'
        process = subprocess.run(cmd, shell=True, capture_output=True)

        if process.returncode != 0:
            print(f"‼ Failed to run program: {cmd}")
            build.cancel("Failed to capture variables from vcvars")

        captures = {}

        for line in process.stdout.decode("utf-8").splitlines():
            if not line.startswith("!"):
                continue

            key, value = line.strip("! ").split(maxsplit=1)
            captures[key] = value

        self.env = captures
        build.env = captures

    def setup(self, build):
        if not RUNNING_ON_WINDOWS:
            build.cancel("MSVC only works on Windows")

        if not self.env:
            build.initializer = self.capture_env

        build.env = self.env


class CmakeCommand(ChimneyCommand):
    def setup(self, build):
        build.in_project_dir()

        mode = build.opt("mode", "build")

        build_dir = build.opt("build_dir") or pref(
            "cmake_build_dir", "build", window=self.window
        )

        build_type = build.opt("build_type") or pref(
            "cmake_build_type", "Release", window=self.window
        )

        if mode == "generate":
            build.cmd.appendleft(
                "cmake", ".", "-B", build_dir, f"-DCMAKE_BUILD_TYPE={build_type}"
            )

            if params := pref("cmake_parameters", window=self.window):
                build.cmd.append(*params)

            build.file_regex = r"CMake Error at (.+?):(\d+) (.*):"
            return

        if mode != "build":
            build.cancel(f"Invalid mode: {mode}")

        jobs = max(cpu_count() - 2, 1)

        cmd = ["cmake", "--build", build_dir, "--parallel", str(jobs)]

        if build.cmd.args:
            build.cmd.preview = f"cmake {' '.join(build.cmd.args)}"
            build.cmd.appendleft(*cmd)
        else:
            build_targets = listify(
                build.opt("build_target")
                or pref("cmake_default_target", window=self.window)
            )

            build.cmd = Cmd(cmd)

            if build_targets:
                build.cmd.append("--target", *build_targets)
                build.cmd.preview = f"cmake --target {' '.join(build_targets)}"

        if RUNNING_ON_WINDOWS:
            build.file_regex = r"(.+?)\((\d+),?(\d+)\): (.*)"
            build.syntax = "MSVC Output"

            build.cmd.append("--config", build_type)
        else:
            build.file_regex = r"^(/.+?):(\d+):(?:(\d+):)? (.*)"
            build.syntax = "GCC Output"
