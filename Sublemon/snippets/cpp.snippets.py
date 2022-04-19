from snippets import Icon, generate

snippets = {
    "pl": "std::cout << $SEL0 << std::endl;",
    "dc": ("doc comment", R"/**-->${SELECTION/^\s*/ * /mg}$0--> */"),
    "main": ("main", "int main(${1:int argc, char* argv[]}) {}"),
    "fn": ("function", "${1:void} ${2:run}($3) {}"),
    ";;": ("i = 0; i < imax; i++", "${1:size_t} ${2:i} = 0; $2 < ${3:imax}; ${4:$2++}"),
    "inc": ("#include <header>", "#include <$SEL0>"),
    "inq": ('#include "header"', '#include "$SEL0"'),
    "ifd": ("#ifdef X ... #endif", "#ifdef $1<->#endif"),
}

completions = {
    ("Keyword", Icon.KEYWORD): [
        "break",
        "continue",
        "default",
        "delete",
        "namespace",
        "new",
        "return",
        "template",
        "throw",
        "typedef",
        "using",
    ],
    ("Modifier", Icon.ACCESS_MODIFIER): [
        "private",
        "protected",
        "public",
    ],
    ("Modifier", Icon.MODIFIER): [
        "const",
        "constexpr",
        "explicit",
        "override",
        "static",
        "thread_local",
        "typename",
        "unsigned",
        "virtual",
        "volatile",
    ],
    ("Cast", Icon.CONVERT): [
        "const_cast",
        "reinterpret_cast",
        "static_cast",
    ],
    ("Function", Icon.FUNCTION): [
        "defined",
        "make_shared",
        "sizeof",
    ],
    ("Block", Icon.BLOCK): [
        "catch (${1:const std::exception& e}) {}",
        "class $1 {};",
        "else {}",
        "for ($1) {}",
        "if ($1) {}",
        "namespace $1 {}",
        "struct $1 {};",
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


def expand_braces_with_semicolon(content):
    return content[:-3] + "{\n\t$0\n};" if content.endswith(" {};") else content


generate("source.c++", snippets, completions, mutators=(expand_braces_with_semicolon,))
