import configparser
import datetime
import re
from pathlib import Path

import sublime
from sublime_plugin import WindowCommand

from . import (
    active_view_contains_file,
    find_in_parent_directories,
    start_process,
    view_cwd,
)
from .chimney import ChimneyBuildListener, ChimneyCommand


def find_dotgit(window, error_when_not_found=True):
    dotgit = None

    if project_file := window.project_file_name():
        path = Path(project_file).with_name(".git")
        if path.exists():
            dotgit = path

    if not dotgit and (folders := window.folders()):
        path = Path(folders[0]) / ".git"
        if path.exists():
            dotgit = path

    if not dotgit:
        dotgit = find_in_parent_directories(window.active_view(), ".git")

    if not dotgit and error_when_not_found:
        sublime.error_message("Not a git repository.")

    return dotgit


class GitGuiCommand(WindowCommand):
    def run(self):
        if dotgit := find_dotgit(self.window):
            start_process(["git", "gui"], dotgit.parent)


class GitEditExcludeCommand(WindowCommand):
    def run(self):
        if dotgit := find_dotgit(self.window):
            exclude_view = self.window.open_file(str(dotgit / "info" / "exclude"))
            exclude_view.assign_syntax(
                "Packages/Sublemon/syntaxes/Unix Config.sublime-syntax"
            )


class GitRevertFileCommand(WindowCommand):
    def run(self, save=True):  # pylint: disable=arguments-differ
        view = self.window.active_view()

        if view.is_dirty() and save:
            self.window.run_command("save")
            self.window.run_command("git_revert_file", args={"save": False})
            return

        start_process(["git", "checkout", view.file_name()], view_cwd(view))

    def is_enabled(self):
        return active_view_contains_file(self.window)


class GitDiffCommand(ChimneyCommand):
    def setup(self, build):
        build.cmd.append("git", "diff", build.active_file)
        build.syntax = "Packages/Diff/Diff.tmLanguage"

    def is_enabled(self):
        return active_view_contains_file(self.window)


class GitLogCommand(ChimneyCommand):
    def setup(self, build):
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
        build.syntax = "Git Log Output"

    def is_enabled(self):
        return active_view_contains_file(self.window)


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
            "date": reformat_date(match.group(2)),
            "author": match.group(3).strip(),
            "message": match.group(4),
        }

        self.line_infos.append(line_info)
        self.author_width = max(self.author_width, len(line_info["author"]))

        return None

    def on_complete(self, ctx):
        def combine(line_info):
            chunks = [
                line_info["date"],
                line_info["author"].ljust(self.author_width),
                line_info["commit"],
                line_info["message"],
            ]
            return "  ".join(chunks)

        lines = (combine(line_info) for line_info in reversed(self.line_infos))
        ctx.print_lines(lines)

        if self.line_infos:
            ctx.on_complete_message = "Last edited at " + self.line_infos[0]["date"]


def reformat_date(date_string):
    return datetime.date.fromisoformat(date_string).strftime("%d %b %Y")


class GitBlameCommand(ChimneyCommand):
    def setup(self, build):
        build.cmd.append("git", "blame", "--date=short")

        view = self.window.active_view()
        sel = view.sel()[0]

        if not sel.empty():
            from_line = view.rowcol(sel.begin())[0] + 1
            to_line, to_col = view.rowcol(sel.end())
            if to_col > 0:
                to_line += 1

            build.cmd.append("-L", f"{from_line},{to_line}")

        build.cmd.append("--", build.active_file)
        build.syntax = "Git Blame Output"
        build.listener = GitBlameBuildListener()

    def is_enabled(self):
        return active_view_contains_file(self.window)


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
            "date": reformat_date(match.group(4)),
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
                date = line_info["date"]
                author = line_info["author"].ljust(self.author_width)
                commit = line_info["commit"]
                line = f"{date}  {author}  {commit}"
            else:
                line = " " * (len(line_info["commit"]) + self.author_width + 15)

            line += "  " + line_info["line_number"]
            if line_info["code"]:
                line += "  " + line_info["code"][self.code_indent :]

            return line

        ctx.print_lines(combine(line_info) for line_info in self.line_infos)


class GitLineLinkCommand(WindowCommand):
    GIT_URL_PATTERN = re.compile(r"git@(.+):(.+)\.git")

    def run(self):
        dotgit = find_dotgit(self.window)
        if not dotgit:
            return

        config = configparser.ConfigParser()
        config.read(dotgit / "config")

        origin_url = config['remote "origin"']["url"]
        if match := self.GIT_URL_PATTERN.match(origin_url):
            origin_url = f"https://{match.group(1)}/{match.group(2)}"

        view = self.window.active_view()
        file_path = "/".join(Path(view.file_name()).relative_to(dotgit.parent).parts)

        lines, lines_desc = self.lines_string()

        sublime.set_clipboard(f"{origin_url}/blob/master/{file_path}#{lines}")
        sublime.status_message(f"Copied URL to {lines_desc}")

    def lines_string(self):
        view = self.window.active_view()
        region = view.sel()[0]

        begin = view.rowcol(region.begin())[0] + 1
        end = view.rowcol(region.end())[0] + 1

        if begin != end and view.rowcol(region.end())[1] == 0:
            end -= 1

        if begin == end:
            return f"L{begin}", f"line {begin}"

        return f"L{begin}-L{end}", f"lines {begin}-{end}"

    def is_enabled(self):
        return active_view_contains_file(self.window)
