import os
import tempfile

import sublime
from sublime_plugin import WindowCommand

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

        if not prefix:
            if file_path.startswith(HOME_PATH + os.sep):
                file_path = file_path[len(HOME_PATH):]
                prefix = "~"

        sublime.status_message((prefix + file_path).replace(os.sep, ' / '))


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

        open_file = True

        parent = os.path.dirname(path)
        if parent and not os.path.exists(parent):
            open_file = sublime.ok_cancel_dialog("Directory doesn't exist: {}".format(parent),
                                                 "Create")
            if open_file:
                os.makedirs(parent)

        if open_file:
            self.window.open_file(path, sublime.ENCODED_POSITION)

    def run(self):
        self.window.show_input_panel("File Path:", '', self.on_done, None, None)


class SelectWithCustomMarkersCommand(WindowCommand):
    def run(self):
        self.window.show_input_panel(
            'Selection markers:', '', self.on_done, None, None)

    def on_done(self, markers):
        self.window.active_view().run_command(
            'select_with_markers', self.split_markers(markers))

    @staticmethod
    def split_markers(markers):
        i = markers.find(' ')

        left_bound = i if i >= 0 else int(len(markers) / 2)
        right_bound = i + 1 if i >= 0 else left_bound

        return {'left': markers[:left_bound], 'right': markers[right_bound:]}


class CloseWithoutSavingCommand(WindowCommand):
    def run(self):
        view = self.window.active_view()
        view.set_scratch(True)
        view.close()
