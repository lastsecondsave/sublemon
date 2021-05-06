import plistlib
import shutil
from pathlib import Path


def generate(all_settings):
    target_dir = Path(".generated")
    shutil.rmtree(target_dir, ignore_errors=True)
    target_dir.mkdir(exist_ok=True)

    for scope, settings in all_settings.items():
        write_settings(scope, settings, target_dir)


def write_settings(scope, settings, target_dir):
    sublime_settings = {}

    if comments := extract_comments(settings):
        sublime_settings["shellVariables"] = comments

    for key, val in settings.items():
        if key == "symbolTransformation":
            val = ";".join(wrap(val)) + ";"
        elif isinstance(val, bool):
            val = int(val)

        sublime_settings[key] = val

    path = target_dir / f"{scope}.tmPreferences"

    with path.open(mode="wb") as pfile:
        plistlib.dump({"scope": scope, "settings": sublime_settings}, pfile)

    print("Generated", path.name)


def wrap(value):
    return value if isinstance(value, (list, tuple)) else (value,)


def extract_comments(settings):
    shell_variables = []
    comment_index = 1

    def add_comment(variant, value):
        name = f"TM_COMMENT_{variant}_{comment_index}"
        shell_variables.append({"name": name, "value": value})

    for line_comment in wrap(settings.pop("lineComment", [])):
        add_comment("START", line_comment + " ")
        comment_index += 1

    if block_comment := settings.pop("blockComment", None):
        add_comment("START", block_comment[0] + " ")
        add_comment("END", " " + block_comment[1])

    return shell_variables


SETTINGS = {
    "meta.context.sublime-syntax entity.name.section": {
        "showInSymbolList": True,
    },
    "meta.variables.sublime-syntax variable.other": {
        "showInSymbolList": True,
    },
    "text.rfc entity.name.title": {"showInSymbolList": True},
    "source.ini": {"lineComment": ("#", ";")},
    "source.ini entity.name.section": {"showInSymbolList": True},
    "source.unix": {"lineComment": "#"},
    "source.powershell": {"lineComment": "#", "blockComment": ("<#", "#>")},
    "source.python": {
        "increaseIndentPattern": r"^(\s*(class|(\basync\s+)?(def|for|with)|elif|else|except|finally|if|try|while)\b.*:|.*[\{\[])\s*$",
        "decreaseIndentPattern": r"^\s*((elif|else|except|finally)\b.*:|[\}\]])",
    },
}

generate(SETTINGS)
