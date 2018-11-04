import hashlib
import os
import re
import shutil

import xml.etree.ElementTree as ET

_TARGET_DIRECTORY = '.generated_snippets'
_CLEANUP = re.compile(r'(\$(\{[^\}]+?\}|\d)\s*)|[\t\n]|\s*:\n')


def _generate_filename(content):
    return hashlib.sha1(content.encode('ascii')).hexdigest() + ".sublime-snippet"


def _write_snippet(scope, tab_trigger, content, description):
    content = content.replace('    ', '\t')
    if content[0] == '\n':
        content = content[1:]
    if content[-1] == '\n':
        content = content[:-1]

    root = ET.Element('snippet')
    ET.SubElement(root, 'description').text = description
    ET.SubElement(root, 'tabTrigger').text = tab_trigger
    ET.SubElement(root, 'scope').text = scope
    ET.SubElement(root, 'content').text = content

    filename = _generate_filename(scope + content)
    print("{}: {}".format(filename, description))

    ET.ElementTree(root).write(os.path.join(_TARGET_DIRECTORY, filename))


class Snippets:
    def __init__(self, scope, prefix='', suffix=''):
        object.__setattr__(self, 'scope', scope)
        object.__setattr__(self, 'prefix', prefix)
        object.__setattr__(self, 'suffix', suffix)

    def _mutate(self, **kwargs):
        conf = {**self.__dict__, **kwargs}
        return Snippets(**conf)

    def with_prefix(self, prefix):
        return self._mutate(prefix=prefix + self.prefix)

    def with_suffix(self, suffix):
        return self._mutate(suffix=self.suffix + suffix)

    def subscope(self, scope):
        return self._mutate(scope=self.scope + ' ' + scope)

    def add(self, tab_trigger, content):
        is_tuple = isinstance(content, tuple)

        snippet = content[1] if is_tuple else content
        snippet = self.prefix + snippet + self.suffix

        def generate_description():
            return _CLEANUP.sub('', snippet).strip()

        description = content[0] if is_tuple else generate_description()

        snippet = snippet.replace('$FILENAME', r'${TM_FILENAME/(.*?)(\..+)/$1/}')

        _write_snippet(self.scope, tab_trigger, snippet, description)

    def __setattr__(self, name, value):
        self.add(name, value)

    def __setitem__(self, name, value):
        self.add(name, value)

    def with_braces(self):
        return self.with_suffix(' {\n\t$0\n}')

    def with_same_line_braces(self):
        return self.with_suffix(' { $0 }')

    def with_selection_in_parentheses(self):
        return self.with_suffix('(${0:$SELECTION})')

    def with_space(self):
        return self.with_suffix(' ')

    def with_semicolon(self):
        return self.with_suffix(';')


shutil.rmtree(_TARGET_DIRECTORY, ignore_errors=True)
os.mkdir(_TARGET_DIRECTORY)
