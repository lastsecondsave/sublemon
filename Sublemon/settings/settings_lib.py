import os
import plistlib
import re

TO_UPPERCASE = re.compile(r'_[a-z]')

PIPE_SEPARATED = ['increaseIndentPattern',
                  'decreaseIndentPattern',
                  'bracketIndentNextLinePattern',
                  'disableIndentNextLinePattern',
                  'unIndentedLinePattern']


def settings(scope, **custom_settings):
    sublime_settings = {}

    comments = extract_comments(custom_settings)
    if comments:
        sublime_settings['shellVariables'] = comments

    for key, val in custom_settings.items():
        key = TO_UPPERCASE.sub(lambda m: m.group(0)[1].upper(), key)

        if key in PIPE_SEPARATED:
            val = '|'.join(wrap(val))
        elif key == 'symbolTransformation':
            val = ';'.join(wrap(val)) + ';'

        sublime_settings[key] = val

    filename = scope + '.tmPreferences'
    os.makedirs('.generated', exist_ok=True)
    path = os.path.join('.generated', filename)

    with open(path, 'wb') as pfile:
        plistlib.dump({'scope': scope, 'settings': sublime_settings}, pfile)

    print('Generated', filename)


def wrap(value):
    return value if isinstance(value, (list, tuple)) else (value,)


def extract_comments(custom_settings):
    shell_variables = []
    comment_index = 1

    def add_comment(variant, value):
        name = 'TM_COMMENT_{}_{}'.format(variant, comment_index)
        shell_variables.append({'name': name, 'value': value})

    def add_start_comment(value):
        add_comment('START', value + ' ')

    def add_end_comment(value):
        add_comment('END', ' ' + value)

    for line_comment in wrap(custom_settings.pop('line_comment', [])):
        add_start_comment(line_comment)
        comment_index += 1

    if 'block_comment' in custom_settings:
        block_comment = custom_settings.pop('block_comment')
        add_start_comment(block_comment[0])
        add_end_comment(block_comment[1])

    return shell_variables
