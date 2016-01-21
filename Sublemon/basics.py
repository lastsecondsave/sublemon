import os
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

class ShowFilePathCommand(sublime_plugin.WindowCommand):
  def run(self, raw=False):
    variables = self.window.extract_variables()
    if not "file" in variables:
      return

    file_path = variables["file"]

    if raw:
      sublime.status_message(file_path)

    if "project_path" in variables:
      project_path = variables["project_path"]
      if file_path.startswith(project_path):
        file_path = file_path[len(project_path)+1:]

    home_path = os.environ["HOME"]
    if file_path.startswith(home_path):
      file_path = "~ " + file_path[len(home_path)+1:]

    sublime.status_message(file_path.replace(os.sep, " → "))

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

class OpenFilePathCommand(sublime_plugin.WindowCommand):
  def run(self):
    on_done = lambda x: self.window.open_file(x.strip(), sublime.ENCODED_POSITION)
    initial = sublime.get_clipboard(4096).strip()
    view = self.window.show_input_panel("File Name:", initial, on_done, None, None)
    view.sel().add(sublime.Region(0, len(initial)))
