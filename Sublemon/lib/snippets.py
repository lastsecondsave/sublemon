import hashlib
import os
import shutil

import xml.etree.ElementTree as ET

TARGET_DIRECTORY = '.generated_snippets'


def generate_filename(content):
    return hashlib.sha1(content.encode('ascii')).hexdigest() + ".sublime-snippet"


def write_snippet(scope, tab_trigger, content, description):
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

    filename = generate_filename(scope + content)
    print("{}: {}".format(filename, description))

    ET.ElementTree(root).write(os.path.join(TARGET_DIRECTORY, filename))


class Snippets:
    def __init__(self, scope, prefix='', suffix=''):
        object.__setattr__(self, 'scope', scope)
        object.__setattr__(self, 'prefix', prefix)
        object.__setattr__(self, 'suffix', suffix)

    def _mutate(self, **kwargs):
        conf = {**self.__dict__, **kwargs}
        return Snippets(**conf)

    def with_prefix(self, prefix):
        return self._mutate(prefix=prefix)

    def with_suffix(self, suffix):
        return self._mutate(suffix=suffix)

    def subscope(self, scope):
        return self._mutate(scope=self.scope + ' ' + scope)

    def add(self, tab_trigger, content):
        conf = dict(tab_trigger=tab_trigger, scope=self.scope)

        if isinstance(content, tuple):
            write_snippet(**conf,
                          description=content[0],
                          content=self.format_content(content[1]))
        else:
            write_snippet(**conf,
                          description=content.strip(),
                          content=self.format_content(content))

    def format_content(self, content):
        return self.prefix + content + self.suffix

    def __setattr__(self, name, value):
        self.add(name, value)

    def __setitem__(self, name, value):
        self.add(name, value)


shutil.rmtree(TARGET_DIRECTORY, ignore_errors=True)
os.mkdir(TARGET_DIRECTORY)
