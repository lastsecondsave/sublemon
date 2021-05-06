from snippets import DEFAULT_MUTATORS, Icon, generate

snippets = {
    "pl": "print($SEL0)",
    "ss": ("self.x = x", "self.$1 = $1"),
    "pld": ("pylint disable", "# pylint: disable="),
    "main": ('if __name__ == "__main__"', 'if __name__ == "__main__":==>${0:main()}'),
    "fi": ("from import", "from $1 import $0"),
    "init": ("__init__", "def __init__(self$1):"),
}

completions = {
    ("Keyword", Icon.KEYWORD): [
        "break",
        "continue",
        "from",
        "import",
        "pass",
        "raise",
        "return",
        "yeild",
    ],
    ("Block", Icon.BLOCK): [
        "elif $1:",
        "else:",
        "for $1 in $2:",
        "if $1:",
        "while $1:",
    ],
    ("Storage", Icon.STORAGE): [
        "def ${1:run}($2):",
        "class ${1:Item}($2):",
    ],
    ("Support", Icon.FUNCTION): [
        "isinstance($1, ${2:str})",
    ],
    ("Decorator", Icon.META): [
        "@classmethod",
        "@dataclass",
        "@staticmethod",
    ],
    ("Constant", Icon.CONSTANT): [
        "False",
        "None",
        "True",
    ],
    ("Variable", Icon.VARIABLE): [
        "self",
    ],
}


def expand_colon(content):
    return content + "\n\t${0:pass}" if content.endswith(":") else content


generate(
    "source.python", snippets, completions, mutators=(*DEFAULT_MUTATORS, expand_colon)
)
