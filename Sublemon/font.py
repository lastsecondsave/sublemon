from sublime_plugin import EventListener, ListInputHandler, WindowCommand


class SelectFontCommand(WindowCommand):
    FONTS = [
        "PragmataPro Liga",
        "Cascadia Code",
        "Consolas",
    ]

    def input(self, _args):
        fonts = self.FONTS
        selected = 0

        if font := self.window.settings().get("font_face"):
            try:
                selected = fonts.index(font)
            except ValueError:
                pass

        class FontInputHandler(ListInputHandler):
            def list_items(self):
                return (fonts, selected)

        return FontInputHandler()

    def run(self, font):  # pylint: disable=arguments-differ
        self.window.settings().set("font_face", font)

        for sheet in self.window.selected_sheets():
            sheet.view().settings().set("font_face", font)


class SelectFontListener(EventListener):
    def on_new(self, view):
        self.set_font(view)

    def on_load(self, view):
        self.set_font(view)

    def on_activated(self, view):
        self.set_font(view)

    def set_font(self, view):
        window = view.window()
        if window and (font := window.settings().get("font_face")):
            view.settings().set("font_face", font)
