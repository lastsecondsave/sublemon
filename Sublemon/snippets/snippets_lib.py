import hashlib
import os
import re
import shutil

import xml.etree.ElementTree as ET

CLEANUP = re.compile(r'(\$(\{[^\}]+?\}|\d)\s*)|[\t\n]|\s*:\n')


def _generate_filename(content):
    return hashlib.sha1(content.encode('ascii')).hexdigest() + ".sublime-snippet"


def _write_snippet(scope, tab_trigger, content, description):
    content = content.replace('    ', '\t').strip()

    root = ET.Element('snippet')
    ET.SubElement(root, 'description').text = description
    ET.SubElement(root, 'tabTrigger').text = tab_trigger
    ET.SubElement(root, 'scope').text = scope
    ET.SubElement(root, 'content').text = content

    filename = _generate_filename(scope + content)
    print("{}: {}".format(filename, description))

    ET.ElementTree(root).write(os.path.join('.generated', scope, filename))


def _clean_target(scope):
    target_dir = os.path.join('.generated', scope)
    shutil.rmtree(target_dir, ignore_errors=True)
    os.makedirs(target_dir)
    return target_dir


class SnippetWriter:
    def __init__(self, scope, tab_trigger, mutators):
        self.scope = scope
        self.tab_trigger = tab_trigger
        self.mutators = mutators

    def __sub__(self, content):
        description, snippet = content if isinstance(content, tuple) else (None, content)

        for mutate in self.mutators:
            snippet = mutate(snippet)

        if not description:
            description = CLEANUP.sub('', snippet).strip()

        snippet = snippet.replace('$FILENAME', r'${TM_FILENAME/(.*?)(\..+)/$1/}')

        _write_snippet(self.scope, self.tab_trigger, snippet, description)


class SnippetDefinition:
    def __init__(self, scope, mutators=()):
        self.scope = scope
        self.mutators = mutators

    def __truediv__(self, other):
        if callable(other):
            return SnippetDefinition(self.scope, self.mutators + (other,))
        else:
            return SnippetWriter(self.scope, other, self.mutators)


class Snippets(SnippetDefinition):
    def __init__(self, scope, mutators=()):
        super().__init__(scope, mutators)
        _clean_target(scope)

    def subscope(self, scope):
        return Snippets(self.scope + ' ' + scope, self.mutators)

# pylint: disable=multiple-statements

def blk(text): return text + ' {\n\t$0\n}'
def bls(text): return text + ' { $0 }'
def scl(text): return text + ';'
def spc(text): return text + ' $0'
def slp(text): return text + '(${0:$SELECTION})'
def ind(text): return text.replace('>=>', '\n\t').replace('==>', '\n')
