from snippets import Icon, generate

snippets = {
    "sb": ("shebang", "#!/usr/bin/env ${0:bash}"),
    "fn": ("function", "${1:run}() {}"),
    "pl": "echo $SEL0",
}

completions = {
    ("Support", Icon.FUNCTION): [
        "echo",
        "exec",
        "exit",
        "printf",
        "source",
        "trap",
    ],
    ("Modifier", Icon.ACCESS_MODIFIER): [
        "export",
        "local",
        "readonly",
    ],
    ("Block", Icon.BLOCK): [
        "case $1 in<=>esac",
        "elif [[ $1 ]]; then==>",
        "else==>",
        "if [[ $1 ]]; then<=>fi",
        "while $1; do<=>done",
    ],
    ("Program", Icon.EXTERNAL): [
        "basename",
        "dirname",
        "xargs",
    ],
}


generate("source.shell.bash", snippets, completions)
