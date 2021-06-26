import plistlib
import shutil
from pathlib import Path

SUBLEMON = Path(__file__).resolve().parent.parent


def generate(all_settings):
    target_dir = SUBLEMON / ".generated" / "settings"
    shutil.rmtree(target_dir, ignore_errors=True)
    target_dir.mkdir(exist_ok=True, parents=True)

    for scope, settings in all_settings.items():
        write_settings(scope, settings, target_dir)


def write_settings(scope, settings, target_dir):
    sublime_settings = settings.copy()
    repack_comments(sublime_settings)

    path = target_dir / f"{scope}.tmPreferences"

    with path.open(mode="wb") as pfile:
        plistlib.dump({"scope": scope, "settings": sublime_settings}, pfile)

    print("Generated", path.name)


def repack_comments(settings):
    shell_variables = []
    comment_index = 1

    def add_comment(variant, value):
        name = f"TM_COMMENT_{variant}_{comment_index}"
        shell_variables.append({"name": name, "value": value})

    def wrap(value):
        return [value] if isinstance(value, str) else value

    for line_comment in wrap(settings.pop("lineComment", [])):
        add_comment("START", line_comment + " ")
        comment_index += 1

    if block_comment := settings.pop("blockComment", None):
        add_comment("START", block_comment[0])
        add_comment("END", block_comment[1])

    if shell_variables:
        settings["shellVariables"] = shell_variables


# fmt: off
generate({
    "meta.symbol.sublime-syntax entity.name": {
        "showInSymbolList": 1
    },
    "text.rfc entity.name.title": {
        "showInSymbolList": 1
    },
    "source.ini": {
        "lineComment": ("#", ";")
    },
    "source.ini entity.name.section": {
        "showInSymbolList": 1
    },
    "source.unix": {
        "lineComment": "#"
    },
    "source.powershell": {
        "lineComment": "#",
        "blockComment": ("<#", "#>")
    },
    "source.python": {
        "increaseIndentPattern": r"^(\s*(class|(\basync\s+)?(def|for|with)|elif|else|except|finally|if|try|while)\b.*:|.*[\{\[])\s*$",
        "decreaseIndentPattern": r"^\s*((elif|else|except|finally)\b.*:|[\}\]])",
    },
    "source.dockerfile": {
        "lineComment": "#"
    },
})
