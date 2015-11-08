import sublime, sublime_plugin

class SublemonDemoCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    selection = self.view.sel()
    view = self.view
    for region in selection:
      pass

class EscapeBackslashesCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    for region in self.view.sel():
      self.escape(edit, region.end())

  def escape(self, edit, point):
    score = lambda p: self.view.score_selector(p, 'string')
    if not score(point):
      return

    begin = point
    while score(begin - 1):
      begin -= 1

    end = point + 1
    while score(end):
      end += 1

    region = sublime.Region(begin, end)
    content = self.view.substr(region)
    initial_content_length = len(content)

    content = content.replace('\\', '\\\\')
    if len(content) > initial_content_length:
      self.view.replace(edit, region, content)

class ToggleIndentGuidesCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    guides = self.view.settings().get("indent_guide_options")
    guides = [] if len(guides) > 0 else ["draw_normal"]
    self.view.settings().set("indent_guide_options", guides)

class ToggleDrawCenteredCommand(sublime_plugin.ApplicationCommand):
  def run(self):
    s = sublime.load_settings("Preferences.sublime-settings")
    current = s.get("draw_centered", False)
    s.set("draw_centered", not current)
    sublime.save_settings("Preferences.sublime-settings")

  def is_checked(self):
    s = sublime.load_settings("Preferences.sublime-settings")
    return s.get("draw_centered", False)

