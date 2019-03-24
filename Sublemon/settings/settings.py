import os
import plistlib
import re
import shutil

TARGET_DIRECTORY = '.generated'


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

    to_uppercase_pattern = re.compile(r'_[a-z]')

    for k, v in custom_settings.items():
        k = to_uppercase_pattern.sub(lambda m: m.group(0)[1].upper(), k)

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

    path = os.path.join(TARGET_DIRECTORY, scope + '.tmPreferences')
    path = os.path.abspath(path)

    with open(path, "wb") as pfile:
        plistlib.dump({'scope': scope, 'settings': sublime_settings}, pfile)

    print('Generated', path)


shutil.rmtree(TARGET_DIRECTORY, ignore_errors=True)
os.mkdir(TARGET_DIRECTORY)


settings("meta.context.sublime-syntax entity.name.key",
    show_in_symbol_list=1,
    show_in_indexed_symbol_list=1
)

settings("source.ini",
    line_comment = [';', '#']
)

settings("source.ini entity.name.section",
    show_in_symbol_list = 1
)

settings("source.unix",
    line_comment = '#'
)

settings("text.rfc entity.name.title",
    show_in_symbol_list = 1
)

settings("source.powershell",
    line_comment = '#',
    block_comment = ['<#', '#>']
)
