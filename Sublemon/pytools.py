import os
import re
from pathlib import Path

from . import RUNNING_ON_WINDOWS, pref, project_pref
from .chimney import ChimneyBuildListener, ChimneyCommand

DEFAULT_BINARY = "python" if RUNNING_ON_WINDOWS else "python3"
VENV_BIN = "Scripts" if RUNNING_ON_WINDOWS else "bin"


def setup_python_exec(build, module=None, allow_venv=True):
    if module := build.opt("module") or module:
        build.cmd.appendleft("-m", module)

    binary = DEFAULT_BINARY

    if allow_venv and (venv := find_venv(build)):
        setup_venv(build, venv)
    else:
        key = "python_binary"
        binary = project_pref(build.window, key) or pref(key, DEFAULT_BINARY)

    build.cmd.appendleft(binary)

    build.env["PYTHONIOENCODING"] = "utf-8"
    build.env["PYTHONUNBUFFERED"] = "1"


def find_venv(build):
    if build.opt("allow_venv") is False:
        return None

    if venv := project_pref(build.window, "python_venv"):
        return venv

    for folder in build.window.folders():
        venv = Path(folder, ".venv")
        if venv.is_dir():
            return str(venv)

    return None


def setup_venv(build, venv):
    build.env["VIRTUAL_ENV"] = venv
    build.env["PYTHONPATH"] = None

    build.env["PATH"] = f"{Path(venv, VENV_BIN)}{os.pathsep}$PATH"
    build.cmd.shell = True

    print(f" Using venv: {venv}")


class PythonCommand(ChimneyCommand):
    def setup(self, build):
        setup_python_exec(build)


class PylintCommand(ChimneyCommand):
    def setup(self, build):
        build.cmd.append("--jobs=0")

        if disable := build.opt("disable"):
            build.cmd.append(f"--disable={','.join(disable)}")

        if pylintrc := build.opt("pylintrc") or project_pref(self.window, "pylintrc"):
            build.cmd.append(f"--rcfile={pylintrc}")

        setup_python_exec(build, "pylint")

        build.file_regex = r"(.+?):(\d+):(\d+): (.*)"
        build.syntax = "Pylint Output"
        build.listener = PylintBuildListener()


class PylintBuildListener(ChimneyBuildListener):
    LINE_PATTERN = re.compile(r"(.+:\d+:)(\d+)(: .*)")

    def __init__(self):
        self.rank = None

    def on_output(self, line, ctx):
        match = self.LINE_PATTERN.match(line)
        if match:
            col = int(match.group(2)) + 1
            line = match.group(1) + str(col) + match.group(3)

        if line.startswith("Your code has been rated at"):
            self.rank = line

        return line

    def on_complete(self, ctx):
        if self.rank:
            ctx.on_complete_message = self.rank
