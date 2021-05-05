from snippets import Icon, generate

snippets = {
    "pl": "std::cout << $SEL0 << std::endl;",
    "dc": ("doc comment", r"/**>>=${SELECTION/^\s*/ * /mg}$0>>= */"),
}

completions = {
    ("Keyword", Icon.KEYWORD): [
        "break",
        "continue",
        "return",
    ],
    ("Modifier", Icon.MODIFIER): [
        "const",
        "private",
        "protected",
        "public",
    ],
    ("Cast", Icon.CONVERT): [
        "const_cast<$1>",
        "reinterpret_cast<$1>",
        "static_cast<$1>",
    ],
    ("Block", Icon.BLOCK): [
        "else {}",
        "for ($1) {}",
        "if ($1) {}",
        "while ($1) {}",
    ],
    ("Macros", Icon.META): [
        "#include",
        "#ifdef",
        "#endif",
    ],
    ("Namespace", Icon.NAMESPACE): [
        "std::"
    ],
    ("Storage", Icon.STORAGE): [
        "class ${1:Class} {}",
        "namespace ${1:ns} {}",
        "struct ${1:Struct} {}",
    ]
}

generate("source.c++", snippets, completions)
