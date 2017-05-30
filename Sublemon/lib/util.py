import sublime

from sublime_plugin import TextCommand


RUNNING_ON_WINDOWS = sublime.platform() == 'windows'


def for_every_region(command, edit, action):
    for region in command.view.sel():
        action(edit, region)


class RegionCommand(TextCommand):
    def run(self, edit):
        for region in self.view.sel():
            self.process_region(edit, region)

    def process_region(self, edit, region):
        pass
