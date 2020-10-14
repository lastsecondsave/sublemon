import os
import tempfile
from pathlib import Path

import sublime
from sublime_plugin import WindowCommand


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

        if len(parts) > 1 and (root := parts[0]) in "~@#":
            if root == "~":
                root = Path.home()
            elif root == "@":
                root = self.find_parent_folder()
            elif root == "#":
                root = tempfile.gettempdir()

            return Path(root, *parts[1:])

        root = Path(self.window.active_view().file_name()).parent
        return Path(root, path)

    def find_parent_folder(self):
        folders = self.window.folders()

        active_file = self.window.active_view().file_name()
        if not active_file:
            return folders[0]

        active_file = Path(active_file)

        for folder in reorder(folders):
            if folder in active_file.parents:
                return folder

        return folders[0]


class ShowFilePathCommand(WindowCommand):
    def is_enabled(self):
        return bool(self.window.active_view().file_name())

    def run(self):
        path = Path(self.window.active_view().file_name())

        (prefix, path) = self.split(path)

        if prefix:
            path = Path(prefix, path)

        sublime.status_message((" / ").join(path.parts))

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


def reorder(folders):
    return (Path(f) for f in sorted(folders, key=len, reverse=True))
