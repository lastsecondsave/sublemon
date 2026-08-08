import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

# pylint: disable=unspecified-encoding

SUBLEMON = Path(__file__).resolve().parent.parent
PACKAGES = SUBLEMON.parent


BUILDS = "__BUILDS__"
COMPLETIONS = "__COMPLETIONS__"
KEYMAPS = "__KEYMAPS__"


def system_package(name):
    if sys.platform == "win32":
        root = "C:/Program Files/Sublime Text"
    elif sys.platform == "darwin":
        root = "/Applications/Sublime Text.app/Contents/MacOS"
    else:
        root = "/opt/sublime_text"

    return Path(root) / "Packages" / f"{name}.sublime-package"


def system_package_zip(name):
    return zipfile.ZipFile(system_package(name))


def installed_package(name):
    if sys.platform == "win32":
        root = "AppData/Roaming/Sublime Text"
    elif sys.platform == "darwin":
        root = "Library/Application Support/Sublime Text"
    else:
        root = ".config/sublime-text"

    return Path.home() / root / "Installed Packages" / f"{name}.sublime-package"


def execute(script):
    print(f"Running {script}:")
    subprocess.call([sys.executable, script.name], cwd=script.parent)
    print()


def generate_files():
    shutil.rmtree(SUBLEMON / ".generated", ignore_errors=True)

    execute(PACKAGES / "Disco" / "src" / "disco.py")
    execute(SUBLEMON / "scripts" / "settings.py")

    for snippet in (SUBLEMON / "snippets").glob("*.snippets.py"):
        execute(snippet)


def mute(package, *items):
    for item in items:
        if item is BUILDS:
            mute_extension(package, "sublime-build")
        elif item is COMPLETIONS:
            mute_extension(package, "sublime-completions")
        elif item is KEYMAPS:
            mute_extension(package, "sublime-keymap")
        else:
            mute_path(package, item)


def mute_path(package, path):
    path = PACKAGES.joinpath(package, path)
    path.parent.mkdir(exist_ok=True, parents=True)

    if (ext := path.suffix) == ".sublime-build":
        path.write_text('{"selector": "_"}')
    elif ext == ".sublime-keymap":
        path.write_text("[]")
    elif ext == ".sublime-completions":
        path.write_text("{}")
    elif ext == ".tmPreferences":
        path.write_text(
            "<plist><dict>"
            "<key>scope</key><string>_</string>"
            "<key>settings</key><dict/>"
            "</dict></plist>"
        )
    else:
        path.write_text("")

    print(f"Muted {path}")


def mute_extension(package, extension):
    pkg_file = system_package(package)
    if not pkg_file.exists():
        pkg_file = installed_package(package)

    with zipfile.ZipFile(pkg_file) as pkg:
        paths = [n for n in pkg.namelist() if n.endswith(extension)]

    for path in paths:
        mute_path(package, path)


def mute_files():
    mute(
        "ShellScript",
        COMPLETIONS,
        KEYMAPS,
        "Bash/Completion Rules.tmPreferences",
        "Zsh/Completion Rules.tmPreferences",
    )

    mute(
        "Markdown",
        KEYMAPS,
        "Symbol List - Reference Link.tmPreferences",
    )

    mute("Python", BUILDS, "Indentation Rules.tmPreferences")
    mute("C++", BUILDS, "Symbol List - Indent Class Methods.tmPreferences")
    mute("Java", BUILDS, COMPLETIONS)
    mute("CMake", COMPLETIONS)
    mute("Go", COMPLETIONS)
    mute("Makefile", BUILDS)
    mute("PowerShell", BUILDS, COMPLETIONS)


def patch_syntax(package, *patches):
    with system_package_zip(package) as pkg:
        syntax = (zipfile.Path(pkg) / f"{package}.sublime-syntax").read_text()

    for pattern, repl in patches:
        syntax = re.sub(pattern, repl, syntax)

    syntax_path = PACKAGES / package / f"{package}.sublime-syntax"
    syntax_path.parent.mkdir(exist_ok=True)
    syntax_path.write_text(syntax)

    print(f"Patched {syntax_path}")


def patch_syntaxes():
    patch_syntax(
        "Python", (r"(set: (?:.+-)?quoted)(-raw-\w-string-body)", r"\1-plain\2")
    )


def unpack_icons():
    with system_package_zip("Theme - Default") as pkg:
        icons = [name for name in pkg.namelist() if name.startswith("icons/")]
        pkg.extractall(path=PACKAGES / "Disco", members=icons)

    print(f"Copied {len(icons)} icons from the default theme")


def override_macos_keymap():
    with system_package_zip("Default") as pkg:
        keymap = Path(
            pkg.extract(
                "Default (Windows).sublime-keymap",
                path=PACKAGES / "Default",
            )
        )
        keymap.rename(keymap.parent / "Default (OSX).sublime-keymap")

    print("Copied the macOS keymap")


def main():
    generate_files()
    mute_files()
    patch_syntaxes()
    unpack_icons()

    if sys.platform == "darwin":
        override_macos_keymap()


if __name__ == "__main__":
    main()
