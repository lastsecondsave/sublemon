from snippets import generate

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
