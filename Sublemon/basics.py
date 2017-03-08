import os
import re
import sublime
import sublime_plugin
import sys

class SublemonDemoCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        selection = self.view.sel()
        view = self.view
        for region in selection:
            pass

class EscapeBackslashesCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            self.escape(edit, region.end())

    def escape(self, edit, point):
        score = lambda p: self.view.score_selector(p, 'string')
        if not score(point):
            return

        begin = point
        while score(begin - 1):
            begin -= 1

        end = point + 1
        while score(end):
            end += 1

        region = sublime.Region(begin, end)
        content = self.view.substr(region)
        initial_content_length = len(content)

        content = content.replace('\\', '\\\\')
        if len(content) > initial_content_length:
            self.view.replace(edit, region, content)

class ShrinkSpacesCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        selection = self.view.sel()
        for region in selection:
            point = region.end()
            selection.subtract(region)
            point = self.shrink(edit, point) + 1
            selection.add(sublime.Region(point, point))

    def shrink(self, edit, point):
        score = lambda p: self.view.substr(p) == ' '

        begin = point
        while score(begin - 1):
            begin -= 1

        end = point
        while score(end):
            end += 1

        if end - begin < 2:
            return point

        region = sublime.Region(begin, end)
        self.view.replace(edit, region, ' ')
        return begin

class ShowFilePathCommand(sublime_plugin.WindowCommand):
    def run(self):
        file_path = self.window.active_view().file_name()
        if not file_path:
            return

        prefix = None
        variables = self.window.extract_variables()

        if "project" in variables:
            settings = self.window.project_data().get("settings", dict())
            base_path = settings.get("project_root", variables["project_path"])

            if file_path.startswith(base_path + os.sep):
                file_path = file_path[len(base_path)+1:]
                prefix = variables["project_base_name"]

        if not prefix:
            if sys.platform != "win32":
                home_path = os.environ["HOME"]
            else:
                home_path = os.environ["HOMEDRIVE"] + os.environ["HOMEPATH"]

            if file_path.startswith(home_path + os.sep):
                file_path = file_path[len(home_path)+1:]
                prefix = "~"
            elif sys.platform == "win32":
                prefix = file_path[0:2].lower()
                file_path = file_path[3:]
            else:
                prefix = "/"
                file_path = file_path[1:]

        sublime.status_message("({}) → {}".format(prefix, file_path.replace(os.sep, " → ")))

class ToggleIndentGuidesCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        guides = self.view.settings().get("indent_guide_options")
        guides = [] if len(guides) > 0 else ["draw_normal"]
        self.view.settings().set("indent_guide_options", guides)

class ToggleDrawCenteredCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        s = sublime.load_settings("Preferences.sublime-settings")
        current = s.get("draw_centered", False)
        s.set("draw_centered", not current)
        sublime.save_settings("Preferences.sublime-settings")

    def is_checked(self):
        s = sublime.load_settings("Preferences.sublime-settings")
        return s.get("draw_centered", False)

class OpenFilePathCommand(sublime_plugin.WindowCommand):
    def run(self):
        def on_done(x): self.window.open_file(x.strip(), sublime.ENCODED_POSITION)
        self.window.show_input_panel("File Name:", '', on_done, None, None)
