import os
import tempfile

import sublime
from sublime_plugin import WindowCommand

from . import RUNNING_ON_WINDOWS

HOME_PATH = os.path.expanduser('~')


class OpenFilePathCommand(WindowCommand):
    def on_done(self, path):
        path = os.path.expandvars(path).strip()

        if RUNNING_ON_WINDOWS:
            path = path.replace('/', '\\')

        root = path[0] if len(path) > 1 and path[1] == os.sep else None

        if root == '~':
            root = HOME_PATH
        elif root == '@':
            root = self.window.folders()[0]
        elif root == '#':
            root = tempfile.gettempdir()

        if root:
            path = root + path[1:]

        parent = os.path.dirname(path) or '.'
        parent_exists = os.path.exists(parent)

        if path.endswith('+'):
            path = path[:-1]
            if not parent_exists:
                os.makedirs(parent)
                parent_exists = True

        if parent_exists:
            self.window.open_file(path, sublime.ENCODED_POSITION)
        else:
            sublime.status_message("Directory " + parent + " doesn't exist")

    def run(self):
        self.window.show_input_panel("File Path:", '', self.on_done, None, None)
        self.window.status_message("@ - project, # - temp")
