import sys
from pathlib import Path
from zipfile import ZipFile

DISCO_PACKAGE = Path(__file__).resolve().parent.parent
SUBLIME_PATH = Path(
    "C:/Program Files/Sublime Text" if sys.platform == "win32" else "/opt/sublime_text"
)


def copy_default_icons():
    theme_path = SUBLIME_PATH / "Packages" / "Theme - Default.sublime-package"

    with ZipFile(theme_path) as theme_zip:
        icons = [name for name in theme_zip.namelist() if name.startswith("icons/")]
        theme_zip.extractall(path=DISCO_PACKAGE, members=icons)

        print(f"Copied {len(icons)} icons from {theme_path}")


if __name__ == "__main__":
    copy_default_icons()
