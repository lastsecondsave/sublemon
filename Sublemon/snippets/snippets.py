import hashlib
import json
import re
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

GENERATED_DIR = Path(".generated")
FIRST_WORD_PATTERN = re.compile(r"^[#@]?([\w\-:\.]+\w)")


class Icon:
    KEYWORD = ""
    MODIFIER = ""
    BLOCK = ""
    CONVERT = ""
    META = ""
    NAMESPACE = ""
    FUNCTION = ""
    STORAGE = ""
    ENTITY = ""


def expand_custom_variables(content):
    content = content.replace("$FILENAME", r"${TM_FILENAME/(.*?)(\..+)/$1/}")
    return content.replace("$SEL0", "${0:$SELECTION}")


def intent_with_tabs(content):
    return content.replace("    ", "\t")


def make_multiline(content):
    content = content.replace("==>", "\n\t").replace(">>=", "\n")
    return content.replace("<=>", "\n\t$0\n")


def expand_braces(content):
    return content[:-2] + "{\n\t$0\n}" if content.endswith(" {}") else content


DEFAULT_MUTATORS = (make_multiline, expand_braces)
MANDATORY_MUTATORS = (expand_custom_variables, intent_with_tabs)


def generate(scope, snippets=None, completions=None, mutators=DEFAULT_MUTATORS):
    mutators = [*mutators, *MANDATORY_MUTATORS]

    target_dir = GENERATED_DIR / scope
    shutil.rmtree(target_dir, ignore_errors=True)
    target_dir.mkdir(exist_ok=True, parents=True)

    if snippets:
        for trigger, snippet in snippets.items():
            snippet = prepare_snippet(scope, trigger, snippet, mutators)
            write_snippet(snippet, target_dir)

    if completions:
        prepared_completions = []

        for kind, values in completions.items():
            kind = prepare_kind(kind)
            for value in values:
                prepared_completions.append(prepare_completion(kind, value, mutators))

        write_completions(scope, prepared_completions, target_dir)


def is_collection(item):
    return isinstance(item, (tuple, list))


def get_first_word(string):
    return FIRST_WORD_PATTERN.search(string).group(1).strip()


def prepare_snippet(scope, trigger, snippet, mutators):
    description, content = snippet if is_collection(snippet) else (None, snippet)

    if not description:
        description = get_first_word(content)

    for mutate in mutators:
        content = mutate(content)

    return {
        "scope": scope,
        "tabTrigger": trigger,
        "description": description,
        "content": content,
    }


def write_snippet(snippet, target_dir):
    root = ET.Element("snippet")
    for key, value in snippet.items():
        ET.SubElement(root, key).text = value

    digest = hashlib.sha1(str(snippet).encode("ascii")).hexdigest()
    path = target_dir / f"{digest}.sublime-snippet"

    print(f"{path.name}: {snippet['description']}")

    ET.ElementTree(root).write(path)


def prepare_kind(kind):
    if isinstance(kind, str):
        return kind.split(maxsplit=2) if " " in kind else kind

    return ("snippet", kind[1], kind[0])


def prepare_completion(kind, completion, mutators):
    trigger, content = completion if is_collection(completion) else (None, completion)

    if not trigger:
        trigger = get_first_word(content)

    for mutate in mutators:
        content = mutate(content)

    return {
        "kind": kind,
        "trigger": trigger,
        "contents": content,
    }


def write_completions(scope, completions, target_dir):
    path = target_dir / "completions.sublime-completions"

    with path.open(mode="w") as json_file:
        json.dump(
            {"scope": scope, "completions": completions},
            json_file,
            indent=2,
        )

    print(path.name)
