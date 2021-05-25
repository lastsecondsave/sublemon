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
    "source.cmake",
    snippets={
        "pl": "message($SEL0)",
    },
    completions={
        ("Function", Icon.FUNCTION): [
            "add_executable()",
            "add_library()",
            "add_subdirectory()",
            "target_include_directories()",
            "target_link_directories()",
            "target_link_libraries()",
            "target_sources()",
        ],
        ("Block", Icon.BLOCK): [
            "if($1)<=>endif()",
        ],
        ("Variable", Icon.VARIABLE): [
            "CMAKE_BINARY_DIR",
            "CMAKE_CURRENT_BINARY_DIR",
            "CMAKE_CURRENT_SOURCE_DIR",
            "CMAKE_SOURCE_DIR",
        ]
    },
)

generate(
    "source.cmake meta.function-call",
    completions={
        ("Constant", Icon.ACCESS_MODIFIER): [
            "PUBLIC",
            "PRIVATE",
            "INTERFACE",
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
