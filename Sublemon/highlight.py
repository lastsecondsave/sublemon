import sublime
from sublime_plugin import ListInputHandler, TextCommand


class HighlightAddCommand(TextCommand):
    def input(self, _args):
        return StyleInputHandler()

    def run(self, edit, style, color):  # pylint: disable=arguments-differ
        regions = [r for r in self.view.sel() if not r.empty()]

        flags = sublime.DRAW_NO_OUTLINE
        if style == "Underline":
            flags |= sublime.DRAW_SOLID_UNDERLINE | sublime.DRAW_NO_FILL

        scope = f"style.{color.lower().replace(' ', '')}"
        name = f"{color} {style}"

        self.view.add_regions(name, regions, flags=flags, scope=scope)


class StyleInputHandler(ListInputHandler):
    def list_items(self):
        return ["Highlight", "Underline"]

    def next_input(self, _args):
        return ColorInputHandler()


class ColorInputHandler(ListInputHandler):
    def list_items(self):
        return ["Orange", "Dark Orange", "Crimson", "Blue", "Green", "Gray"]
