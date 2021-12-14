import os
import re
import tempfile
from pathlib import Path

import sublime
from sublime_plugin import ListInputHandler, TextCommand, WindowCommand


class OpenFilePathCommand(WindowCommand):
    def run(self):
        self.window.show_input_panel("File Path:", "", self.on_done, None, None)

    def on_done(self, path):
        path = os.path.expandvars(path).strip()
        if not path:
            return

        path = Path(path)
        if not path.is_absolute():
            path = self.expand(path)

        if path.name.endswith("+"):
            path = path.with_name(path.name[:-1])
            path.parent.mkdir(exist_ok=True, parents=True)

        if path.parent.exists():
            self.window.open_file(str(path), sublime.ENCODED_POSITION)
        else:
            sublime.status_message(f'Directory "{path.parent}" doesn\'t exist')

    def expand(self, path):
        parts = path.parts

        if len(parts) > 1 and parts[0] == "~":
            return Path(Path.home(), *parts[1:])

        joined = str(path)

        if joined.startswith("!"):
            return Path(tempfile.gettempdir(), joined[1:])

        if joined.startswith("@"):
            return Path(find_project_folder(self.window), joined[1:])

        root = Path(self.window.active_view().file_name()).parent
        return Path(root, path)


def find_project_folder(window):
    folders = window.folders()

    active_file = window.active_view().file_name()
    if not active_file:
        return folders[0]

    parents = Path(active_file).parents

    for folder in reorder(folders):
        if folder in parents:
            return folder

    return folders[0]


def reorder(folders):
    return (Path(f) for f in sorted(folders, key=len, reverse=True))


class OpenFileUnderCursorCommand(TextCommand):
    PATH_PATTERN_STR = r"([^\s:]+)(?::\d+){0,2}"
    PATH_PATTERN = re.compile(PATH_PATTERN_STR)

    def run(self, edit):
        paths = []
        root = None

        if file_name := self.view.file_name():
            root = Path(file_name).parent

        for region in self.view.sel():
            if path := self.find_path(region):
                if path := self.process_path(path, root):
                    paths.append(path)

        for path in paths:
            self.view.window().open_file(path, sublime.ENCODED_POSITION)

    def find_path(self, region):
        if not region.empty():
            return self.view.substr(region)

        point = self.view.find_by_class(
            region.begin(),
            forward=False,
            classes=sublime.CLASS_WORD_START | sublime.CLASS_LINE_START,
            separators=" ",
        )

        match = self.view.find(self.PATH_PATTERN_STR, point)
        return self.view.substr(match)

    def process_path(self, path, root):
        if not Path(path).is_absolute():
            if not root:
                return None

            path = str(root / path)

        match = self.PATH_PATTERN.match(path)
        if match and Path(match.group(1)).is_file():
            return path

        return None


class ShowFilePathCommand(WindowCommand):
    def is_enabled(self):
        return bool(self.window.active_view().file_name())

    def run(self):
        path = Path(self.window.active_view().file_name())

        (prefix, path) = self.split(path)
        parts = path.parts

        if prefix:
            parts = (prefix,) + parts
        elif parts[0] == "/":
            parts = ("",) + parts[1:]

        sublime.status_message(" / ".join(parts).strip())

    def split(self, path):
        for folder in reorder(self.window.folders()):
            try:
                return ("@" + folder.name, path.relative_to(folder))
            except ValueError:
                pass

        try:
            return ("~", path.relative_to(Path.home()))
        except ValueError:
            return (None, path)


class CopyFilePathCommand(WindowCommand):
    MODES = {
        "file_name": "File Name",
        "file_path": "File Path",
        "file_project_path": "File Project Path",
        "dir_name": "Directory Name",
        "dir_path": "Directory Path",
        "dir_project_path": "Directory Project Path",
    }

    def is_enabled(self):
        return bool(self.window.active_view().file_name())

    def run(self, mode):  # pylint: disable=arguments-differ
        path = Path(self.window.active_view().file_name())

        if mode == "file_name":
            path = path.name
        elif mode == "file_project_path":
            path = self.project_path(path)
        elif mode == "dir_name":
            path = path.parent.name
        elif mode == "dir_path":
            path = path.parent
        elif mode == "dir_project_path":
            path = self.project_path(path.parent)

        if path:
            sublime.set_clipboard(str(path))
            sublime.status_message(f"Copied {self.MODES[mode].lower()}")

    def project_path(self, path):
        if project_file := self.window.project_file_name():
            try:
                return path.relative_to(Path(project_file).parent)
            except ValueError:
                pass

        sublime.status_message("Not in a project")
        return None

    def input(self, _args):
        items = [(val, key) for key, val in self.MODES.items()]

        class ModeInputHandler(ListInputHandler):
            def list_items(self):
                return items

        return ModeInputHandler()
