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
BLUE         = "#6699FF" # [102, 153, 255]
DARK_BLUE    = "#264F78" # [ 38,  79, 120]
BLUISH_BLACK = "#272728" # [ 45,  45,  52]
GREEN        = "#C5CC4B" # [197, 204,  75]
YELLOW       = "#EDC61A" # [239, 197,  45]
ORANGE       = "#FF9A41" # [255, 154,  65]
DARK_ORANGE  = "#FF8147" # [255, 129,  71]
CRIMSON      = "#E5476C" # [229,  71, 108]

FOREGROUND        = WHITE
KEYWORD           = PURPLE
STORAGE           = PINK
INDEXED           = BLUE
OPERATOR          = LIGHT_BLUE
PUNCTUATION       = DARK_ORANGE
COMMENT           = GRAY
COMMENT_HIGHLIGHT = WHITE
PRIMITIVE         = DARK_ORANGE
STRING            = GREEN
META              = YELLOW
TAG               = LIGHT_BLUE
PARAMETER         = ORANGE
USER_CONSTANT     = CRIMSON

def rule(name, scope, **settings):
  return dict(
    name = name,
    scope = re.sub("\s{2,}", ' ', scope),
    settings = settings
  )

theme_globals = dict(
  background         = '#202830',
  foreground         = FOREGROUND,
  caret              = CLEAR_WHITE,
  selection          = "#384868",
  lineHighlight      = "#E5476C40",
  findHighlight      = YELLOW,
  minimapBorder      = FOREGROUND,
  bracketsForeground = PUNCTUATION
)

widget_globals = dict(
  background         = '#1B1B1C',
  foreground         = FOREGROUND,
  caret              = CLEAR_WHITE,
  selection          = "#384868",
  bracketsForeground = PUNCTUATION
)

settings = [
  dict(settings=theme_globals),

  rule("Language constant",         "constant.language", foreground = ORANGE),
  rule("Language variable",         "variable.language", foreground = ORANGE),
  rule("User-defined variable",     "variable.user", foreground = ORANGE),
  rule("Inherited class",           "entity.other.inherited-class", foreground = CRIMSON),
  rule("Support constant",          "support.constant", foreground = ORANGE),

  rule("Inline expressions", "string meta.inline-expression", foreground = WHITE),

  rule("Doc-comment inline keyword",          "keyword.documentation.inline", foreground = DARK_GRAY),
  rule("Tags in doc-comments",                "comment.block.documentation meta.tag", foreground = DARK_VIOLET),

  rule("Java log exception",                   "text.log.java entity.name.exception", foreground = CRIMSON),

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

widget_settings = [dict(settings=widget_globals)]

def group(category, lang, widget):
  global current_lang, current_category, widget_category
  current_lang, current_category, widget_category = lang, category, widget

def source(lang, widget=False):
  group('source', lang, widget)

def no_group(widget=False):
  group(None, None, widget)

def rec(color, *scopes, **attributes):
  attributes['foreground'] = color

  for scope in scopes:
    chunks = [current_category] if current_category != None else []
    chunks += scope.split()

    for i, chunk in enumerate(chunks):
      if chunk.startswith('#'):
        chunks[i] = chunk[1:]
      elif current_lang != None:
        chunks[i] = chunk +'.' + current_lang
      else:
        chunks[i] = chunk

    record_settings = dict(scope=' '.join(chunks), settings=attributes)
    settings.append(record_settings)
    if widget_category:
      widget_settings.append(record_settings)

##> FOUNDATION ##

no_group(widget=True)
rec(COMMENT,       'comment')
rec(PRIMITIVE,     'constant.numeric',
                   'constant.character')
rec(STRING,        'string')
rec(STORAGE,       'storage',
                   'support.type',
                   'support.class',
                   'support.function')
rec(KEYWORD,       'keyword',
                   'keyword.operator.alphanumeric',
                   'storage.modifier')
rec(OPERATOR,      'keyword.operator')
rec(INDEXED,       'entity.name')
rec(FOREGROUND,    'punctuation.separator',
                   'punctuation.terminator')
rec(PARAMETER,     'variable.parameter')
rec(USER_CONSTANT, 'constant.user')
rec(FOREGROUND,    'invalid', background=CRIMSON)

##> PYTHON ##

source('python')
rec(KEYWORD, 'keyword.operator.logical')
rec(INDEXED, 'entity.name.function support.function.magic',
             'entity.name.function.decorator',
             'entity.name.function.decorator support.function.builtin')

##> REGEXP IN PYTHON ##

rec(YELLOW, 'source.regexp #punctuation.definition.group')
rec(PURPLE, 'source.regexp #constant.other.character-class.set',
            '#constant.character.character-class.regexp')

##> JAVASCRIPT ##

source('js')
rec(KEYWORD,     'meta.instance.constructor keyword.operator.new',
                 'meta.for keyword.operator')
rec(STORAGE,     'variable.type')
rec(LIGHT_BLUE,  'meta.object-literal.key')
rec(OPERATOR,    'storage.type.function.arrow')
rec(ORANGE,      '#support.type.object')
rec(FOREGROUND,  '#support.function')

##> REGEXP IN JAVASCRIPT ##

rec(YELLOW, '#keyword.operator.or.regexp',
            '#punctuation.definition.group.regexp')
rec(PURPLE, '#keyword.operator.quantifier.regexp',
            '#constant.other.character-class.escape.backslash.regexp')
rec(PINK,   '#keyword.operator.quantifier.regexp')

##> REGEXP ##

source('regexp', widget=True)
rec(YELLOW,  'keyword.operator.or',
             'punctuation.definition.group')
rec(PURPLE,  'constant.language.character-class',
             'constant.character -constant.character.escape')
rec(PINK,    'constant.language.character-class constant.language.character-class', # Character classes in group
             '#keyword.control',
             '#keyword.operator')
rec(CRIMSON, '#keyword.modifier',
             'meta.group.modifier punctuation.definition.group.modifier')

##> JAVA ##

source('java')
rec(META,              'punctuation.definition.annotation',
                       'meta.annotation.identifier #storage.type',
                       'variable.parameter.annotation')
rec(COMMENT_HIGHLIGHT, 'comment.block.documentation #keyword',
                       'comment.block.documentation #variable.parameter')
rec(CRIMSON,           'meta.package #storage.type',
                       'storage.type.asterisk',
                       'keyword.control.assert',
                       'meta.class.body.anonymous #punctuation.definition.class',
                       'meta.extends.statement storage.type #-meta.generic',
                       'meta.implements.statement storage.type #-meta.generic',
                       'meta.throws.statement storage.type #-meta.generic')
rec(DARK_ORANGE,       'storage.type.generic')

##> C++ ##

source('c++')
rec(USER_CONSTANT, 'entity.name.constant.preprocessor')
rec(KEYWORD,       'keyword.operator.word')
rec(OPERATOR,      'punctuation.accessor')

##> XML ##

source('xml')
rec(TAG,         'entity.name.tag',
                 '#keyword',
                 '#punctuation.definition')
rec(STRING,      'meta.attribute #string')
rec(PUNCTUATION, 'meta.cdata #punctuation.definition')
rec(YELLOW,      '#entity.name.attribute',
                 'entity.name.doctype.element')
rec(DARK_ORANGE, 'punctuation.definition.substitution')

##> YAML ##

source('yaml')
rec(PUNCTUATION, '#keyword.operator')

##> ETC ##

no_group()
rec(GREEN,       'meta.not-commited-yet.git constant.numeric.line-number')
rec(DARK_VIOLET, 'constant.date.git')

##> ICONS ##

def icon(scope, filename):
  return dict(
    scope = scope,
    settings = dict(icon = filename)
  )

icons = [
  icon("source.c++",        "file_type_cpp"),
  icon("source.css",        "file_type_css"),
  icon("source.git",        "file_type_git"),
  icon("source.groovy",     "file_type_groovy"),
  icon("source.java",       "file_type_java"),
  icon("source.ini",        "file_type_properties"),
  icon("source.java-props", "file_type_properties"),
  icon("source.js",         "file_type_javascript"),
  icon("source.json",       "file_type_json"),
  icon("source.powershell", "file_type_powershell"),
  icon("source.python",     "file_type_python"),
  icon("source.xml",        "file_type_xml"),
  icon("source.yaml",       "file_type_yaml"),
  icon("text.markdown",     "file_type_markup"),
  icon("text.rfc",          "file_type_markup")
]

with open(os.path.join("..", "Disco.tmTheme"), "wb") as pfile:
  plistlib.dump(dict(name="Disco", settings=settings), pfile)

with open(os.path.join("..", "Widget - Disco.tmTheme"), "wb") as pfile:
  plistlib.dump(dict(name="Disco", settings=widget_settings), pfile)

shutil.rmtree("generated", ignore_errors=True)
os.mkdir("generated")

for icon in icons:
  filename = hashlib.sha1(icon["scope"].encode('ascii')).hexdigest() + ".tmPreferences"
  print("{}: {}".format(filename, icon["scope"]))
  with open(os.path.join("generated", filename), "wb") as pfile:
    plistlib.dump(icon, pfile)
