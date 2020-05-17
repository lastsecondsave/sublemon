import subprocess

from sublime import Region
from sublime_plugin import TextCommand

from . import find_in_file_parents, indent_params, view_cwd


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
            use_tabs, tab_width = indent_params(view)
            cmd += [f"--use-tabs={use_tabs}", f"--tab-width={tab_width}"]

            if parser == "markdown":
                cmd += ["--prose-wrap=always", "--print-width=100"]

        return cmd


def matched_scope(view, scopes):
    matched = (scope for scope in scopes if view.match_selector(0, scope))
    return next(matched, None)


class FmtCommand(TextCommand):
    FORMATTERS = (
        Prettier(),
        Formatter("source.rust", "rustfmt"),
        Formatter("source.python", "black -"),
    )

    def run(self, edit):
        for formatter in self.FORMATTERS:
            if formatter.match(self.view):
                self.run_formatter(edit, formatter.cmd(self.view))
                return

        self.status_message("No supported formatter")

    def status_message(self, message):
        self.view.window().status_message(message)

    def run_formatter(self, edit, cmd):
        region = Region(0, self.view.size())
        process = subprocess.run(
            cmd,
            input=self.view.substr(region),
            encoding="utf-8",
            capture_output=True,
            shell=True,
            cwd=view_cwd(self.view),
        )

        if process.returncode != 0:
            self.log_error(cmd, process)
            return

        self.view.replace(edit, region, process.stdout)

    def log_error(self, cmd, process):
        self.status_message("Formatter exited with error")

        print("Formatter:", cmd)
        print(f"{'-'*12}stderr{'-'*12}")
        print(process.stderr.strip())
        print("-" * 30)
