# pylint: disable=invalid-name

import subprocess
from pathlib import Path

import sublime

RUNNING_ON_WINDOWS = sublime.platform() == "windows"
RUNNING_ON_LINUX = sublime.platform() == "linux"

POPEN_CREATION_FLAGS = subprocess.CREATE_NO_WINDOW if RUNNING_ON_WINDOWS else 0


def pref(key, default=None, view=None, window=None, expand=False, settings=False):
    value = None

    if view:
        window = view.window()

    if window:
        value = (window.project_data() or {}).get("settings", {}).get(key)

    if value is None and settings:
        value = sublime.load_settings("Sublemon.sublime-settings").get(key)

    if value is None:
        return default

    if window and expand:
        if isinstance(value, str):
            value = sublime.expand_variables(value, window.extract_variables())
        elif isinstance(value, list):
            variables = window.extract_variables()
            value = [sublime.expand_variables(x, variables) for x in value]

    return value


def listify(value, split=None):
    if isinstance(value, list):
        return value

    if isinstance(value, str) and split:
        if split in value:
            return value.split(split)

    return [value] if value is not None else []


def indent_params(view):
    tab_size = view.settings().get("tab_size")
    use_tabs = not view.settings().get("translate_tabs_to_spaces")

    return (use_tabs, tab_size)


def view_cwd(view):
    if active_file := view.file_name():
        return Path(active_file).parent
    return Path.home()


def locate_config(view, *file_names):
    active_file = view.file_name()
    if not active_file:
        return None

    for parent in Path(active_file).parents:
        for file_name in file_names:
            if (path := parent.joinpath(file_name)).exists():
                return path

        if parent.joinpath(".git").exists():
            return None

    return None


def active_view_contains_file(window):
    return bool(window.active_view() and window.active_view().file_name())


def start_process(args, cwd=None):
    # pylint: disable=consider-using-with
    subprocess.Popen(
        args,
        cwd=cwd,
        creationflags=POPEN_CREATION_FLAGS,
    )
