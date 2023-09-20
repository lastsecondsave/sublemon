from sublime_plugin import WindowCommand


class TabberNextCommand(WindowCommand):
    def run(self, forward=True):
        sheets = self.window.selected_sheets()
        active = self.window.active_sheet()

        step = 1 if forward else -1
        index = (sheets.index(active) + len(sheets) + step) % len(sheets)

        self.window.focus_sheet(sheets[index])


class TabberFocus(WindowCommand):
    def run(self, index):  # pylint: disable=arguments-differ
        sheets = self.window.selected_sheets()
        if index < len(sheets):
            self.window.focus_sheet(sheets[index])
