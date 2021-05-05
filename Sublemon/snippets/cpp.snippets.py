from snippets import *

snippets = {
    "pl": "std::cout << $SEL0 << std::endl;",
    "dc": ("doc comment", r"/**>>=${SELECTION/^\s*/ * /mg}$0>>= */"),
}

completions = {
    kind(ICON_KEYWORD, "Keyword"): [
        "break",
        "continue",
        "return",
    ],
    kind(ICON_CONVERT, "Cast"): [
        "const_cast<$1>",
        "reinterpret_cast<$1>",
        "static_cast<$1>",
    ],
    kind(ICON_BLOCK, "Block"): [
        "else ($1) {}",
        "for ($1) {}",
        "if ($1) {}",
        "while ($1) {}",
    ],
    kind(ICON_MACROS, "Macros"): [
        "#include",
        "#ifdef",
        "#endif",
    ],
}

generate("source.c++", snippets, completions)
