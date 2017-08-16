import hashlib
import os
import shutil

import xml.etree.ElementTree as ET


TARGET_DIRECTORY = '.generated_snippets'


def generate_filename(content):
    return hashlib.sha1(content.encode('ascii')).hexdigest() + ".sublime-snippet"


def setup():
    shutil.rmtree(TARGET_DIRECTORY, ignore_errors=True)
    os.mkdir(TARGET_DIRECTORY)


def scope(s):
    global global_scope
    global_scope = s


def snippet(tabTrigger, content, description=None, scope=None):
    content = content.replace('    ', '\t')
    if content[0] == '\n':
        content = content[1:]
    if content[-1] == '\n':
        content = content[:-1]

    scope = global_scope if scope is None else scope
    description = description if description is not None else content.strip()

    root = ET.Element('snippet')
    ET.SubElement(root, 'description').text = description
    ET.SubElement(root, 'tabTrigger').text = tabTrigger
    ET.SubElement(root, 'scope').text = scope
    ET.SubElement(root, 'content').text = content

    filename = generate_filename(scope + content)
    print("{}: {}".format(filename, description))

    ET.ElementTree(root).write(os.path.join(TARGET_DIRECTORY, filename))
