import re
import subprocess
from timeit import default_timer as timer

import sublime
from sublime import Region
from sublime_plugin import TextCommand

from . import (
    POPEN_CREATION_FLAGS,
    RUNNING_ON_LINUX,
    RUNNING_ON_WINDOWS,
    indent_params,
    locate_config,
    pref,
    view_cwd,
)


class BasicFormatter:
    def error(self, message):
        return message


class Formatter(BasicFormatter):
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


class Prettier(BasicFormatter):
    ERROR_FILTER = re.compile(r".+: SyntaxError: ")
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
        config = locate_config(view, ".prettierrc", ".prettierrc.json")

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

    def error(self, message):
        return self.ERROR_FILTER.sub("", message)


class ClangFormat(BasicFormatter):
    FILES = {
        "source.c": "file.c",
        "source.c++": "file.cpp",
        "source.objc": "file.m",
        "source.objc++": "file.mm",
    }

    def supported_scopes(self):
        return self.FILES

    def cmd(self, view, scope):
        cmd = ["clang-format", f"--assume-filename={self.FILES[scope]}"]
        config = locate_config(view, ".clang-format")

        if not config:
            style = ", ".join(self.generate_style(view, scope))
            cmd.append(f"--style={{{style}}}")

        return (cmd, False)

    def generate_style(self, view, _scope):
        _, tab_width = indent_params(view)

        return [
            "BasedOnStyle: Google",
            "ColumnLimit: 88",
            f"IndentWidth: {tab_width}",
            f"ContinuationIndentWidth: {tab_width * 2}",
            "IncludeBlocks: Preserve",
            "KeepEmptyLinesAtTheStartOfBlocks: true",
            "AllowShortFunctionsOnASingleLine: Empty",
            "PointerAlignment: Left",
            "DerivePointerAlignment: false",
            f"AccessModifierOffset: -{1 if tab_width == 2 else tab_width}",
        ]


class CMakeFormat(BasicFormatter):
    def supported_scopes(self):
        return ("source.cmake",)

    def cmd(self, view, _scope):
        config = locate_config(view, ".cmake-format", ".cmake-format.json")

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


class PythonFormat(BasicFormatter):
    ERROR_FILTER = re.compile(r"\s+Oh no.+reformat\.", flags=re.DOTALL)

    def supported_scopes(self):
        return ("source.python",)

    def cmd(self, view, _scope):
        use_isort = pref("fmt_isort", True, view=view)

        if use_isort:
            return ("isort --profile black - | black -", True)

        return (["black", "-"], False)

    def error(self, message):
        message = message.replace("error: cannot format -: ", "")
        return self.ERROR_FILTER.sub("", message)


class JavaFormat(BasicFormatter):
    def supported_scopes(self):
        return ("source.java",)

    def cmd(self, view, _scope):
        google_java_format_jar = pref("google_java_format_jar", view=view)

        return (
            ["java", "-jar", google_java_format_jar, "-a", "-"],
            False,
        )


class GoFormat(Formatter):
    def __init__(self):
        super().__init__("source.go", "goimports")

    def error(self, message):
        return message.replace("<standard input>:", "")


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
        PythonFormat(),
        JavaFormat(),
        GoFormat(),
        Formatter("source.rust", "rustfmt"),
        Formatter("source.cs", ["dotnet", "csharpier"]),
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
            start_time = timer()

            process = subprocess.run(
                cmd,
                input=original_text,
                encoding="utf-8",
                capture_output=True,
                shell=shell,
                cwd=view_cwd(self.view),
                creationflags=POPEN_CREATION_FLAGS,
            )

            if process.returncode != 0:
                print(f"‼ Formatter exited with error: {cmd}")
                sublime.error_message(formatter.error(process.stderr.strip()))
                return

            self.view.run_command("replace_view_content", {"text": process.stdout})

            time_taken = round((timer() - start_time) * 1000, 2)
            self.view.window().status_message(f"Formatted in {time_taken} ms")

        sublime.set_timeout_async(run_formatter, 0)


class ReplaceViewContentCommand(TextCommand):
    # pylint: disable=arguments-differ
    def run(self, edit, text):
        region = Region(0, self.view.size())
        self.view.replace(edit, region, text)
