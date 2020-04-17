import subprocess
import sys

from pathlib import Path

SUBLEMON = Path(__file__).parent.parent
PACKAGES = SUBLEMON.parent


def execute(script):
    print(f"Running {script}:")
    subprocess.call([sys.executable, script.name], cwd=script.parent)
    print()


def generate_files():
    execute(SUBLEMON / "disco" / "disco.py")
    execute(SUBLEMON / "settings" / "settings.py")

    for snippet in (SUBLEMON / "snippets").glob("*.snippets.py"):
        execute(snippet)


def mute(path):
    path.parent.mkdir(exist_ok=True, parents=True)

    if path.name.endswith("build"):
        path.write_text(r'{"selector": "_"}')
    elif path.name.endswith("keymap"):
        path.write_text("[]")
    else:
        path.touch(exist_ok=True)

    print(f"Muted {path}")


def mute_files():
    mute(PACKAGES / "Python" / "Python.sublime-build")

    mute(PACKAGES / "Rust" / "Default.sublime-keymap")

    mute(PACKAGES / "Java" / "Ant.sublime-build")
    mute(PACKAGES / "Java" / "JavaC.sublime-build")
    mute(PACKAGES / "Java" / "Java.sublime-completions")


if __name__ == "__main__":
    generate_files()
    mute_files()
