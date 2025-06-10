import shutil
import subprocess
import sys
from pathlib import Path
from zipfile import ZipFile

# pylint: disable=unspecified-encoding

SUBLEMON = Path(__file__).resolve().parent.parent
PACKAGES = SUBLEMON.parent


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


def mute(*path):
    path = PACKAGES.joinpath(*path)
    path.parent.mkdir(exist_ok=True, parents=True)

    if (ext := path.suffix) == ".sublime-build":
        path.write_text('{"selector": "_"}')
    elif ext == ".sublime-keymap":
        path.write_text("[]")
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


def mute_in_package(package, file_type):
    pkg_file = system_package(package)
    if not pkg_file.exists():
        pkg_file = installed_package(package)

    with ZipFile(pkg_file) as pkg:
        completions = [n.split("/") for n in pkg.namelist() if n.endswith(file_type)]

    for path in completions:
        mute(package, *path)


def mute_completions(package):
    mute_in_package(package, "sublime-completions")


def mute_builds(package):
    mute_in_package(package, "sublime-build")


def mute_files():
    mute_builds("Python")
    mute("Python", "Indentation Rules.tmPreferences")

    mute_completions("ShellScript")
    mute("ShellScript", "Default.sublime-keymap")
    mute("ShellScript", "Bash", "Completion Rules.tmPreferences")
    mute("ShellScript", "Zsh", "Completion Rules.tmPreferences")

    mute("Markdown", "Default.sublime-keymap")
    mute("Markdown", "Symbol List - Reference Link.tmPreferences")

    mute_completions("Java")
    mute_builds("Java")

    mute_completions("CMake")
    mute_completions("Go")

    mute_builds("Makefile")
    mute_builds("C++")


def system_package(name):
    if sys.platform == "win32":
        root = "C:/Program Files/Sublime Text"
    elif sys.platform == "darwin":
        root = "/Applications/Sublime Text.app/Contents/MacOS"
    else:
        root = "/opt/sublime_text"

    return Path(root) / "Packages" / f"{name}.sublime-package"


def installed_package(name):
    if sys.platform == "win32":
        root = "AppData/Roaming/Sublime Text"
    elif sys.platform == "darwin":
        root = "/Applications/Sublime Text.app/Contents/MacOS"
    else:
        root = ".config/sublime-text"

    return Path.home() / root / "Installed Packages" / f"{name}.sublime-package"


def unpack_icons():
    with ZipFile(system_package("Theme - Default")) as pkg:
        icons = [name for name in pkg.namelist() if name.startswith("icons/")]
        pkg.extractall(path=PACKAGES / "Disco", members=icons)

    print(f"Copied {len(icons)} icons from the default theme")


def override_macos_keymap():
    with ZipFile(system_package("Default")) as pkg:
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
    unpack_icons()

    if sys.platform == "darwin":
        override_macos_keymap()


if __name__ == "__main__":
    main()
