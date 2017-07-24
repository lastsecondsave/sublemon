import sublime

from sublime_plugin import TextCommand


RUNNING_ON_WINDOWS = sublime.platform() == 'windows'


class RegionCommand(TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            self.process_region(edit, region)

    def process_region(self, edit, region):
        pass


def for_every_region(command, edit, action):
    for region in command.view.sel():
        action(edit, region)


def row_to_line(view, row):
    return view.line(view.text_point(row, 0))


def row_to_full_line(view, row):
    return view.full_line(view.text_point(row, 0))
