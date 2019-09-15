import os

import sublime

RUNNING_ON_WINDOWS = sublime.platform() == 'windows'
HOME_PATH = os.environ['USERPROFILE' if RUNNING_ON_WINDOWS else 'HOME']
