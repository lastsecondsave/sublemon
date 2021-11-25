from snippets import Icon, generate

snippets = {
    "pl": "std::cout << $SEL0 << std::endl;",
    "dc": ("doc comment", r"/**-->${SELECTION/^\s*/ * /mg}$0--> */"),
    "main": ("main", "int main(${1:int argc, char *argv[]}) {}"),
    "fun": ("function", "${1:void} ${2:run}($3) {}"),
    ";;": ("i = 0; i < imax; i++", "${1:size_t} ${2:i} = 0; $2 < ${3:imax}; ${4:$2++}"),
}

completions = {
    ("Keyword", Icon.KEYWORD): [
        "break",
        "continue",
        "delete",
        "new",
        "return",
        "throw",
    ],
    ("Modifier", Icon.ACCESS_MODIFIER): [
        "const",
        "constexpr",
        "override",
        "private",
        "protected",
        "public",
        "static",
        "thread_local",
        "virtual",
        "volatile",
    ],
    ("Modifier", Icon.MODIFIER): [
        "typename",
        "unsigned",
    ],
    ("Cast", Icon.CONVERT): [
        "const_cast",
        "reinterpret_cast",
        "static_cast",
    ],
    ("Function", Icon.FUNCTION): [
        "defined",
        "sizeof",
    ],
    ("Block", Icon.BLOCK): [
        "catch (${1:const std::exception& e}) {}",
        "class $1 {}",
        "else {}",
        "for ($1) {}",
        "if ($1) {}",
        "namespace $1 {}",
        "struct $1 {}",
        "switch ($1) {}",
        "try {}",
        "while ($1) {}",
        ("elif", "else if ($1) {}"),
    ],
    ("Macros", Icon.META): [
        "define",
        "endif",
        "ifdef",
        "include",
        "pragma",
    ],
    ("Namespace", Icon.NAMESPACE): [
        "std",
    ],
    ("Class", Icon.TYPE): [
        "auto",
        "shared_ptr",
        "string",
        "typedef",
        "unique_ptr",
        "unordered_map",
        "unordered_set",
        "vector",
    ],
    ("Type", Icon.PRIMITIVE_TYPE): [
        "bool",
        "char",
        "double",
        "float",
        "int",
        "int16_t",
        "int32_t",
        "int64_t",
        "int8_t",
        "long",
        "size_t",
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
