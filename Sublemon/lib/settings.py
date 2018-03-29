import hashlib
import os
import plistlib
import re
import shutil

TARGET_DIRECTORY = '.generated_settings'
TO_UPPERCASE_PATTERN = re.compile(r'_[a-z]')


def generate_filename(scope):
    return hashlib.sha1(scope.encode('ascii')).hexdigest() + ".tmPreferences"


def generate_settings_file(scope, content):
    filename = generate_filename(scope)
    print("{}: {}".format(filename, scope))

    path = os.path.join(TARGET_DIRECTORY, filename)
    with open(path, "wb") as pfile:
        plistlib.dump(content, pfile)


def settings(scope, **custom_settings):
    shell_variables = []
    comment_index = 1

    def add_comment(variant, value):
        name = 'TM_COMMENT_{}_{}'.format(variant, comment_index)
        shell_variables.append({'name': name, 'value': value})

    def add_start_comment(value):
        add_comment('START', value + ' ')

    def add_end_comment(value):
        add_comment('END', ' ' + value)

    line_comments = custom_settings.pop('line_comment', [])
    if not isinstance(line_comments, list):
        line_comments = [line_comments]

    for line_comment in line_comments:
        add_start_comment(line_comment)
        comment_index += 1

    if 'block_comment' in custom_settings:
        block_comment = custom_settings.pop('block_comment')
        add_start_comment(block_comment[0])
        add_end_comment(block_comment[1])

    sublime_settings = {}

    if shell_variables:
        sublime_settings['shellVariables'] = shell_variables

    for k, v in custom_settings.items():
        k = TO_UPPERCASE_PATTERN.sub(lambda m: m.group(0)[1].upper(), k)

        if isinstance(v, list):
            if k in ['increaseIndentPattern',
                     'decreaseIndentPattern',
                     'bracketIndentNextLinePattern',
                     'disableIndentNextLinePattern',
                     'unIndentedLinePattern']:
                v = '|'.join(v)
            elif k == 'symbolTransformation':
                v = ';'.join(v) + ';'

        sublime_settings[k] = v

    generate_settings_file(scope, {'scope': scope, 'settings': sublime_settings})


shutil.rmtree(TARGET_DIRECTORY, ignore_errors=True)
os.mkdir(TARGET_DIRECTORY)
