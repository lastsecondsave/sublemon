import hashlib
import os
import plistlib
import re
import shutil


def encode_filename(scope):
    return hashlib.sha1(scope.encode('ascii')).hexdigest() + ".tmPreferences"


def write_plist(path, content):
    with open(path, "wb") as pfile:
        plistlib.dump(content, pfile)


def generate_settings_file(scope, settings):
    filename = encode_filename(scope)
    print("{}: {}".format(filename, scope))
    write_plist(os.path.join("generated", filename), settings)


def cleanup():
    shutil.rmtree("generated", ignore_errors=True)
    os.mkdir("generated")


TO_UPPERCASE_PATTERN = re.compile(r'_[a-z]')


def entry(scope, **settings):
    shell_variables = []
    comment_index = 1

    def add_comment(variant, value):
        name = 'TM_COMMENT_{}_{}'.format(variant, comment_index)
        shell_variables.append({'name': name, 'value': value})

    def add_start_comment(value):
        add_comment('START', value + ' ')

    def add_end_comment(value):
        add_comment('END', ' ' + value)

    line_comments = settings.pop('line_comment', [])
    if not isinstance(line_comments, list):
        line_comments = [line_comments]

    for line_comment in line_comments:
        add_start_comment(line_comment)
        comment_index += 1

    if 'block_comment' in settings:
        block_comment = settings.pop('block_comment')
        add_start_comment(block_comment[0])
        add_end_comment(block_comment[1])

    sublime_settings = {}

    if shell_variables:
        sublime_settings['shellVariables'] = shell_variables

    for k, v in settings.items():
        k = TO_UPPERCASE_PATTERN.sub(lambda m: m.group(0)[1].upper(), k)

        if isinstance(v, list):
            if k in ['increaseIndentPattern', 'decreaseIndentPattern']:
                v = '|'.join(v)
            elif k == 'symbolTransformation':
                v = ';'.join(v) + ';'

        sublime_settings[k] = v

    generate_settings_file(scope, dict(scope=scope, settings=sublime_settings))
