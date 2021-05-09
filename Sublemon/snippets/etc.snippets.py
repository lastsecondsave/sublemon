from snippets import Icon, generate

generate(
    "source.regexp",
    snippets={
        "?>": ("atomic group", "(?>$SEL0)"),
        "?=": ("lookahead", "(?=$SEL0)"),
        "?:": ("non-capturing group", "(?:$SEL0)"),
    },
)

generate(
    "text.xml",
    snippets={
        "cdata": ("CDATA", "<![CDATA[$SEL0]]>"),
        "xml": ("xml declaration", '<?xml version="1.0" encoding="UTF-8"?>'),
    },
)

generate(
    "source.makefile",
    completions={
        ("Block", Icon.BLOCK): [
            "define $1<->endef",
            "ifdef $1<->endif",
            'ifeq "$1" "$2"<->endif',
        ]
    },
)

generate(
    "source.makefile meta.function-call",
    completions={
        ("Function", Icon.FUNCTION): [
            "addprefix",
            "addsuffix",
            "call",
            "patsubst",
            "subst",
        ]
    },
)

generate(
    "source.rust",
    snippets={
        "pl": 'println!("{}", $SEL0);',
    },
)

generate(
    "source.js",
    snippets={
        "pl": "console.log($SEL0);",
    },
)
