import sublime
from sublime_plugin import ListInputHandler, TextCommand

SETTING_GROUPS = "sublemon.highlight.groups"


class HighlightAddCommand(TextCommand):
    def input(self, _args):
        return StyleInputHandler()

    def is_enabled(self):
        return all(not r.empty() for r in self.view.sel())

    def run(self, edit, style, color):  # pylint: disable=arguments-differ
        regions = [r for r in self.view.sel() if not r.empty()]

        for region in regions:
            self.view.sel().subtract(region)
            self.view.sel().add(sublime.Region(region.end(), region.end()))

        flags = sublime.DRAW_NO_OUTLINE
        if style == "Underline":
            flags |= sublime.DRAW_SOLID_UNDERLINE | sublime.DRAW_NO_FILL

        scope = f"style.{color.lower().replace(' ', '')}"
        name = f"{color} {style}"

        if existing_regions := self.view.get_regions(name):
            regions += existing_regions

        self.view.add_regions(name, regions, flags=flags, scope=scope)

        groups = self.view.settings().get(SETTING_GROUPS, [])
        if name not in groups:
            groups.append(name)

        self.view.settings().set(SETTING_GROUPS, groups)


class StyleInputHandler(ListInputHandler):
    def list_items(self):
        return ["Highlight", "Underline"]

    def next_input(self, _args):
        return ColorInputHandler()


class ColorInputHandler(ListInputHandler):
    def list_items(self):
        return ["Orange", "Blue", "Green", "Crimson", "Gray"]


class HighlightDeleteAllCommand(TextCommand):
    def is_enabled(self):
        return bool(self.view.settings().get(SETTING_GROUPS))

    def run(self, edit):
        groups = self.view.settings().get(SETTING_GROUPS)
        for group in groups:
            self.view.erase_regions(group)
        self.view.settings().erase(SETTING_GROUPS)


class HighlightDeleteCommand(TextCommand):
    def is_enabled(self):
        return bool(self.view.settings().get(SETTING_GROUPS))

    def run(self, edit, group):  # pylint: disable=arguments-differ
        self.view.erase_regions(group)
        groups = self.view.settings().get(SETTING_GROUPS)
        groups.remove(group)
        self.view.settings().set(SETTING_GROUPS, groups)

    def input(self, _args):
        groups = self.view.settings().get(SETTING_GROUPS)

        class GroupInputHandler(ListInputHandler):
            def list_items(self):
                return groups

        return GroupInputHandler()
