from snippets import Icon, generate

snippets = {
    "pl": "fmt.Println($SEL0)",
    "ts": ("type struct", "type ${1:Type} struct {}"),
}

completions = {
    ("Keyword", Icon.KEYWORD): [
        "defer",
        "import",
        "package",
        "return",
        "type",
        "var",
    ],
    ("Block", Icon.BLOCK): [
        "func ${1:run}($2)$3 {}",
        "if $1 {}",
        "struct {}",
    ],
    ("Constant", Icon.CONSTANT): [
        "false",
        "nil",
        "true",
    ],
    ("Primitive", Icon.PRIMITIVE_TYPE): [
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
    ("Primitive", Icon.TYPE): [
        "string",
        "map",
    ],
    ("Support", Icon.FUNCTION): [
        "make",
    ],
}

generate("source.go", snippets, completions)
