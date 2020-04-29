# pylint: disable=invalid-name

import sublime

RUNNING_ON_WINDOWS = sublime.platform() == 'windows'


def pref(key, default=None):
    settings = sublime.load_settings("Preferences.sublime-settings")
    return settings.get(key, default)


def project_pref(window, key, default=None):
    settings = window.project_data().get("settings")
    if not settings:
        return None

    value = settings.get(key, default)
    return sublime.expand_variables(value, window.extract_variables())
