import sublime, sublime_plugin

class SublemonDemoCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    selection = self.view.sel()
    view = self.view
    for region in selection:
      pass

class SublemonEscapeCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    selection = self.view.sel()
    for region in selection:
      pass
