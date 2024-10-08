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
            "ifndef $1<->endif",
            'ifeq "$1" "$2"<->endif',
            'ifneq "$1" "$2"<->endif',
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
            "error",
            "info",
            "patsubst",
            "subst",
            "warning",
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
    completions={
        ("Block", Icon.BLOCK): [
            "else {}",
            "for ($1) {}",
            "if ($1) {}",
            "switch ($1) {}",
            "while ($1) {}",
            ("elif", "else if ($1) {}"),
        ],
    },
)

generate(
    "text.html.markdown",
    snippets={
        "cf": ("code fence", "```$1-->$SEL0-->```"),
        "ln": ("link", "[$SEL1]($2)"),
        "bd": ("bold", "**$SEL1**"),
        "it": ("italic", "_$SEL1_"),
        "tb": ("table", "| $0 |  |\n|--|--|\n|  |  |"),
    },
)

generate("source.makefile", snippets={"ph": ".PHONY: "})

generate(
    "source.sublime-project meta.mapping.key string.quoted",
    completions={
        ("Property", Icon.NAMESPACE): [
            "build_systems",
            "folders",
            "settings",
        ],
        ("Property", Icon.PROPERTY): [
            "binary_file_patterns",
            "cancel",
            "cmd",
            "encoding",
            "file_include_patterns",
            "file_patterns",
            "file_regex",
            "folder_exclude_patterns",
            "folder_include_patterns",
            "follow_symlinks",
            "index_exclude_patterns",
            "index_include_patterns",
            "line_regex",
            "name",
            "shell_cmd",
            "syntax",
            "target",
            "variants",
            "working_dir",
        ],
    },
)

generate(
    "source.sublime-project meta.mapping.value string.quoted",
    completions={
        ("Variable", Icon.VARIABLE): [
            "file",
            "file_base_name",
            "file_extension",
            "file_name",
            "file_path",
            "folder",
            "packages",
            "platform",
            "project",
            "project_base_name",
            "project_extension",
            "project_name",
            "project_path",
        ],
    },
)
