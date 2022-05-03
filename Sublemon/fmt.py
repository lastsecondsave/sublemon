import subprocess

import sublime
from sublime import Region
from sublime_plugin import TextCommand

from . import (
    POPEN_CREATION_FLAGS,
    RUNNING_ON_LINUX,
    RUNNING_ON_WINDOWS,
    find_in_parent_directories,
    indent_params,
    sad_message,
    view_cwd,
)


class Formatter:
    def __init__(self, scope, command, shell=False, windows=None, linux=None):
        self.scopes = (scope,)
        self.shell = shell

        if RUNNING_ON_WINDOWS and windows:
            self.command = windows
        elif RUNNING_ON_LINUX and linux:
            self.command = linux
        else:
            self.command = command

    def supported_scopes(self):
        return self.scopes

    def cmd(self, _view, _scope):
        return (self.command, self.shell)


class Prettier:
    FILES = {
        "source.json": "file.json",
        "source.js": "file.js",
        "source.css": "file.css",
        "source.yaml": "file.yaml",
        "text.html.markdown": "file.md",
        "text.html.basic": "file.html",
    }

    def supported_scopes(self):
        return self.FILES

    def cmd(self, view, scope):
        config = find_in_parent_directories(view, ".prettierrc", ".prettierrc.json")

        binary = "prettier.cmd" if RUNNING_ON_WINDOWS else "prettier"
        cmd = [binary, f"--stdin-filepath={self.FILES[scope]}"]

        if not config:
            if scope == "text.html.markdown":
                cmd += ["--prose-wrap=always", "--print-width=88"]
            else:
                use_tabs, tab_width = indent_params(view)
                cmd += [f"--use-tabs={use_tabs}", f"--tab-width={tab_width}"]
        else:
            cmd.append(f"--config={config}")

        return (cmd, False)


class ClangFormat:
    FILES = {
        "source.c": "file.c",
        "source.c++": "file.cpp",
        "source.java": "file.java",
        "source.objc": "file.m",
        "source.objc++": "file.mm",
    }

    def supported_scopes(self):
        return self.FILES

    def cmd(self, view, scope):
        cmd = ["clang-format", f"--assume-filename={self.FILES[scope]}"]
        config = None

        if scope != "source.java":
            config = find_in_parent_directories(view, ".clang-format")

        if not config:
            style = ", ".join(self.generate_style(view, scope))
            cmd.append(f"--style={{{style}}}")

        return (cmd, False)

    def generate_style(self, view, scope):
        _, tab_width = indent_params(view)

        common = [
            "ColumnLimit: 88",
            f"IndentWidth: {tab_width}",
            f"ContinuationIndentWidth: {tab_width * 2}",
        ]

        if scope == "source.java":
            return common + [
                "BreakAfterJavaFieldAnnotations: true",
                "AllowShortFunctionsOnASingleLine: Empty",
                "AllowShortIfStatementsOnASingleLine: Never",
                "AllowShortLoopsOnASingleLine: false",
                "AlignAfterOpenBracket: false",
                "AlignOperands: DontAlign",
                "AllowAllArgumentsOnNextLine: true",
            ]

        return common + [
            "BasedOnStyle: Google",
            "IncludeBlocks: Preserve",
            "KeepEmptyLinesAtTheStartOfBlocks: true",
        ]


class CMakeFormat:
    def supported_scopes(self):
        return ("source.cmake",)

    def cmd(self, view, scope):
        config = find_in_parent_directories(view, ".cmake-format")

        cmd = ["cmake-format", "-"]

        if not config:
            _, tab_width = indent_params(view)
            cmd += [
                "--line-width=88",
                f"--tab-size={tab_width}",
                "--enable-markup=false",
                "--max-subgroups-hwrap=3",
            ]

        return (cmd, False)


def prepare_formatters(*formatters):
    mapping = {}

    for formatter in formatters:
        for scope in formatter.supported_scopes():
            mapping[scope] = formatter

    return mapping


class FmtCommand(TextCommand):
    FORMATTERS = prepare_formatters(
        Prettier(),
        ClangFormat(),
        CMakeFormat(),
        Formatter("source.rust", "rustfmt"),
        Formatter("source.python", "isort --profile black - | black -", shell=True),
        Formatter("source.go", "goimports"),
        Formatter("source.shell.bash", ["shfmt", "-ci", "-sr", "-"]),
        Formatter("text.xml", ["xmlstarlet", "fo", "-"], windows=["xml", "fo", "-"]),
    )

    def run(self, edit):
        scopes = self.view.scope_name(0).split()[:3]

        for scope in scopes:
            if formatter := self.FORMATTERS.get(scope):
                self.reformat(formatter, scope)
                return

        self.view.window().status_message("No supported formatter")

    def reformat(self, formatter, scope):
        original_text = self.view.substr(Region(0, self.view.size()))

        def run_formatter():
            cmd, shell = formatter.cmd(self.view, scope)

            process = subprocess.run(
                cmd,
                input=original_text,
                encoding="utf-8",
                capture_output=True,
                shell=shell,
                cwd=view_cwd(self.view),
                creationflags=POPEN_CREATION_FLAGS,
            )

            if process.returncode == 0:
                replacement = process.stdout
                self.view.run_command("replace_with_formatted", {"text": replacement})
            else:
                sad_message(f"Failed to run program: {cmd}")
                sublime.error_message(process.stderr.strip())

        sublime.set_timeout_async(run_formatter, 0)


class ReplaceWithFormattedCommand(TextCommand):
    # pylint: disable=arguments-differ
    def run(self, edit, text):
        viewport = self.view.viewport_position()

        region = Region(0, self.view.size())
        self.view.replace(edit, region, text)

        self.view.set_viewport_position((0, 0), False)
        self.view.set_viewport_position((0, viewport[1]), False)
