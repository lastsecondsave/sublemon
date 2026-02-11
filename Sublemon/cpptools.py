import re
import shutil
import subprocess
from multiprocessing import cpu_count
from pathlib import Path

from . import RUNNING_ON_WINDOWS, listify
from .chimney import ChimneyBuildListener, ChimneyCommand, Cmd


class MakeCommand(ChimneyCommand):
    def setup(self, build):
        build.cmd.appendleft("make", "-j")

        build.file_regex = r"(.+?):(\d+):(?:(\d+):)? (.*)"
        build.syntax = "GCC Output"


class VcenvCommand(ChimneyCommand):
    env = None

    def capture_env(self, build):
        self.window.status_message("Capturing VC environment")

        vs_path = Path("C:/Program Files/Microsoft Visual Studio/18/Community")
        vcvars_path = vs_path / "VC/Auxiliary/Build/vcvarsall.bat"

        variables = ["LIB", "INCLUDE", "PATH"]
        echo_cmd = " ".join(f'"""!{var} $env:{var}"""' for var in variables)
        pwsh_cmd = f"pwsh -NoProfile -NoLogo -Command Write-Output {echo_cmd}"

        cmd = f'"{vcvars_path}" x64 && {pwsh_cmd}'
        process = subprocess.run(cmd, shell=True, capture_output=True)

        if process.returncode != 0:
            print(f"‼ Failed to run program: {cmd}")
            build.cancel("Failed to capture VC environment")

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

        build_dir = build.opt("build_dir", expand=True) or build.pref(
            "cmake_build_dir", "build"
        )

        build_type = build.opt("build_type") or build.pref(
            "cmake_build_type", "Release"
        )

        if mode.startswith("generate"):
            build.cmd.appendleft(
                "cmake", ".", "-B", build_dir, f"-DCMAKE_BUILD_TYPE={build_type}"
            )

            if params := build.prefx("cmake_parameters"):
                build.cmd.append(*params)

            build.file_regex = r"CMake Error at (.+?):(\d+) (.*):"

            if mode.endswith("-clean"):
                build.initializer = lambda _: shutil.rmtree(
                    Path(build.working_dir) / build_dir, ignore_errors=True
                )

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
                build.opt("build_target") or build.pref("cmake_default_target"),
                split=";",
            )

            build.cmd = Cmd(cmd)

            if build_targets:
                build.cmd.append("--target", *build_targets)
                build.cmd.preview = f"cmake --target {' '.join(build_targets)}"

        stdout_replace = build.opt("stdout_replace") or build.pref(
            "cmake_stdout_replace", {}
        )

        stderr_replace = build.opt("stderr_replace") or build.pref(
            "cmake_stderr_replace", {}
        )

        if RUNNING_ON_WINDOWS:
            stdout_replace[f"{build.working_dir}\\".replace("\\", r"[/\\]")] = ""
            stdout_replace[r" \[[^\[]+\.vcxproj\]"] = ""
        else:
            stderr_replace[re.escape(f"{build.working_dir}/")] = ""
            stderr_replace[r"^g?make(?:\[\d+\])?:.*"] = ""

        if stdout_replace or stderr_replace:
            build.listener = CmakeBuildListener(stdout_replace, stderr_replace)

        if RUNNING_ON_WINDOWS:
            build.file_regex = r"^\s*(.+?)\((\d+),?(\d+)\): *(.*)"
            build.syntax = "MSVC Output"

            build.cmd.append("--config", build_type)
        else:
            build.file_regex = r"^([\w\./ -]+?):(\d+):(?:(\d+):)? (.*)"
            build.syntax = "GCC Output"


class CmakeBuildListener(ChimneyBuildListener):
    def __init__(self, stdout_replace, stderr_replace):
        self.output_patterns = [
            (re.compile(key), val) for key, val in stdout_replace.items()
        ]
        self.error_patterns = [
            (re.compile(key), val) for key, val in stderr_replace.items()
        ]

    def on_line(self, line, patterns):
        if len(line) == 0:
            return ""

        for pat, repl in patterns:
            line = pat.sub(repl, line)

        return line if len(line) > 0 else None

    def on_output(self, line, ctx):
        return self.on_line(line, self.output_patterns)

    def on_error(self, line, ctx):
        return self.on_line(line, self.error_patterns)
