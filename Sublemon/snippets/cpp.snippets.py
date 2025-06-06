from snippets import Icon, generate

rule_of_five = """
${1:Class}() = default;
virtual ~${1:Class}() = default;
${1:Class}(const ${1:Class}&) = delete;
${1:Class}& operator=(const ${1:Class}&) = delete;
${1:Class}(${1:Class}&&) = delete;
${1:Class}& operator=(${1:Class}&&) = delete;
"""


def expand_braces_with_semicolon(content):
    return content[:-3] + "{\n\t$0\n};" if content.endswith(" {};") else content


generate(
    "source.c++",
    mutators=[expand_braces_with_semicolon],
    snippets={
        "pl": "std::cout << $SEL0 << std::endl;",
        "dc": ("doc comment", R"/**-->${SELECTION/^\s*/ * /mg}$0--> */"),
        "main": ("main", "int main(${1:int argc, char* argv[]}) {}"),
        "fn": ("function", "${1:void} ${2:run}($3) {}"),
        ";;": (
            "i = 0; i < imax; i++",
            "${1:size_t} ${2:i} = 0; $2 < ${3:imax}; ${4:++$2}",
        ),
        "inc": ("#include <header>", "#include <$SEL0>"),
        "inq": ('#include "header"', '#include "$SEL0"'),
        "ifd": ("#if defined()", "#if defined($1)<->#endif"),
        "ifnd": ("if !defined()", "#if !defined(${1:NDEBUG})<->#endif"),
        "mi": ("member init", "$1_(${2:$1})"),
        "mmi": ("member move init", "$1_(std::move(${2:$1}))"),
        "mv": "std::move($SEL0)",
        "cpc": ("copy constructor", "${1:Class}(const ${1:Class}& ${2:other})"),
        "mvc": ("move constructor", "${1:Class}(${1:Class}&& ${2:other})"),
        "cpa": (
            "copy assignment",
            "${1:Class}& operator=(const ${1:Class}& ${2:other})",
        ),
        "mva": ("move assignment", "${1:Class}& operator=(${1:Class}&& ${2:other})"),
        "rof": ("rule of five", rule_of_five),
        "tm": "template<$0>",
        "td": ("TODO", "// TODO: "),
        "lm": ("lambda", "[$1]($2) { $0 }"),
        "be": ("begin-end", "std::begin($1), std::end($1)$0"),
        "rs": ("raw string", 'R"($SEL0)"'),
        "rc": ("reinterpret_cast", "reinterpret_cast<$1>($SEL2)"),
        "sc": ("static_cast", "static_cast<${1:size_t}>($SEL2)"),
    },
    completions={
        ("Keyword", Icon.KEYWORD): [
            "break",
            "continue",
            "decltype",
            "default",
            "delete",
            "enum",
            "friend",
            "goto",
            "namespace",
            "new",
            "operator",
            "return",
            "template",
            "throw",
            "typedef",
            "typename",
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
            "inline",
            "mutable",
            "noexcept",
            "override",
            "static",
            "thread_local",
            "unsigned",
            "virtual",
            "volatile",
        ],
        ("Cast", Icon.CONVERT): [
            "const_cast",
            "dynamic_cast",
            "reinterpret_cast",
            "static_cast",
        ],
        ("Function", Icon.FUNCTION): [
            "defined",
            "make_optional",
            "make_shared",
            "make_unique",
            "move",
            "sizeof",
            "static_assert",
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
        ],
        ("Macros", Icon.META): [
            "define",
            "elif",
            "endif",
            "error",
            "ifdef",
            "ifndef",
            "include",
            "pragma",
        ],
        ("Namespace", Icon.NAMESPACE): [
            "filesystem",
        ],
        ("Class", Icon.TYPE): [
            "auto",
            "optional",
            "pair",
            "runtime_error",
            "shared_ptr",
            "string",
            "tuple",
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
            "nullopt",
            "nullptr",
            "true",
        ],
        ("Variable", Icon.VARIABLE): [
            "this",
        ],
    },
)
