import os
import re

import sublime
from sublime import Region
from sublime_plugin import ApplicationCommand, TextCommand, WindowCommand

import Sublemon.lib.util as util


class EscapeBackslashesCommand(TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            self.escape(edit, region.end())

    def escape(self, edit, point):
        def score(p): return self.view.score_selector(p, 'string')

        if not score(point):
            return

        begin = point
        while score(begin - 1):
            begin -= 1

        end = point + 1
        while score(end):
            end += 1

        region = Region(begin, end)
        content = self.view.substr(region)
        initial_content_length = len(content)

        content = content.replace('\\', '\\\\')
        if len(content) > initial_content_length:
            self.view.replace(edit, region, content)


class ShrinkWhitespaceCommand(util.RegionCommand):
    EMPTY_LINE_PATTERN = re.compile(r'\s*$')

    def process_region(self, edit, region):
        selection = self.view.sel()
        selection.subtract(region)

        point = self.shrink_spaces(edit, region.end())
        selection.add(Region(point, point))

    def shrink_spaces(self, edit, point):
        def is_space(p):
            return self.view.substr(p) == ' '

        begin = point
        while is_space(begin - 1):
            begin -= 1

        end = point
        while is_space(end):
            end += 1

        if end - begin < 2:
            return point

        self.view.replace(edit, Region(begin, end), ' ')
        return begin + 1


class ShowFilePathCommand(WindowCommand):
    def run(self):
        file_path = self.window.active_view().file_name()
        if not file_path:
            return

        prefix = None
        variables = self.window.extract_variables()

        if 'project' in variables:
            settings = self.window.project_data().get('settings', {})
            base_path = settings.get("project_root", variables["project_path"])

            if file_path.startswith(base_path + os.sep):
                file_path = file_path[len(base_path)+1:]
                prefix = variables["project_base_name"]

        if not prefix:
            home_path = (os.environ['HOME'] if not util.RUNNING_ON_WINDOWS
                         else os.environ['HOMEDRIVE'] + os.environ['HOMEPATH'])

            if file_path.startswith(home_path + os.sep):
                file_path = file_path[len(home_path)+1:]
                prefix = "~"
            elif util.RUNNING_ON_WINDOWS:
                prefix = file_path[0:2].lower()
                file_path = file_path[3:]
            else:
                prefix = "/"
                file_path = file_path[1:]

        sublime.status_message('({}) → {}'.format(
            prefix, file_path.replace(os.sep, ' → ')))


class ToggleIndentGuidesCommand(TextCommand):
    def run(self, edit):
        guides = self.view.settings().get("indent_guide_options")
        guides = [] if guides else ["draw_normal"]
        self.view.settings().set("indent_guide_options", guides)


class ToggleDrawCenteredCommand(ApplicationCommand):
    def run(self):
        s = sublime.load_settings("Preferences.sublime-settings")
        current = s.get("draw_centered", False)
        s.set("draw_centered", not current)
        sublime.save_settings("Preferences.sublime-settings")

    def is_checked(self):
        s = sublime.load_settings("Preferences.sublime-settings")
        return s.get("draw_centered", False)


class OpenFilePathCommand(WindowCommand):
    def run(self):
        def on_done(x):
            self.window.open_file(x.strip(), sublime.ENCODED_POSITION)
        self.window.show_input_panel("File Name:", '', on_done, None, None)
