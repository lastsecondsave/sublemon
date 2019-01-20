import os
import sys
import shutil

from pathlib import Path

PACKAGES_DIR = Path(os.environ['USERPROFILE']) / 'Workspace' / 'Packages'
SUBLIME_PACKAGES_DIR = Path(sys.argv[0]).parent.parent.parent

FILES_TO_COPY = [
    'Java/Java.sublime-syntax',
    'Java/syntax_test_java.java'
]

for file_to_copy in FILES_TO_COPY:
    src = PACKAGES_DIR / file_to_copy
    dst = SUBLIME_PACKAGES_DIR / file_to_copy

    dst.parent.mkdir(exist_ok=True)
    shutil.copy(str(src), str(dst))
    print('Copied', src)
