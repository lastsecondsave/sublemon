# pylint: disable=invalid-name

from pathlib import Path

import sublime

RUNNING_ON_WINDOWS = sublime.platform() == "windows"


def pref(key, default=None):
    settings = sublime.load_settings("Preferences.sublime-settings")
    return settings.get(key, default)


def project_pref(window, key):
    value = (window.project_data() or {}).get("settings", {}).get(key)
    if not value:
        return value
    return sublime.expand_variables(value, window.extract_variables())


def indent_params(view):
    tab_size = view.settings().get("tab_size")
    use_tabs = not view.settings().get("translate_tabs_to_spaces")

    return (use_tabs, tab_size)


def view_cwd(view):
    if active_file := view.file_name():
        return Path(active_file).parent
    return Path.home()


def find_in_file_parents(view, file_name):
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
