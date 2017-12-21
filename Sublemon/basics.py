import os
import re

import sublime
from sublime import Region
from sublime_plugin import ApplicationCommand, TextCommand, WindowCommand


class EscapeBackslashesCommand(TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            self.escape(edit, region.end())

    def escape(self, edit, point):
        def score(p):
            return self.view.score_selector(p, 'string')

        if not score(point):
            return

        (begin, end) = (point, point + 1)

        while score(begin - 1):
            begin -= 1

        while score(end):
            end += 1

        region = Region(begin, end)
        content = self.view.substr(region)
        initial_content_length = len(content)

        content = content.replace('\\', '\\\\')
        if len(content) > initial_content_length:
            self.view.replace(edit, region, content)


class ShrinkWhitespaceCommand(TextCommand):
    EMPTY_LINE_PATTERN = re.compile(r'\s*$')

    def run(self, edit):
        selection = self.view.sel()
        for region in selection:
            selection.subtract(region)
            selection.add(self.shrink(edit, region.end()))

    def is_empty_line(self, line_region):
        return self.EMPTY_LINE_PATTERN.match(self.view.substr(line_region))

    def shrink(self, edit, point):
        line = self.view.line(point)

        if self.is_empty_line(line):
            point = self.shrink_lines(edit, line)
        else:
            point = self.shrink_spaces(edit, point)

        return Region(point, point)

    def row_to_line(self, row):
        return self.view.line(self.view.text_point(row, 0))

    def shrink_lines(self, edit, line):
        row = self.view.rowcol(line.begin())[0]

        first_row, anchor = (row, None)

        while True:
            prev_line = self.row_to_line(first_row-1)
            if prev_line.begin() == anchor:
                break

            if not self.is_empty_line(prev_line):
                break

            first_row -= 1
            anchor = prev_line.begin()

        last_row, anchor = (row, None)

        while True:
            next_line = self.row_to_line(last_row+1)
            if next_line.end() == anchor:
                break

            if not self.is_empty_line(next_line):
                break

            last_row += 1
            anchor = next_line.end()

        if first_row == last_row:
            self.view.erase(edit, line)
            return line.begin()

        begin = self.row_to_line(first_row).begin()
        end = self.row_to_line(last_row).end()

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
    RUNNING_ON_WINDOWS = sublime.platform() == 'windows'

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
            home_path = (os.environ['HOME'] if not self.RUNNING_ON_WINDOWS
                         else os.environ['HOMEDRIVE'] + os.environ['HOMEPATH'])

            if file_path.startswith(home_path + os.sep):
                file_path = file_path[len(home_path)+1:]
                prefix = "~"
            elif self.RUNNING_ON_WINDOWS:
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
        guides = [] if guides else ["draw_normal", "draw_active"]
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


class LastSingleSelectionCommand(TextCommand):
    def run(self, edit):
        selection = self.view.sel()
        regions = [r for r in selection]
        for region in regions[:-1]:
            selection.subtract(region)


class SelectWithMarkersCommand(TextCommand):
    def run(self, edit, left, right):
        selection = self.view.sel()
        for region in selection:
            replacement = self.expand_region(region.end(), left, right)
            if replacement:
                selection.add(replacement)

    def expand_region(self, point, left_marker, right_marker):
        lmlen = len(left_marker)
        left = point - lmlen

        while left_marker != self.view.substr(Region(left, left+lmlen)):
            left -= 1
            if left < 0:
                return None

        rmlen = len(right_marker)
        right = point + rmlen

        while right_marker != self.view.substr(Region(right-rmlen, right)):
            right += 1
            if right > self.view.size():
                return None

        return Region(left+lmlen, right-rmlen)


class SelectWithCustomMarkersCommand(WindowCommand):
    def run(self):
        def on_done(x):
            if x.strip():
                self.window.active_view().run_command(
                    'select_with_markers', self.split_markers(x))

        self.window.show_input_panel(
            'Selection markers:', '', on_done, None, None)

    def split_markers(self, markers):
        i = markers.find(' ')

        b1 = i if i >= 0 else int(len(markers) / 2)
        b2 = i + 1 if i >= 0 else b1

        return {'left': markers[0:b1], 'right': markers[b2:]}
