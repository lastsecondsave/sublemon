from snippets import Icon, generate

snippets = {
    "pl": "fmt.Println($SEL0)",
    "ts": ("type struct", "type ${1:Type} struct {}"),
}

completions = {
    ("Keyword", Icon.KEYWORD): [
        "const",
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
        "for $1 {}",
        "func ${1:run}($2)$3 {}",
        "if $1 {}",
        "interface {}",
        "struct {}",
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
        "string",
        "map",
    ],
    ("Support", Icon.FUNCTION): [
        "make",
    ],
}

generate("source.go", snippets, completions)
