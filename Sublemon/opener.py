import os
import tempfile
from pathlib import Path

import sublime
from sublime_plugin import WindowCommand


class OpenFilePathCommand(WindowCommand):
    def run(self):
        self.window.status_message("@ - project, # - temp")
        self.window.show_input_panel("File Path:", '', self.on_done, None, None)

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
            sublime.status_message(f"Directory \"{path.parent}\" doesn't exist")

    def expand(self, path: Path) -> Path:
        parts = path.parts

        if len(parts) > 1 and (root := parts[0]) in "~@#":
            if root == '~':
                root = Path.home()
            elif root == '@':
                root = self.window.folders()[0]
            elif root == '#':
                root = tempfile.gettempdir()

            return Path(root, *parts[1:])

        root = Path(self.window.active_view().file_name()).parent
        return Path(root, path)
