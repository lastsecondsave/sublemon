from textwrap import dedent

from snippets import Icon, generate

snippets = {
    "pl": "fmt.Println($SEL0)",
    "ts": ("type struct", "type ${1:Type} struct {}"),
    "fn": ("function", "func ${1:run}($2)$3 {}"),
    "fm": ("method", "func ($1) ${2:run}($3)$4 {}"),
    "ie": ("if err != nil", "if ${1:err} != nil {}"),
    "ier": (
        "if err != nil { return }",
        dedent(
            """
            if ${1:err} != nil {
                return ${2:nil}, ${1}
            }
            """
        ),
    ),
    "lf": "log.Fatal(${1:err})",
    "mp": "map[${1:string}]${2:any}",
}

completions = {
    ("Keyword", Icon.KEYWORD): [
        "case",
        "const",
        "continue",
        "default",
        "defer",
        "import",
        "new",
        "package",
        "range",
        "return",
        "type",
        "var",
    ],
    ("Block", Icon.BLOCK): [
        "else {}",
        "for $1 {}",
        "func ${1:run}($2)$3 {}",
        "if $1 {}",
        "interface {}",
        "select {}",
        "struct {}",
        "switch $1 {}",
    ],
    ("Constant", Icon.CONSTANT): [
        "false",
        "nil",
        "true",
    ],
    ("Type", Icon.PRIMITIVE_TYPE): [
        "bool",
        "byte",
        "complex128",
        "complex64",
        "float32",
        "float64",
        "int",
        "int16",
        "int32",
        "int64",
        "int8",
        "rune",
        "uint",
        "uint16",
        "uint32",
        "uint64",
        "uint8",
        "uintptr",
    ],
    ("Type", Icon.TYPE): [
        "any",
        "chan",
        "error",
        "map",
        "string",
    ],
    ("Support", Icon.FUNCTION): [
        "append",
        "cap",
        "clear",
        "close",
        "copy",
        "delete",
        "len",
        "make",
        "new",
        "panic",
        "recover",
    ],
}

generate("source.go", snippets, completions)
