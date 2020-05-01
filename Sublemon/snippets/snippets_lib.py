import hashlib
import json
import re
import shutil
import xml.etree.ElementTree as ET
from contextlib import contextmanager
from pathlib import Path

GENERATED_DIR = Path(".generated")


def _write_snippet(scope, tab_trigger, content, description):
    content = content.replace('    ', '\t').strip()

    root = ET.Element('snippet')
    ET.SubElement(root, 'description').text = description
    ET.SubElement(root, 'tabTrigger').text = tab_trigger
    ET.SubElement(root, 'scope').text = scope
    ET.SubElement(root, 'content').text = content

    digest = hashlib.sha1(content.encode('ascii')).hexdigest()
    path = GENERATED_DIR / scope / f"{digest}.sublime-snippet"

    print(f"{path.name}: {description}")

    ET.ElementTree(root).write(path)


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
            description = re.search(r'^@?[-\w\s\.]+|.*', snippet).group().strip()

        snippet = snippet.replace('$FILENAME', r'${TM_FILENAME/(.*?)(\..+)/$1/}')

        _write_snippet(self.scope, self.tab_trigger, snippet, description)


class SnippetDefinition:
    def __init__(self, scope, mutators=()):
        self.scope = scope
        self.mutators = mutators

    def __truediv__(self, other):
        if callable(other):
            return SnippetDefinition(self.scope, self.mutators + (other,))
        return SnippetWriter(self.scope, other, self.mutators)


class Snippets(SnippetDefinition):
    def __init__(self, scope, mutators=()):
        super().__init__(scope, mutators)

        self.target_dir = GENERATED_DIR / scope

        shutil.rmtree(self.target_dir, ignore_errors=True)
        self.target_dir.mkdir(exist_ok=True, parents=True)

    def subscope(self, scope):
        return Snippets(f"{self.scope} {scope}", self.mutators)

    @contextmanager
    def completions(self):
        cmp = Completions(self.scope)
        try:
            yield cmp
        finally:
            cmp.write(self.target_dir)


# pylint: disable=multiple-statements
def blk(text): return text + ' {\n\t$0\n}'
def bls(text): return text + ' { $0 }'
def blp(text): return text + ' (\n\t$0\n)'
def scl(text): return text + ';'
def spc(text): return text + ' $0'
def slp(text): return text + '(${0:$SELECTION})'
def ind(text): return text.replace('>=>', '\n\t').replace('==>', '\n')
# pylint: enable=multiple-statements


class Completions():
    def __init__(self, scope):
        self.content = dict(scope=scope, completions=[])

    def write(self, target_dir):
        path = target_dir / "completions.sublime-completions"

        with path.open(mode='w') as json_file:
            json.dump(self.content, json_file, indent=2)

        print(path.name)

    def group(self, kind, *items):
        for item in items:
            completion = {
                "trigger": item,
                "content": item,
                "kind": kind
            }
            self.content["completions"].append(completion)
