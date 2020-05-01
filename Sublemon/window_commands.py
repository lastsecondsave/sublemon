import os
import tempfile

import sublime
from sublime_plugin import TextInputHandler, WindowCommand

from . import RUNNING_ON_WINDOWS

HOME_PATH = os.path.expanduser('~')


class ShowFilePathCommand(WindowCommand):
    def is_enabled(self):
        return bool(self.window.active_view().file_name())

    def run(self):
        file_path = self.window.active_view().file_name()
        variables = self.window.extract_variables()

        prefix = None

        if 'project' in variables:
            project_path = variables['project_path']

            if file_path.startswith(project_path + os.sep):
                file_path = file_path[len(project_path):]
                prefix = variables['project_base_name']

        if not prefix and file_path.startswith(HOME_PATH + os.sep):
            file_path = file_path[len(HOME_PATH):]
            prefix = "~"

        file_path = prefix + file_path if prefix else file_path
        sublime.status_message(file_path.replace(os.sep, ' / '))


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


class CloseWithoutSavingCommand(WindowCommand):
    def run(self):
        view = self.window.active_view()
        view.set_scratch(True)
        view.close()


class WrapLinesAtWidthCommand(WindowCommand):
    def run(self, width):
        self.window.run_command("wrap_lines", {"width": int(width)})

    def input(self, _args):
        class WidthInputHandler(TextInputHandler):
            def placeholder(self):
                return "Width"

        return WidthInputHandler()
