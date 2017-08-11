import os
import re

import sublime
from sublime import Region
from sublime_plugin import ApplicationCommand, TextCommand, WindowCommand

import Sublemon.lib.util as util


class EscapeBackslashesCommand(util.RegionCommand):
    def process_region(self, edit, region):
        def score(p):
            return self.view.score_selector(p, 'string')

        point = region.end()
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

        point = region.end()
        line = self.view.line(point)

        if self.EMPTY_LINE_PATTERN.match(self.view.substr(line)):
            point = self.shrink_lines(edit, line)
        else:
            point = self.shrink_spaces(edit, point)

        selection.add(Region(point, point))

    def shrink_lines(self, edit, line):
        row = self.view.rowcol(line.begin())[0]

        first_row = row
        anchor = None

        while True:
            prev_line = util.row_to_line(self.view, first_row-1)
            if prev_line.begin() == anchor:
                break

            if not self.EMPTY_LINE_PATTERN.match(self.view.substr(prev_line)):
                break

            first_row -= 1
            anchor = prev_line.begin()

        last_row = row
        anchor = None

        while True:
            next_line = util.row_to_line(self.view, last_row+1)
            if next_line.end() == anchor:
                break

            if not self.EMPTY_LINE_PATTERN.match(self.view.substr(next_line)):
                break

            last_row += 1
            anchor = next_line.end()

        if first_row == last_row:
            self.view.erase(edit, line)
            return line.begin()

        begin = util.row_to_line(self.view, first_row).begin()
        end = util.row_to_line(self.view, last_row).end()

        self.view.erase(edit, Region(begin, end))
        return begin

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


class OpenFilePathCommand(WindowCommand):
    def run(self):
        def on_done(x):
            self.window.open_file(x.strip(), sublime.ENCODED_POSITION)
        self.window.show_input_panel("File Name:", '', on_done, None, None)


class StreamlineRegionsCommand(TextCommand):
    def run(self, edit):
        selection = self.view.sel()
        regions = [r for r in selection if not r.empty()]

        if not regions:
            return

        left, right = self.aligment(regions)

        if left == 0 or right == 0:
            replacement = [Region(r.b, r.a) for r in regions]
        elif left <= right:
            replacement = [Region(r.begin(), r.end()) for r in regions]
        else:
            replacement = [Region(r.end(), r.begin()) for r in regions]

        for r in regions:
            selection.subtract(r)

        selection.add_all(replacement)

    def aligment(self, regions):
        left, right = 0, 0

        for r in regions:
            if r.a > r.b:
                left += 1
            else:
                right += 1

        return left, right


class LastSingleSelection(TextCommand):
    def run(self, edit):
        selection = self.view.sel()
        regions = [r for r in selection]
        for region in regions[:-1]:
            selection.subtract(region)
