import subprocess

import sublime
from sublime import Region
from sublime_plugin import TextCommand, WindowCommand

from . import find_in_file_parents, indent_params, view_cwd


class Formatter:
    def __init__(self, scope, cmdline):
        self.scopes = (scope,)
        self.cmdline = cmdline

    def supported_scopes(self):
        return self.scopes

    def cmd(self, _view, _scope):
        return self.cmdline


class Prettier:
    PARSERS = {
        "source.json": "json",
        "source.js": "babel",
        "source.css": "css",
        "source.yaml": "yaml",
        "text.html.markdown": "markdown",
        "text.html": "html",
    }

    def supported_scopes(self):
        return self.PARSERS

    def cmd(self, view, scope):
        parser = self.PARSERS[scope]
        config = find_in_file_parents(view, ".prettierrc")

        cmd = ["prettier", f"--parser={parser}"]

        if not config:
            if parser == "markdown":
                cmd += ["--prose-wrap=always", "--print-width=100"]
            else:
                use_tabs, tab_width = indent_params(view)
                cmd += [f"--use-tabs={use_tabs}", f"--tab-width={tab_width}"]

        return " ".join(cmd)


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
        config = find_in_file_parents(view, ".clang-format")

        cmd = ["clang-format", f"--assume-filename={self.FILES[scope]}"]

        if not config:
            _, tab_width = indent_params(view)
            cmd.append(f'-style="{{BasedOnStyle: Google, IndentWidth: {tab_width}}}"')

        return " ".join(cmd)


def prepare_formatters(*formatters):
    mapping = {}

    for formatter in formatters:
        for scope in formatter.supported_scopes():
            mapping[scope] = formatter

    return mapping


class FmtCommand(WindowCommand):
    FORMATTERS = prepare_formatters(
        Prettier(),
        ClangFormat(),
        Formatter("source.rust", "rustfmt"),
        Formatter("source.python", "isort - | black -"),
        Formatter("source.cmake", "cmake-format -"),
        Formatter("source.go", "gofmt"),
        Formatter("source.shell.bash", "shfmt -ci -"),
        Formatter("text.xml", "xmlstarlet fo -"),
    )

    def run(self):
        view = self.window.active_view()
        scopes = view.scope_name(0).split()

        for scope in scopes:
            if formatter := self.FORMATTERS.get(scope):
                self.reformat(formatter, view, scope)
                return

        self.window.status_message("No supported formatter")

    def reformat(self, formatter, view, scope):
        text = view.substr(Region(0, view.size()))

        def run_formatter():
            process = subprocess.run(
                formatter.cmd(view, scope),
                input=text,
                encoding="utf-8",
                capture_output=True,
                shell=True,
                cwd=view_cwd(view),
            )

            if process.returncode == 0:
                view.run_command("replace_with_formatted", {"text": process.stdout})
            else:
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
