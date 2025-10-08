from sublime_plugin import WindowCommand


class TabberNextCommand(WindowCommand):
    def run(self, forward=True):
        sheets = self.window.selected_sheets()
        active = self.window.active_sheet()

        step = 1 if forward else -1
        index = (sheets.index(active) + len(sheets) + step) % len(sheets)

        self.window.focus_sheet(sheets[index])


class TabberFocusCommand(WindowCommand):
    def run(self, index):  # pylint: disable=arguments-differ
        sheets = self.window.selected_sheets()
        if index < len(sheets):
            self.window.focus_sheet(sheets[index])


class TabberMoveCommand(WindowCommand):
    def run(self, forward=True):  # pylint: disable=arguments-differ
        selected_sheets = self.window.selected_sheets()
        sheet = self.window.active_sheet()
        group, index = self.window.get_sheet_index(sheet)

        if forward:
            index += 1
            if index == len(self.window.sheets_in_group(group)):
                group += 1
                index = 0
        else:
            index -= 1
            if index < 0:
                group -= 1
                index = len(self.window.sheets_in_group(group))

        if 0 <= group < self.window.num_groups():
            self.window.set_sheet_index(sheet, group, index)

        if len(selected_sheets) > 1:
            self.window.select_sheets(selected_sheets)


class TabberJoinCommand(WindowCommand):
    def run(self):
        sheets = self.window.selected_sheets()
        active = self.window.active_sheet()
        group, index = self.window.get_sheet_index(sheets[0])

        for sheet in sheets[1:]:
            index += 1
            self.window.set_sheet_index(sheet, group, index)

        self.window.select_sheets(sheets)
        self.window.focus_sheet(active)
