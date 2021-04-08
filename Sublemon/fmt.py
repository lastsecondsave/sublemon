import subprocess

import sublime
from sublime import Region
from sublime_plugin import TextCommand, WindowCommand

from . import RUNNING_ON_WINDOWS, find_in_file_parents, indent_params, view_cwd


class Formatter:
    def __init__(self, scope=None, cmdline=None):
        self.scope = scope
        self.cmdline = cmdline

    def match(self, view):
        return view.match_selector(0, self.scope) > 0

    # pylint: disable=unused-argument
    def cmd(self, view):
        return self.cmdline


class Prettier(Formatter):
    PARSERS = {
        "source.json": "json",
        "source.js": "babel",
        "source.css": "css",
        "source.yaml": "yaml",
        "text.html.markdown": "markdown",
        "text.html": "html",
    }

    def match(self, view):
        return bool(matched_scope(view, self.PARSERS))

    def cmd(self, view):
        scope = matched_scope(view, self.PARSERS)
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


class ClangFormat(Formatter):
    SCOPES = ("source.c++", "source.c", "source.java", "source.objc", "source.objc++")

    def match(self, view):
        return bool(matched_scope(view, self.SCOPES))

    def cmd(self, view):
        scope = matched_scope(view, self.SCOPES)
        config = find_in_file_parents(view, ".clang-format")

        filename = scope if not "objc" in scope else "source.mm"
        cmd = ["clang-format", f"--assume-filename={filename}"]

        if not config:
            _, tab_width = indent_params(view)
            cmd.append(f'-style="{{BasedOnStyle: Google, IndentWidth: {tab_width}}}"')

        return " ".join(cmd)


def matched_scope(view, scopes):
    matched = (scope for scope in scopes if view.match_selector(0, scope))
    return next(matched, None)


class FmtCommand(WindowCommand):
    FORMATTERS = (
        Prettier(),
        ClangFormat(),
        Formatter("source.rust", "rustfmt"),
        Formatter("source.python", "isort - | black -"),
        Formatter("source.cmake", "cmake-format -"),
        Formatter("text.xml", "xmlstarlet fo -"),
    )

    def run(self):
        view = self.window.active_view()

        for formatter in self.FORMATTERS:
            if formatter.match(view):
                self.reformat(formatter, view)
                return

        self.window.status_message("No supported formatter")

    def reformat(self, formatter, view):
        text = view.substr(Region(0, view.size()))

        def run_formatter():
            process = subprocess.run(
                formatter.cmd(view),
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
        region = Region(0, self.view.size())
        self.view.replace(edit, region, text)
