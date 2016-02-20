import hashlib
import os
import plistlib
import re
import shutil

GRAY         = "#9090A0" # [144, 144, 160]
WHITE        = "#CDCDCD" # [205, 205, 205]
CLEAR_WHITE  = "#FFFFFF" # [255, 255, 255]
LIGHT_VIOLET = "#AAAAF0" # [170, 170, 240]
VIOLET       = "#B69EFF" # [182, 158, 255]
PURPLE       = "#E572D2" # [229, 114, 210]
PINK         = "#EF51AA" # [239,  81, 170]
BLUE         = "#77ABFF" # [119, 171, 255]
DARK_BLUE    = "#264F78" # [ 38,  79, 120]
BLUISH_GRAY  = "#363642" # [ 54,  54,  66]
BLUISH_BLACK = "#2D2D34" # [ 45,  45,  52]
GREEN        = "#C5CC4B" # [197, 204,  75]
YELLOW       = "#EDC61A" # [239, 197,  45]
ORANGE       = "#FF9A41" # [255, 154,  65]
DARK_ORANGE  = "#FF8147" # [255, 129,  71]
CRIMSON      = "#E5476C" # [229,  71, 108]

def rule(name, scope, **settings):
  return dict(
    name = name,
    scope = re.sub("\s{2,}", ' ', scope),
    settings = settings
  )

settings = dict(
  background         = BLUISH_BLACK,
  foreground         = WHITE,
  caret              = CLEAR_WHITE,
  selection          = DARK_BLUE,
  inactiveSelection  = DARK_BLUE,
  selectionBorder    = BLUE,
  lineHighlight      = LIGHT_VIOLET+"20",
  findHighlight      = YELLOW,
  minimapBorder      = WHITE,
  bracketsForeground = DARK_ORANGE
)

settings = [
  dict(settings=settings),

  rule("Invalid", "invalid", background = CRIMSON),
  rule("Warning", "warning", background = BLUISH_GRAY),

  rule("Keyword",                     "keyword, storage.modifier", foreground = PURPLE),
  rule("Symbolic operator",           "keyword.operator", foreground = VIOLET),
  rule("Alphanumeric operator",       "keyword.operator.alphanumeric", foreground = PURPLE),
  rule("Special symbolic operator", """keyword.operator.unary,
                                       keyword.operator.yaml,
                                       punctuation.separator.line""", foreground = DARK_ORANGE),
  rule("Delimiter",                 """keyword.operator.dereference,
                                       meta.delimiter,
                                       punctuation.separator,
                                       punctuation.terminator""", foreground = WHITE),

  rule("Number and characters", "constant.numeric, constant.character", foreground = DARK_ORANGE),
  rule("String",                "string, meta.inline-expression string", foreground = GREEN),

  rule("Comment",      "comment", foreground = GRAY),
  rule("Comment mark", "comment.mark", foreground = LIGHT_VIOLET),

  rule("Storage",                   "storage", foreground = PINK),
  rule("Language constant",         "constant.language", foreground = DARK_ORANGE),
  rule("Language variable",         "variable.language", foreground = ORANGE),
  rule("User-defined constant",     "constant.user", foreground = CRIMSON),
  rule("User-defined variable",     "variable.user", foreground = ORANGE),
  rule("Entity name",               "entity.name", foreground = BLUE),
  rule("Inherited class",           "entity.other.inherited-class", foreground = CRIMSON),
  rule("Parameter",                 "variable.parameter", foreground = ORANGE),
  rule("Support type and function", "support.type, support.class, support.function", foreground = PINK),
  rule("Support constant",          "support.constant", foreground = ORANGE),

  rule("Lambda",             "punctuation.definition.lambda, keyword.operator.lambda", foreground = BLUE),
  rule("Inline expressions", "string meta.inline-expression", foreground = WHITE),

  rule("Doc-comment keyword and parameter", """comment.block.documentation keyword,
                                               comment.block.documentation variable.parameter""", foreground = WHITE),
  rule("Doc-comment inline keyword",          "keyword.documentation.inline", foreground = GRAY+"90"),
  rule("Tags in doc-comments",                "comment.block.documentation meta.tag", foreground = LIGHT_VIOLET+"90"),

  rule("Java package declaration",             "meta.package.java storage.type", foreground = CRIMSON),
  rule("Java import asterisk",                 "storage.type.asterisk.java", foreground = CRIMSON),
  rule("Java throwable declaration",           "entity.other.throwable.java", foreground = CRIMSON),
  rule("Java assert keyword",                  "keyword.control.assert.java", foreground = CRIMSON),
  rule("Java annotation name and parameter", """punctuation.definition.annotation.java,
                                                meta.annotation.identifier.java storage.type,
                                                variable.parameter.annotation.java""", foreground = YELLOW),
  rule("Java generic type",                    "storage.type.generic.java", foreground = DARK_ORANGE),
  rule("Java anonymous class brackets",        "meta.class.body.anonymous.java punctuation.definition.class", foreground = CRIMSON),
  rule("Java log exception",                   "text.log.java entity.name.exception", foreground = CRIMSON),

  rule("Tag", "entity.name.tag", foreground = BLUE),

  rule("XML keywords and punctuation",   "source.xml keyword, source.xml punctuation.definition", foreground = BLUE),
  rule("XML attribute and doctype name", "source.xml entity.name.attribute, entity.name.doctype.element.xml", foreground = YELLOW),
  rule("XML attribute value",            "meta.attribute.xml string", foreground = GREEN),
  rule("XML CDATA brackets",             "meta.cdata.xml punctuation.definition", foreground = DARK_ORANGE),
  rule("XML substitution variable",      "punctuation.definition.substitution.xml", foreground = DARK_ORANGE),

  rule("Diff inserted", "markup.inserted.diff, punctuation.definition.to-file.diff", foreground = GREEN),
  rule("Diff deleted",  "markup.deleted.diff, punctuation.definition.from-file.diff", foreground = CRIMSON),
  rule("Diff range",    "meta.diff.range", foreground = YELLOW),
  rule("Diff header",   "meta.diff.header", foreground = BLUE),

  rule("C macro definition",      "punctuation.definition.macro.c, keyword.macro.c", foreground = YELLOW),
  rule("C macro body",            "meta.macro.body.c", foreground = GREEN),
  rule("C++ namespace separator", "punctuation.separator.namespace.c++", foreground = VIOLET),

  rule("Powershell pipe and stream",       "keyword.operator.pipe.powershell, keyword.operator.stream.powershell", foreground = DARK_ORANGE),
  rule("Powershell execute and escape",    "keyword.operator.execute.powershell, keyword.operator.escape.powershell", foreground = CRIMSON),
  rule("Powershell static call separator", "punctuation.separator.static-call.powershell", foreground = VIOLET),
  rule("Powershell embedded expression",   "punctuation.definition.expression.powershell", foreground = DARK_ORANGE),

  rule("INI section", "meta.section.ini, entity.name.section.ini", foreground = YELLOW),
  rule("Error indicator", "meta.indicator.error", foreground = CRIMSON),
  rule("Warning indicator", "meta.indicator.warning", foreground = DARK_ORANGE),
  rule("Success indicator", "meta.indicator.success", foreground = GREEN),
  rule("Log message", "text.log meta.message", foreground = YELLOW),

  rule("RegExp limiters",                   "keyword.operator.or.regexp, punctuation.definition.group.regexp", foreground = YELLOW),
  rule("RegExp character classes",        """constant.language.character-class.regexp,
                                             source.regexp constant.character - constant.character.escape""", foreground = PURPLE),
  rule("RegExp character classes in group", "constant.language.character-class.regexp constant.language.character-class.regexp", foreground = PINK),
  rule("RegExp keywords",                   "source.regexp keyword.control, source.regexp keyword.operator", foreground = PINK),
  rule("RegExp modifiers",                """keyword.modifier.regexp,
                                             meta.group.modifier.regexp punctuation.definition.group.modifier""", foreground = CRIMSON),

  rule("Embedded RegExp",            "source.regexp.embedded - source.yaml", foreground = GREEN),
  rule("Embedded RegExp delimiters", "source punctuation.definition.regexp", foreground = ORANGE),

  rule("Markup italic",        "markup.italic", foreground = ORANGE),
  rule("Markup bold",          "markup.bold", foreground = CRIMSON),
  rule("Markup strikethrough", "markup.strikethrough", foreground = GRAY),
  rule("Markup links",         "markup.underline.link", foreground = YELLOW),

  rule("Markdown monospace",       """markup.raw.inline.markdown, punctuation.definition.block.fenced.markdown,
                                      text.markdown markup.raw.block""", foreground = GREEN),
  rule("Markdown punctuation",     """punctuation.definition.list.markdown, punctuation.definition.quote.markdown,
                                      punctuation.heading.underline.markdown, punctuation.definition.image.markdown""", foreground = DARK_ORANGE),
  rule("Markdown language marker",   "meta.fenced.language.marker.markdown", foreground = YELLOW),
  rule("Markdown language marker",   "text.markdown entity.name.tag", foreground = PINK),

  rule("CSS general selector",      "meta.rule.selector.css entity.name.general", foreground = PINK),
  rule("CSS id selector",           "meta.rule.selector.css entity.name.id", foreground = YELLOW),
  rule("CSS class selector",        "meta.rule.selector.css entity.name.class", foreground = CRIMSON),
  rule("CSS pseudo-class selector", "meta.rule.selector.css entity.name.pseudo-class", foreground = PURPLE),
  rule("CSS important",             "keyword.other.important.css", foreground = DARK_ORANGE),

  # Tweaks for default syntaxes

  rule("Python logical operator",         "keyword.operator.logical.python", foreground = PURPLE),
  rule("Python function with underlines", "entity.name.function.python support.function.magic.python", foreground = BLUE),
  rule("Python annotation",             """entity.name.function.decorator.python,
                                           entity.name.function.decorator.python support.function.builtin.python""", foreground = YELLOW)
]

with open(os.path.join("..", "Disco.tmTheme"), "wb") as pfile:
  plistlib.dump(dict(name="Disco", settings=settings), pfile)

def icon(scope, filename):
  return dict(
    scope = scope,
    settings = dict(icon=filename)
  )

icons = [
  icon("source.c++", "file_type_cpp"),
  icon("source.css", "file_type_css"),
  icon("source.git", "file_type_git"),
  icon("source.groovy", "file_type_groovy"),
  icon("source.java", "file_type_java"),
  icon("source.java-props, source.ini", "file_type_properties"),
  icon("source.js", "file_type_javascript"),
  icon("source.json", "file_type_json"),
  icon("source.powershell", "file_type_powershell"),
  icon("source.python", "file_type_python"),
  icon("source.xml", "file_type_xml"),
  icon("source.yaml", "file_type_yaml"),
  icon("text.markdown, text.rfc", "file_type_markup")
]

targetDirectory = os.path.join("..", "generated")
shutil.rmtree(targetDirectory, ignore_errors=True)
os.mkdir(targetDirectory)

for icon in icons:
  filename = hashlib.sha1(icon["scope"].encode('ascii')).hexdigest() + ".tmPreferences"
  print("{}: {}".format(filename, icon["scope"]))
  with open(os.path.join(targetDirectory, filename), "wb") as pfile:
    plistlib.dump(icon, pfile)
