import os
import tempfile

import sublime
from sublime_plugin import WindowCommand

from . import RUNNING_ON_WINDOWS

HOME_PATH = os.path.expanduser('~')


class ShowFilePathCommand(WindowCommand):
    def run(self):
        file_path = self.window.active_view().file_name()
        if not file_path:
            return

        prefix = None
        variables = self.window.extract_variables()

        def path_starts_with(path, prefix):
            return path.startswith(prefix + os.sep)

        if 'project' in variables:
            settings = self.window.project_data().get('settings', {})
            base_path = settings.get("project_root", variables["project_path"])

            if path_starts_with(file_path, base_path):
                file_path = file_path[len(base_path)+1:]
                prefix = variables["project_base_name"]

        if not prefix:
            if path_starts_with(file_path, HOME_PATH):
                file_path = file_path[len(HOME_PATH)+1:]
                prefix = "~"
            elif RUNNING_ON_WINDOWS:
                prefix = file_path[0:2].lower()
                file_path = file_path[3:]
            else:
                prefix = "/"
                file_path = file_path[1:]

        sublime.status_message('{} / {}'.format(prefix, file_path.replace(os.sep, ' / ')))


class OpenFilePathCommand(WindowCommand):
    def on_done(self, path):
        path = os.path.expandvars(path).strip()

        if RUNNING_ON_WINDOWS:
            path = path.replace('/', '\\')

        root = path[0] if len(path) > 1 and path[1] == os.sep else None

        if root == '~':
            root = HOME_PATH
        elif root == '@':
            root = self.window.extract_variables().get('folder')
        elif root == '#':
            root = tempfile.gettempdir()

        if root:
            path = root + path[1:]

        open_file = True

        parent = os.path.dirname(path)
        if (parent and not os.path.exists(parent)):
            open_file = sublime.ok_cancel_dialog("Directory doesn't exist: {}".format(parent),
                                                 "Create")
            if open_file:
                os.makedirs(parent)

        if open_file:
            self.window.open_file(path, sublime.ENCODED_POSITION)

    def run(self):
        self.window.show_input_panel("File Name:", '', self.on_done, None, None)


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
