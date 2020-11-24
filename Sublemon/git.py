import re
import subprocess
from pathlib import Path

from sublime_plugin import WindowCommand

from . import find_in_file_parents, view_cwd
from .chimney import ChimneyBuildListener, ChimneyCommand

NOT_A_GIT_REPOSITORY = "Not a git repository"


class GitGuiCommand(WindowCommand):
    def run(self):
        dotgit = find_in_file_parents(self.window.active_view(), ".git")
        if dotgit:
            subprocess.Popen("git gui", cwd=dotgit.parent, shell=True)
        else:
            self.window.status_message(NOT_A_GIT_REPOSITORY)


class GitEditExcludeCommand(WindowCommand):
    def run(self):
        process = subprocess.run(
            "git rev-parse --show-toplevel",
            encoding="utf-8",
            capture_output=True,
            shell=True,
            cwd=view_cwd(self.window.active_view()),
        )

        if process.returncode != 0:
            self.window.status_message(NOT_A_GIT_REPOSITORY)
            return

        path = Path(process.stdout.strip(), ".git", "info", "exclude")
        exclude_view = self.window.open_file(str(path))
        exclude_view.set_syntax_file(
            "Packages/Sublemon/syntaxes/unix_config.sublime-syntax"
        )


class GitDiffCommand(ChimneyCommand):
    def setup(self, build):
        if not build.active_file:
            build.cancel("No file")

        build.cmd.append("git", "diff", build.active_file)
        build.syntax = "Packages/Diff/Diff.tmLanguage"


class GitLogCommand(ChimneyCommand):
    def setup(self, build):
        if not build.active_file:
            build.cancel("No file")

        build.cmd.append(
            "git",
            "log",
            "-200",
            "--follow",
            "--no-merges",
            "--date=short",
            "--format=%h %ad %an → %s",
            "--",
            build.active_file,
        )

        build.listener = GitLogBuildListener()
        build.syntax = "git_log"


class GitLogBuildListener(ChimneyBuildListener):
    LINE_PATTERN = re.compile(r"([0-9a-z]+) (\d{4}-\d{2}-\d{2}) (.*) → (.*)")

    def __init__(self):
        self.line_infos = []
        self.author_width = 0

    def on_output(self, line, ctx):
        match = self.LINE_PATTERN.match(line)
        if not match:
            return None

        line_info = {
            "commit": match.group(1),
            "date": match.group(2),
            "author": match.group(3).strip(),
            "message": match.group(4),
        }

        self.line_infos.append(line_info)
        self.author_width = max(self.author_width, len(line_info["author"]))

        return None

    def on_complete(self, ctx):
        def combine(line_info):
            pieces = (
                line_info["date"],
                line_info["author"].ljust(self.author_width),
                line_info["commit"],
                line_info["message"],
            )
            return " ".join(pieces)

        lines = (combine(line_info) for line_info in reversed(self.line_infos))
        ctx.print_lines(lines)

        if self.line_infos:
            ctx.window.status_message("Last edited at " + self.line_infos[0]["date"])


class GitBlameCommand(ChimneyCommand):
    def setup(self, build):
        if not build.active_file:
            build.cancel("No file")

        build.cmd.append("git", "blame", "--date=short")

        view = self.window.active_view()
        sel = view.sel()[0]

        if not sel.empty():
            from_line = view.rowcol(sel.begin())[0] + 1
            to_line, to_col = view.rowcol(sel.end())
            if to_col > 0:
                to_line += 1

            build.cmd.append("-L", "{},{}".format(from_line, to_line))

        build.cmd.append("--", build.active_file)
        build.syntax = "git_blame"
        build.listener = GitBlameBuildListener()


class GitBlameBuildListener(ChimneyBuildListener):
    LINE_PATTERN = re.compile(
        r"([0-9a-z]+) (.*?)\((.+?) (\d{4}-\d{2}-\d{2}) (\s*\d+)\) (.*)"
    )

    def __init__(self):
        self.line_infos = []
        self.code_indent = 999
        self.author_width = 0

    def on_output(self, line, ctx):
        match = self.LINE_PATTERN.match(line)
        if not match:
            return None

        line_info = {
            "commit": match.group(1),
            "author": match.group(3).strip(),
            "date": match.group(4),
            "line_number": match.group(5),
            "code": match.group(6),
            "not_committed": match.group(3) == "Not Committed Yet",
        }

        self.line_infos.append(line_info)

        if line_info["code"]:
            code = line_info["code"]
            self.code_indent = min(self.code_indent, len(code) - len(code.lstrip()))

        if not line_info["not_committed"]:
            self.author_width = max(self.author_width, len(line_info["author"]))

        return None

    def on_complete(self, ctx):
        def combine(line_info):
            if not line_info["not_committed"]:
                pieces = [
                    line_info["date"],
                    line_info["author"].ljust(self.author_width),
                    line_info["commit"],
                ]
                line = " ".join(pieces)
            else:
                line = " " * (len(line_info["commit"]) + self.author_width + 12)

            line += "   " + line_info["line_number"]
            if line_info["code"]:
                line += " " + line_info["code"][self.code_indent :]

            return line

        ctx.print_lines(combine(line_info) for line_info in self.line_infos)
