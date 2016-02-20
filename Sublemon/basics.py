import os
import re
import sublime, sublime_plugin
import sys

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
  def run(self):
    file_path = self.window.active_view().file_name()
    if not file_path:
      return

    if self.window.project_data():
      score = 0
      short_path = file_path

      for name, path in self.project_folders().items():
        if not file_path.startswith(path):
          continue

        if len(path) > score:
          short_path = os.path.join(name, file_path[len(path):])

      file_path = short_path

    home_path = os.environ["HOME"] + os.sep
    if file_path.startswith(home_path):
      file_path = "~ " + file_path[len(home_path):]

    sublime.status_message(file_path.replace(os.sep, " → "))

  def project_folders(self):
    project_path = self.window.extract_variables()["project_path"]
    folders = self.window.project_data()["folders"]
    result = dict()
    for folder in folders:
      path = os.path.normpath(os.path.join(project_path, folder["path"]))
      name = folder["name"] if "name" in folder else os.path.basename(path)
      result[name] = path + os.sep
    return result

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
  WIN_PATH = re.compile(r'(?:[A-Za-z]:|\\)\\[^<>:"/|?*]+(?::\d+){0,2}')
  NIX_PATH = re.compile(r'~?/.+')

  def run(self):
    initial = sublime.get_clipboard(4096).strip()
    if initial.find('\n') != -1:
      initial = ""

    path_pattern = self.WIN_PATH if sys.platform == "win32" else self.NIX_PATH
    if initial and not path_pattern.match(initial):
      initial = ""

    on_done = lambda x: self.window.open_file(x.strip(), sublime.ENCODED_POSITION)
    view = self.window.show_input_panel("File Name:", initial, on_done, None, None)
    view.sel().add(sublime.Region(0, len(initial)))
