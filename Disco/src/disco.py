import hashlib
import os
import plistlib
import re
import shutil

GRAY         = "#9090A0" # [144, 144, 160]
DARK_GRAY    = "#51515D" # [ 81,  81,  93]
WHITE        = "#CDCDCD" # [205, 205, 205]
CLEAR_WHITE  = "#FFFFFF" # [255, 255, 255]
LIGHT_VIOLET = "#AAAAF0" # [170, 170, 240]
VIOLET       = "#B69EFF" # [182, 158, 255]
DARK_VIOLET  = "#5E5E8E" # [94,   94, 142]
PURPLE       = "#E572D2" # [229, 114, 210]
PINK         = "#EF51AA" # [239,  81, 170]
LIGHT_BLUE   = "#77ABFF" # [119, 171, 255]
BLUE         = "#6699FF" # [182, 158, 255]
DARK_BLUE    = "#264F78" # [ 38,  79, 120]
BLUISH_BLACK = "#272728" # [ 45,  45,  52]
GREEN        = "#C5CC4B" # [197, 204,  75]
YELLOW       = "#EDC61A" # [239, 197,  45]
ORANGE       = "#FF9A41" # [255, 154,  65]
DARK_ORANGE  = "#FF8147" # [255, 129,  71]
CRIMSON      = "#E5476C" # [229,  71, 108]

FOREGROUND  = WHITE
KEYWORD     = PURPLE
STORAGE     = PINK
INDEXED     = LIGHT_BLUE
PUNCTUATION = BLUE
COMMENT     = GRAY
PRIMITIVE   = DARK_ORANGE
STRING      = GREEN

def rule(name, scope, **settings):
  return dict(
    name = name,
    scope = re.sub("\s{2,}", ' ', scope),
    settings = settings
  )

settings = [
  dict(settings = dict(
    background         = '#000000',
    foreground         = FOREGROUND,
    caret              = CLEAR_WHITE,
    selection          = DARK_BLUE+"90",
    inactiveSelection  = DARK_BLUE,
    selectionBorder    = LIGHT_BLUE,
    lineHighlight      = CRIMSON+"50",
    findHighlight      = YELLOW,
    minimapBorder      = FOREGROUND,
    bracketsForeground = DARK_ORANGE
  )),

  dict(scope = 'invalid', settings = dict(background = CRIMSON)),

  rule("Keyword",                     "keyword, storage.modifier", foreground = PURPLE),
  rule("Symbolic operator",           "keyword.operator", foreground = BLUE),
  rule("Alphanumeric operator",       "keyword.operator.alphanumeric", foreground = PURPLE),
  rule("Special symbolic operator", """keyword.operator.unary,
                                       keyword.operator.yaml,
                                       punctuation.separator.line""", foreground = DARK_ORANGE),
  rule("Delimiter",                 """keyword.operator.dereference,
                                       meta.delimiter,
                                       punctuation.separator,
                                       punctuation.terminator""", foreground = FOREGROUND),

  rule("Comment mark", "comment.mark", foreground = LIGHT_VIOLET),

  rule("Storage",                   "storage", foreground = PINK),
  rule("Language constant",         "constant.language", foreground = DARK_ORANGE),
  rule("Language variable",         "variable.language", foreground = ORANGE),
  rule("User-defined constant",     "constant.user", foreground = CRIMSON),
  rule("User-defined variable",     "variable.user", foreground = ORANGE),
  rule("Entity name",               "entity.name", foreground = LIGHT_BLUE),
  rule("Inherited class",           "entity.other.inherited-class", foreground = CRIMSON),
  rule("Parameter",                 "variable.parameter", foreground = ORANGE),
  rule("Support type and function", "support.type, support.class, support.function", foreground = PINK),
  rule("Support constant",          "support.constant", foreground = ORANGE),

  rule("Lambda",             "punctuation.definition.lambda, keyword.operator.lambda", foreground = LIGHT_BLUE),
  rule("Inline expressions", "string meta.inline-expression", foreground = WHITE),

  rule("Doc-comment keyword and parameter", """comment.block.documentation keyword,
                                               comment.block.documentation variable.parameter""", foreground = WHITE),
  rule("Doc-comment inline keyword",          "keyword.documentation.inline", foreground = DARK_GRAY),
  rule("Tags in doc-comments",                "comment.block.documentation meta.tag", foreground = DARK_VIOLET),

  rule("Java package declaration",             "meta.package.java storage.type", foreground = CRIMSON),
  rule("Java import asterisk",                 "storage.type.asterisk.java", foreground = CRIMSON),
  rule("Java throwable declaration",           "(meta.throws.statement.java storage.type.java) -meta.generic", foreground = CRIMSON),
  rule("Java inherited class",               """(meta.extends.statement.java storage.type.java) -meta.generic,
                                                (meta.implements.statement.java storage.type.java) -meta.generic""", foreground = CRIMSON),
  rule("Java assert keyword",                  "keyword.control.assert.java", foreground = CRIMSON),
  rule("Java annotation name and parameter", """punctuation.definition.annotation.java,
                                                meta.annotation.identifier.java storage.type,
                                                variable.parameter.annotation.java""", foreground = YELLOW),
  rule("Java generic type",                    "storage.type.generic.java", foreground = DARK_ORANGE),
  rule("Java anonymous class brackets",        "meta.class.body.anonymous.java punctuation.definition.class", foreground = CRIMSON),
  rule("Java log exception",                   "text.log.java entity.name.exception", foreground = CRIMSON),

  rule("Tag", "entity.name.tag", foreground = LIGHT_BLUE),

  rule("XML keywords and punctuation",   "source.xml keyword, source.xml punctuation.definition", foreground = LIGHT_BLUE),
  rule("XML attribute and doctype name", "source.xml entity.name.attribute, entity.name.doctype.element.xml", foreground = YELLOW),
  rule("XML attribute value",            "meta.attribute.xml string", foreground = GREEN),
  rule("XML CDATA brackets",             "meta.cdata.xml punctuation.definition", foreground = DARK_ORANGE),
  rule("XML substitution variable",      "punctuation.definition.substitution.xml", foreground = DARK_ORANGE),

  rule("Diff inserted", "markup.inserted.diff, punctuation.definition.to-file.diff", foreground = GREEN),
  rule("Diff deleted",  "markup.deleted.diff, punctuation.definition.from-file.diff", foreground = CRIMSON),
  rule("Diff range",    "meta.diff.range", foreground = YELLOW),
  rule("Diff header",   "meta.diff.header", foreground = LIGHT_BLUE),

  rule("Powershell pipe and stream",       "keyword.operator.pipe.powershell, keyword.operator.stream.powershell", foreground = DARK_ORANGE),
  rule("Powershell execute and escape",    "keyword.operator.execute.powershell, keyword.operator.escape.powershell", foreground = CRIMSON),
  rule("Powershell static call separator", "punctuation.separator.static-call.powershell", foreground = BLUE),
  rule("Powershell embedded expression",   "punctuation.definition.expression.powershell", foreground = DARK_ORANGE),

  rule("INI section", "meta.section.ini, entity.name.section.ini", foreground = YELLOW),
  rule("Error indicator", "meta.indicator.error", foreground = CRIMSON),
  rule("Warning indicator", "meta.indicator.warning", foreground = DARK_ORANGE),
  rule("Success indicator", "meta.indicator.success", foreground = GREEN),
  rule("Log message", "text.log meta.message", foreground = YELLOW),

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
]

def group(lang, flavor='source'):
  global current_lang
  current_lang = lang
  global current_flavor
  current_flavor = flavor

def no_group():
  global current_lang
  current_lang = None
  global current_flavor
  current_flavor = None

def rec(color, *scopes):
  for scope in scopes:
    chunks = [current_flavor] if current_flavor != None else []
    chunks += scope.split()

    for i, chunk in enumerate(chunks):
      if chunk.startswith('#'):
        chunks[i] = chunk[1:]
      elif current_lang != None:
        chunks[i] = chunk +'.' + current_lang
      else:
        chunks[i] = chunk

    settings.append(dict(scope = ' '.join(chunks), settings = dict(foreground = color)))

## FOUNDATION ##

no_group()
rec(COMMENT,   'comment')
rec(PRIMITIVE, 'constant.numeric',
               'constant.character')
rec(STRING,    'string')

## PYTHON ##

group('python')
rec(KEYWORD, 'keyword.operator.logical')
rec(INDEXED, 'entity.name.function support.function.magic',
             'entity.name.function.decorator',
             'entity.name.function.decorator support.function.builtin')

## REGEXP IN PYTHON ##

rec(YELLOW, 'source.regexp #punctuation.definition.group')
rec(PURPLE, 'source.regexp #constant.other.character-class.set',
            '#constant.character.character-class.regexp')

## JAVASCRIPT ##

group('js')
rec(KEYWORD,     'meta.instance.constructor keyword.operator.new',
                 'meta.for keyword.operator')
rec(FOREGROUND,  '#support.function')
rec(STORAGE,     'variable.type')
rec(LIGHT_BLUE,  'meta.object-literal.key')
rec(PUNCTUATION, 'storage.type.function.arrow')
rec(ORANGE,      '#support.type.object')

## REGEXP IN JAVASCRIPT ##

rec(YELLOW, '#keyword.operator.or.regexp',
            '#punctuation.definition.group.regexp')
rec(PURPLE, '#keyword.operator.quantifier.regexp',
            '#constant.other.character-class.escape.backslash.regexp')
rec(PINK,   '#keyword.operator.quantifier.regexp')

## REGEXP ##

group('regexp')
rec(YELLOW,  'keyword.operator.or',
             'punctuation.definition.group')
rec(PURPLE,  'constant.language.character-class',
             'constant.character -constant.character.escape')
rec(PINK,    'constant.language.character-class constant.language.character-class', # Character classes in group
             '#keyword.control',
             '#keyword.operator')
rec(CRIMSON, '#keyword.modifier',
             'meta.group.modifier punctuation.definition.group.modifier')

## ETC ##

no_group()
rec(GREEN,       'meta.not-commited-yet.git constant.numeric.line-number')
rec(DARK_VIOLET, 'constant.date.git')

## ICONS ##

def icon(scope, filename):
  return dict(
    scope = scope,
    settings = dict(icon = filename)
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

with open(os.path.join("..", "Disco.tmTheme"), "wb") as pfile:
  plistlib.dump(dict(name="Disco", settings=settings), pfile)

targetDirectory = os.path.join("..", "generated")
shutil.rmtree(targetDirectory, ignore_errors=True)
os.mkdir(targetDirectory)

for icon in icons:
  filename = hashlib.sha1(icon["scope"].encode('ascii')).hexdigest() + ".tmPreferences"
  print("{}: {}".format(filename, icon["scope"]))
  with open(os.path.join(targetDirectory, filename), "wb") as pfile:
    plistlib.dump(icon, pfile)
