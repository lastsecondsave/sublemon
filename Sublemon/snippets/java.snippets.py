from snippets import Icon, generate

getter = r"""
public ${1:String} ${1/boolean|(.*)/(?1:get:is)/}${2/./\u$0/}() {
    return ${2:property};
}
"""

setter = r"""
public void set${2/./\u$0/}(${1:String} ${2/.*/$0/}) {
    this.${2:property} = ${2/.*/$0/};
}
"""

snippets = {
    "pl": "System.out.println($SEL0);",
    "sf": (
        "static final CONSTANT",
        "static final ${1:String} ${2:CONSTANT} = ${3:null};",
    ),
    "ima": ("import *", "import $0.*;"),
    "fun": ("function", "${1:void} ${2:run}($3) {}"),
    "main": ("main", "public static void main(String[] args) {}"),
    "tt": ("this.x = x", "this.$1 = $1;"),
    "te": ("throw Exception", "throw new ${1:RuntimeException}($2);"),
    "lgg": (
        "logger",
        "private static final Logger log = LoggerFactory.getLogger(${1:$FILENAME}.class);",
    ),
    "fori": ("for i", "for (int ${1:i} = 0; $1 < ${2:imax}; ${3:$1++}) {}"),
    "fort": (
        "for iterator",
        "for (Iterator<$1> ${2:itr} = ${3:list}.iterator(); $2.hasNext(); ) {}",
    ),
    "jd": ("javadoc", r"/**-->${SELECTION/^\s*/ * /mg}$0--> */"),
    "td": ("TODO", "// TODO: "),
    "get": ("getter", getter),
    "geto": (
        "getter with optional",
        getter.replace("public ${1:String}", "public Optional<${1:String}>"),
    ),
    "set": ("setter", setter),
    "gs": ("getter + setter", getter + setter),
    "rnn": "Objects.requireNonNull($SEL1)",
}

completions = {
    ("Keyword", Icon.KEYWORD): [
        "break",
        "case",
        "continue",
        "return",
        "throw",
        "import",
        "package",
    ],
    ("Modifier", Icon.ACCESS_MODIFIER): [
        "final",
        "private",
        "protected",
        "public",
        "static",
        "volatile",
    ],
    ("Block", Icon.BLOCK): [
        "catch (${1:Exception} e) {}",
        "else {}",
        "finally {}",
        "for ($1) {}",
        "if ($1) {}",
        "switch ($1) {}",
        "synchronized (${1:this}) {}",
        "try {}",
        "while ($1) {}",
        ("elif", "else if ($1) {}"),
    ],
    ("Storage", Icon.STORAGE): [
        "class ${1:$FILENAME} {}",
        "enum ${1:$FILENAME} {}",
        "interface ${1:$FILENAME} {}",
    ],
    ("Annotation", Icon.META): [
        "@Override",
        "@SuppressWarnings()",
    ],
    ("Type", Icon.PRIMITIVE_TYPE): [
        "boolean",
        "byte",
        "char",
        "double",
        "float",
        "int",
        "long",
        "short",
        "void",
    ],
    ("Class", Icon.TYPE): [
        "Optional",
        "String",
    ],
    ("Constant", Icon.CONSTANT): [
        "false",
        "null",
        "true",
    ],
    ("Variable", Icon.VARIABLE): [
        "super",
        "this",
    ],
}

generate("source.java", snippets, completions)


generate(
    "source.java comment.block.documentation.javadoc",
    snippets={
        "code": ("@code", "{@code $SEL1}"),
        "link": ("@link", "{@link $SEL1}"),
    },
)
