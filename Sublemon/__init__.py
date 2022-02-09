# pylint: disable=invalid-name

import subprocess
from pathlib import Path

import sublime

RUNNING_ON_WINDOWS = sublime.platform() == "windows"
RUNNING_ON_LINUX = sublime.platform() == "linux"

POPEN_CREATION_FLAGS = subprocess.CREATE_NO_WINDOW if RUNNING_ON_WINDOWS else 0


def pref(key, default=None):
    settings = sublime.load_settings("Preferences.sublime-settings")
    return settings.get(key, default)


def project_pref(window, key):
    value = (window.project_data() or {}).get("settings", {}).get(key)
    if isinstance(value, str):
        return sublime.expand_variables(value, window.extract_variables())

    return value


def indent_params(view):
    tab_size = view.settings().get("tab_size")
    use_tabs = not view.settings().get("translate_tabs_to_spaces")

    return (use_tabs, tab_size)


def view_cwd(view):
    if active_file := view.file_name():
        return Path(active_file).parent
    return Path.home()


def find_in_parent_directories(view, file_name):
    active_file = view.file_name()
    if not active_file:
        return None

    for parent in Path(active_file).parents:
        path = parent.joinpath(file_name)
        if path.exists():
            return path

        if parent.joinpath(".git").exists():
            return None

    return None


def active_view_contains_file(window):
    return bool(window.active_view() and window.active_view().file_name())


def sad_message(*args):
    print("☹", *args)
