import shutil
import subprocess
import sys
from pathlib import Path

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


def mute(path):
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


def mute_files():
    mute(PACKAGES / "Python" / "Python.sublime-build")
    mute(PACKAGES / "Python" / "Indentation Rules.tmPreferences")

    mute(PACKAGES / "Rust" / "Default.sublime-keymap")

    mute(PACKAGES / "Markdown" / "Default.sublime-keymap")

    mute(PACKAGES / "Java" / "Ant.sublime-build")
    mute(PACKAGES / "Java" / "JavaC.sublime-build")
    mute(PACKAGES / "Java" / "Java.sublime-completions")

    mute(PACKAGES / "CMake" / "CMake.sublime-completions")
    mute(PACKAGES / "CMake" / "CMakeVariables.sublime-completions")

    mute(PACKAGES / "C++" / "C++ Single File.sublime-build")

    mute(PACKAGES / "Go" / "Go.sublime-completions")


if __name__ == "__main__":
    generate_files()
    mute_files()
