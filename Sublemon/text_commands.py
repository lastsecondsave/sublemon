import re

import sublime
from sublime import Region
from sublime_plugin import TextCommand


class EscapeBackslashesCommand(TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            self.escape(edit, region.end())

    def points_to_string(self, point):
        return self.view.score_selector(point, 'string')

    def escape(self, edit, point):
        if not self.points_to_string(point):
            return

        (begin, end) = (point, point + 1)

        while self.points_to_string(begin - 1):
            begin -= 1

        while self.points_to_string(end):
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
        begin = point
        while self.view.substr(begin - 1) == ' ':
            begin -= 1

        end = point
        while self.view.substr(end) == ' ':
            end += 1

        if end - begin < 2:
            return point

        self.view.replace(edit, Region(begin, end), ' ')
        return begin + 1


class ToggleLigaturesCommand(TextCommand):
    def run(self, _edit):
        font_options = self.view.settings().get("font_options")
        enable = "no_calt" in font_options
        if enable:
            font_options.remove("no_calt")
        else:
            font_options.append("no_calt")
        self.view.settings().set("font_options", font_options)
        show_setting_status('ligatires', enable)


class ToggleSettingVerboseCommand(TextCommand):
    def run(self, _edit, setting):
        was_enabled = self.view.settings().get(setting)
        self.view.run_command('toggle_setting', dict(setting=setting))
        show_setting_status(setting, not was_enabled)


def show_setting_status(setting, active):
    status = 'ON' if active else 'OFF'
    setting = setting.replace('_', ' ').title()
    sublime.status_message('{}: {}'.format(setting, status))


class StreamlineRegionsCommand(TextCommand):
    def run(self, _edit):
        selection = self.view.sel()
        regions = [r for r in selection if not r.empty()]

        if not regions:
            return

        left, right = 0, 0

        for region in regions:
            if region.a > region.b:
                left += 1
            else:
                right += 1

        if left == 0 or right == 0:
            replacement = [Region(r.b, r.a) for r in regions]
        elif left <= right:
            replacement = [Region(r.begin(), r.end()) for r in regions]
        else:
            replacement = [Region(r.end(), r.begin()) for r in regions]

        for region in regions:
            selection.subtract(region)

        selection.add_all(replacement)


class SelectionToCursorsCommand(TextCommand):
    def run(self, _edit):
        selection = self.view.sel()
        for region in selection:
            if region.empty():
                continue

            selection.subtract(region)
            selection.add(Region(region.a, region.a))
            selection.add(Region(region.b, region.b))


class LastSingleSelectionCommand(TextCommand):
    def run(self, _edit):
        selection = self.view.sel()
        regions = [r for r in selection]
        for region in regions[:-1]:
            selection.subtract(region)


class SelectWithMarkersCommand(TextCommand):
    def run(self, _edit, left, right):
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


class IndentToBracesCommand(TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            self.indent_region(edit, region)

    def indent_region(self, edit, region):
        row, col = self.view.rowcol(region.begin())
        if row == 0:
            return

        line = self.view.line(self.view.text_point(row-1, col))
        if line.empty():
            return

        open_brace_position = self.find_open_brace_position(self.view.substr(line))
        if open_brace_position < 0:
            return

        self.indent_lines(edit, region, ' ' * (open_brace_position+1))

    def indent_lines(self, edit, region, indent):
        for line in reversed(self.view.lines(region)):
            if line.empty():
                continue
            replacement = indent + self.view.substr(line).lstrip()
            self.view.replace(edit, line, replacement)

    @staticmethod
    def find_open_brace_position(text):
        counters = {
            ('[', ']'): 0,
            ('{', '}'): 0,
            ('(', ')'): 0
        }

        for i in reversed(range(len(text))):
            for chars, counter in counters.items():
                if text[i] == chars[0]:
                    counter -= 1
                elif text[i] == chars[1]:
                    counter += 1

                if counter == -1:
                    return i

                counters[chars] = counter

        return -1


class DualSideDeleteCommand(TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            self.view.replace(edit,
                              Region(region.end(), region.end()+1),
                              '')
            self.view.replace(edit,
                              Region(region.begin(), region.begin()-1),
                              '')
