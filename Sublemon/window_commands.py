import os

import sublime
from sublime_plugin import TextInputHandler, WindowCommand

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
