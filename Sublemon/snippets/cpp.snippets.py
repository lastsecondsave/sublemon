from snippets import Icon, generate

snippets = {
    "pl": "std::cout << $SEL0 << std::endl;",
    "dc": ("doc comment", r"/**-->${SELECTION/^\s*/ * /mg}$0--> */"),
    "main": ("main", "int main(${1:int argc, char *argv[]}) {}"),
    "fun": ("function", "${1:void} ${2:run}($3) {}"),
}

completions = {
    ("Keyword", Icon.KEYWORD): [
        "break",
        "continue",
        "return",
        "throw",
    ],
    ("Modifier", Icon.ACCESS_MODIFIER): [
        "const",
        "private",
        "protected",
        "public",
    ],
    ("Modifier", Icon.MODIFIER): [
        "typename",
        "unsigned",
    ],
    ("Cast", Icon.CONVERT): [
        "const_cast<$1>()",
        "reinterpret_cast<$1>()",
        "static_cast<$1>()",
    ],
    ("Function", Icon.FUNCTION): [
        "defined()",
        "sizeof()",
    ],
    ("Block", Icon.BLOCK): [
        "catch (${1:const std::exception& e}) {}",
        "else {}",
        ("elif", "else if ($1) {}"),
        "for ($1) {}",
        "if ($1) {}",
        "try {}",
        "while ($1) {}",
    ],
    ("Macros", Icon.META): [
        "#define",
        "#endif",
        "#ifdef",
        "#include",
        "#pragma",
    ],
    ("Namespace", Icon.NAMESPACE): [
        "std::",
    ],
    ("Storage", Icon.STORAGE): [
        "auto",
        "class ${1:Class} {}",
        "namespace ${1:ns} {}",
        "struct ${1:Struct} {}",
    ],
    ("Class", Icon.ENTITY): [
        ("string", "std::string"),
        ("vector", "std::vector<$1>"),
    ],
    ("Type", Icon.PRIMITIVE): [
        "char",
        "double",
        "float",
        "int",
        "int16_t",
        "int32_t",
        "int64_t",
        "int8_t",
        "long",
        "uint16_t",
        "uint32_t",
        "uint64_t",
        "uint8_t",
        "void",
    ],
    ("Constant", Icon.CONSTANT): [
        "false",
        "nullptr",
        "true",
    ],
    ("Variable", Icon.VARIABLE): [
        "this",
    ],
}

generate("source.c++", snippets, completions)
