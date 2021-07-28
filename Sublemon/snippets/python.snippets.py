from snippets import Icon, generate

snippets = {
    "pl": "print($SEL0)",
    "ss": ("self.x = x", "self.$1 = $1"),
    "pld": ("pylint disable", "# pylint: disable="),
    "main": ('if __name__ == "__main__"', 'if __name__ == "__main__":==>${0:main()}'),
    "fi": ("from import", "from $1 import $0"),
    "init": ("__init__", "def __init__(self$1):"),
    "ie": ("if x else y", "if $1 else $0"),
    "lm": "lambda ${1:x}: ${0:None}",
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
        "class $1:",
        "def ${1:run}($2):",
        "elif $1:",
        "else:",
        "except",
        "for $1 in $2:",
        "if $1:",
        "try:",
        "while $1:",
        "with $1 as $2:",
    ],
    ("Support", Icon.FUNCTION): [
        "__init__",
        "isinstance",
        "super",
    ],
    ("Decorator", Icon.META): [
        "classmethod",
        "contextmanager",
        "dataclass",
        "property",
        "staticmethod",
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


generate("source.python", snippets, completions, mutators=[expand_colon])
