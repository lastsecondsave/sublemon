import importlib
import json
import re
import sys
from collections import OrderedDict
from itertools import chain

import sublime
from sublime import Region
from sublime_plugin import (
    ApplicationCommand,
    EventListener,
    ListInputHandler,
    TextCommand,
    TextInputHandler,
    WindowCommand,
)

from . import indent_params


class SublemonReloadCommand(ApplicationCommand):
    def run(self):
        modules = [v for k, v in sys.modules.items() if k.startswith("Sublemon")]
        modules.append(sys.modules["Default.exec"])

        for module in modules:
            print("reloading", module.__name__)
            importlib.reload(module)

        sublime.active_window().status_message("Reloaded")


class CommandFineTuning(EventListener):
    def on_post_text_command(self, view, command_name, args):
        if command_name == "toggle_setting":
            setting = args["setting"]
            show_setting_status(setting, view.settings().get(setting))

        elif command_name == "set_setting":
            show_setting_status(args["setting"], args["value"])

        elif command_name == "swap_with_mark":
            location = view.sel()[0]
            view.show(location)

    def on_activated(self, view):
        window = view.window()
        if not window:
            return

        sheets = window.selected_sheets()
        if len(sheets) > 1:
            for sheet in sheets:
                sheet.view().settings().set("draw_centered", False)


class EscapeBackslashesCommand(TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            self.escape(edit, region.end())

    def points_to_string(self, point):
        return self.view.score_selector(point, "string")

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

        content = content.replace("\\", "\\\\")
        if len(content) > initial_content_length:
            self.view.replace(edit, region, content)


class SortTokensCommand(TextCommand):
    SEP_PATTERNS = {", ": re.compile(r",\s*"), " ": re.compile(r"\s+")}
    SEP_CHARACTERS = "|"

    def run(self, edit):
        for region in self.view.sel():
            content = self.view.substr(region)
            self.view.replace(edit, region, self.sort_tokens(content))

    def sort_tokens(self, content):
        for sep, pattern in self.SEP_PATTERNS.items():
            tokens = pattern.split(content)
            if len(tokens) > 1:
                return sep.join(sorted(tokens))

        for sep in self.SEP_CHARACTERS:
            tokens = content.split(sep)
            if len(tokens) > 1:
                return sep.join(sorted(tokens))

        return content


class ShrinkWhitespaceCommand(TextCommand):
    EMPTY_LINE_PATTERN = re.compile(r"\s*$")

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
        row, _ = self.view.rowcol(line.begin())

        first_row, boundary = (row, None)

        while True:
            prev_line = self.row_to_line(first_row - 1)
            if prev_line.begin() == boundary:
                break

            if not self.is_empty_line(prev_line):
                break

            first_row -= 1
            boundary = prev_line.begin()

        last_row, boundary = (row, None)

        while True:
            next_line = self.row_to_line(last_row + 1)
            if next_line.end() == boundary:
                break

            if not self.is_empty_line(next_line):
                break

            last_row += 1
            boundary = next_line.end()

        if first_row == last_row:
            self.view.erase(edit, line)
            return line.begin()

        begin = self.row_to_line(first_row).begin()
        end = self.row_to_line(last_row).end()

        self.view.erase(edit, Region(begin, end))
        return begin

    def shrink_spaces(self, edit, point):
        begin = point
        while self.view.substr(begin - 1) == " ":
            begin -= 1

        end = point
        while self.view.substr(end) == " ":
            end += 1

        if end - begin < 2:
            return point

        self.view.replace(edit, Region(begin, end), " ")
        return begin + 1


class ToggleLigaturesCommand(WindowCommand):
    def run(self):
        settings = self.window.active_view().settings()
        font_options = settings.get("font_options")

        enable = "no_calt" in font_options
        if enable:
            font_options.remove("no_calt")
        else:
            font_options.append("no_calt")

        settings.set("font_options", font_options)
        show_setting_status("ligatures", enable)


def show_setting_status(setting, value):
    if isinstance(value, bool):
        value = "ON" if value else "OFF"
    setting = setting.replace("_", " ").title()
    sublime.status_message(f"{setting}: {value}")


class StreamlineRegionsCommand(TextCommand):
    def run(self, edit):
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
    def run(self, edit):
        selection = self.view.sel()
        regions = [r for r in selection if not r.empty()]

        for region in regions:
            selection.subtract(region)
            selection.add(Region(region.a, region.a))
            selection.add(Region(region.b, region.b))


class LastSingleSelectionCommand(TextCommand):
    def run(self, edit):
        selection = self.view.sel()
        for region in list(selection)[:-1]:
            selection.subtract(region)


class SelectQueryCommand(TextCommand):
    last_query = ""

    def run(self, edit):
        input_view = self.view.window().show_input_panel(
            "Select:", self.last_query, self.on_done, None, None
        )

        input_view.sel().add(sublime.Region(0, len(self.last_query)))

    def on_done(self, query):
        self.last_query = query

        for region in self.view.sel():
            self.expand_region(region, query)

    def expand_region(self, region, query):
        lm, rm, wide = self.parse_query(query)  # pylint: disable=invalid-name

        lmlen = len(lm)
        left = region.begin() - lmlen

        while lm != self.view.substr(Region(left, left + lmlen)):
            left -= 1
            if left < 0:
                return

        if rm:
            right = self.view.find(rm, region.end(), sublime.LITERAL)
            right = right.begin() if right else None
        else:
            right = region.end()

        if not right:
            return

        if wide:
            right += len(rm)
        else:
            left += lmlen

        self.view.sel().add(Region(left, right))

    def parse_query(self, query):
        left, right = 0, 0
        wide = False

        if query == " ":
            left, right = 0, 0

        elif query in ("  ", "><"):
            left, right = 1, 1

        elif (sep := query.find("><")) > -1:
            left, right = sep, sep + 2

        elif (sep := query.find("> <")) > -1:
            left, right = sep, sep + 3
            wide = True

        elif (sep := query.find("  ")) > -1:
            left, right = sep, sep + 2
            wide = True

        elif (sep := query.find(" ")) > -1:
            left, right = sep, sep + 1

        else:
            left = int(len(query) / 2)
            right = left

        return (query[:left], query[right:], wide)


class IndentToBracesCommand(TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            self.indent_region(edit, region)

    def indent_region(self, edit, region):
        row, col = self.view.rowcol(region.begin())
        if row == 0:
            return

        line = self.view.line(self.view.text_point(row - 1, col))
        if line.empty():
            return

        open_brace_position = self.find_open_brace_position(self.view.substr(line))
        if open_brace_position < 0:
            return

        self.indent_lines(edit, region, " " * (open_brace_position + 1))

    def indent_lines(self, edit, region, indent):
        for line in reversed(self.view.lines(region)):
            if line.empty():
                continue
            replacement = indent + self.view.substr(line).lstrip()
            self.view.replace(edit, line, replacement)

    @staticmethod
    def find_open_brace_position(text):
        counters = {("[", "]"): 0, ("{", "}"): 0, ("(", ")"): 0}

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
            self.view.erase(edit, Region(region.end(), region.end() + 1))
            self.view.erase(edit, Region(region.begin(), region.begin() - 1))


class JsonReindentCommand(TextCommand):
    def is_enabled(self):
        json_file = self.view.match_selector(0, "source.json")
        return self.has_selected_text() or json_file

    def has_selected_text(self):
        return all(not region.empty() for region in self.view.sel())

    def run(self, edit):
        regions = (
            self.view.sel()
            if self.has_selected_text()
            else (Region(0, self.view.size()),)
        )

        for region in regions:
            self.reindent(edit, region)

    def reindent(self, edit, region):
        try:
            parsed = json.loads(self.view.substr(region), object_pairs_hook=OrderedDict)
        except ValueError as err:
            self.view.window().status_message(f"Invalid json: {err}")
            return

        _, tab_size = indent_params(self.view)
        self.view.replace(edit, region, json.dumps(parsed, indent=tab_size))


class CloseWithoutSavingCommand(WindowCommand):
    def run(self):
        view = self.window.active_view()
        view.set_scratch(True)
        view.close()


class WrapLinesAtWidthCommand(WindowCommand):
    def run(self, width):  # pylint: disable=arguments-differ
        self.window.run_command("wrap_lines", {"width": int(width)})

    def input(self, _args):
        class WidthInputHandler(TextInputHandler):
            def placeholder(self):
                return "Width"

        return WidthInputHandler()


class SaveAllEdited(WindowCommand):
    def run(self):
        for view in self.window.views():
            if view.is_dirty() and view.file_name():
                view.run_command("save")


class MoveViewportHorizontallyCommand(TextCommand):
    def run(self, _edit, forward=True):  # pylint: disable=arguments-differ
        current = self.view.viewport_position()
        if forward:
            cursor = self.view.sel()[0]
            line = self.view.line(cursor)
            line_width = self.view.text_to_layout(line.end())[0]
            xpos = line_width - self.view.viewport_extent()[0]
        else:
            xpos = 0

        self.view.set_viewport_position((xpos, current[1]), False)


class AddRulerCommand(TextCommand):
    def run(self, _edit, position):  # pylint: disable=arguments-differ
        settings = self.view.settings()
        rulers = settings.get("rulers", [])
        rulers.extend([int(p) for p in position.replace(",", " ").split()])
        settings.set("rulers", rulers)

    def input(self, _args):
        class PositionInputHandler(TextInputHandler):
            def placeholder(self):
                return "Position"

        return PositionInputHandler()


class DeleteRulersCommand(TextCommand):
    def run(self, _edit):
        self.view.settings().set("rulers", [])


class ConvertCaseCommand(TextCommand):
    SEPARATORS = re.compile(r"[_\.\- ]+")
    CASE_CHANGE = re.compile(r"(?=[A-Z0-9])")

    CONVERTORS = {
        "camelCase": lambda ts: ts[0] + "".join(x.capitalize() for x in ts[1:]),
        "PascalCase": lambda ts: "".join(x.capitalize() for x in ts),
        "snake_case": "_".join,
        "SCREAM_CASE": lambda ts: "_".join(ts).upper(),
        "kebab-case": "-".join,
        "dot.case": ".".join,
        "Sentence case": lambda ts: (
            " ".join(chain((ts[0].capitalize(),), (x.lower() for x in ts[1:])))
        ),
        "Title Case": lambda ts: " ".join(x.capitalize() for x in ts),
    }

    def run(self, edit, case):  # pylint: disable=arguments-differ
        adjusted_regions = []

        for region in self.view.sel():
            if region.empty():
                region = self.view.word(region)
                if region.empty():
                    continue

            token = self.view.substr(region)
            replacement = self.convert(token, case)
            self.view.replace(edit, region, replacement)

            begin = region.begin()
            adjusted_regions.append(Region(begin, begin + len(replacement)))

        self.view.sel().add_all(adjusted_regions)

    def convert(self, token, case):
        tokens = [x.lower() for x in self.tokenize(token)]
        return self.CONVERTORS[case](tokens)

    def tokenize(self, token):
        tokens = self.SEPARATORS.split(token)

        if len(tokens) > 1 or token.isupper():
            return tokens

        splits = self.CASE_CHANGE.split(token)
        tokens = []
        buffer = ""

        for split in splits:
            if not split:
                continue

            if len(split) == 1:
                buffer += split
                continue

            if buffer:
                tokens.append(buffer)
                buffer = ""

            tokens.append(split)

        if buffer:
            tokens.append(buffer)

        return tokens

    def input(self, _args):
        items = self.CONVERTORS.keys()

        class CaseInputHandler(ListInputHandler):
            def list_items(self):
                return items

        return CaseInputHandler()


class CopyAsOneLineCommand(TextCommand):
    EOL_PATTERN = re.compile(r"(\s*\\?\n\s*)+")

    def run(self, edit):
        chunks = []

        for region in self.view.sel():
            if region.empty():
                continue

            text = self.view.substr(region)
            if text := self.EOL_PATTERN.sub(" ", text).strip():
                chunks.append(text)

        text = " ".join(chunks)
        sublime.set_clipboard(text)
        sublime.status_message(f"Copied {len(text)} characters")


# pylint: disable=arguments-differ
class FindAllInFolderCommand(WindowCommand):
    def run(self, dirs):
        self.window.run_command(
            "show_panel",
            {"panel": "find_in_files", "where": ",".join(dirs)},
        )

    def is_visible(self, dirs):
        return len(dirs) > 0


class GlideCommand(TextCommand):
    def run(self, edit, forward=True, amount=0.5):
        page_size = self.view.viewport_extent()[1] / self.view.line_height()
        distance = int(page_size * amount) * (1 if forward else -1)

        def move(region):
            row, col = self.view.rowcol(region.begin())
            return Region(self.view.text_point(row + distance, col, clamp_column=True))

        selection = self.view.sel()
        region = move(next(iter(selection)))

        selection.clear()
        selection.add(region)

        self.view.show_at_center(region)
