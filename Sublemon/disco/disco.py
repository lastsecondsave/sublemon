import os
import re
import sys

sys.path.append("../lib")
import settings

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
DARK_BLUE    = "#384868" # [ 56,  72, 104]
BLUISH_BLACK = "#202830" # [ 32,  40,  48]
GREEN        = "#C5CC4B" # [197, 204,  75]
YELLOW       = "#EDC61A" # [239, 197,  45]
ORANGE       = "#FF9A41" # [255, 154,  65]
DARK_ORANGE  = "#FF8147" # [255, 129,  71]
CRIMSON      = "#E5476C" # [229,  71, 108]

BACKGROUND        = BLUISH_BLACK
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
CONSTANT          = ORANGE

def alpha(color, value):
  return color + '{:02X}'.format(round(255 * value))

def rule(name, scope, **settings):
  return dict(
    name = name,
    scope = re.sub("\s{2,}", ' ', scope),
    settings = settings
  )

theme_globals = dict(
  background         = BACKGROUND,
  foreground         = FOREGROUND,
  caret              = CLEAR_WHITE,
  selection          = DARK_BLUE,
  lineHighlight      = alpha(CRIMSON, 0.2),
  findHighlight      = YELLOW,
  minimapBorder      = FOREGROUND,
  bracketsForeground = PUNCTUATION
)

widget_globals = dict(
  background         = BACKGROUND,
  foreground         = FOREGROUND,
  caret              = CLEAR_WHITE,
  selection          = DARK_BLUE,
  bracketsForeground = PUNCTUATION
)

theme_settings = [
  rule("Language variable",         "variable.language", foreground = ORANGE),
  rule("User-defined variable",     "variable.user", foreground = ORANGE),
  rule("Inherited class",           "entity.other.inherited-class", foreground = CRIMSON),

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

  rule("CSS general selector",      "meta.rule.selector.css entity.name.general", foreground = PINK),
  rule("CSS id selector",           "meta.rule.selector.css entity.name.id", foreground = YELLOW),
  rule("CSS class selector",        "meta.rule.selector.css entity.name.class", foreground = CRIMSON),
  rule("CSS pseudo-class selector", "meta.rule.selector.css entity.name.pseudo-class", foreground = PURPLE),
  rule("CSS important",             "keyword.other.important.css", foreground = DARK_ORANGE),
]

widget_settings = []

def group(category, lang, widget=False):
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

    theme_settings.append(record_settings)
    if widget_category:
      widget_settings.append(record_settings)

## FOUNDATION ##

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
rec(CONSTANT,      'constant.language',
                   'support.constant')
rec(FOREGROUND,    'invalid', background=CRIMSON)

## PYTHON ##

source('python')
rec(KEYWORD, 'keyword.operator.logical')
rec(INDEXED, 'entity.name.function support.function.magic',
             'entity.name.function.decorator',
             'entity.name.function.decorator support.function.builtin')

## REGEXP IN PYTHON ##

rec(YELLOW, 'source.regexp #punctuation.definition.group')
rec(PURPLE, 'source.regexp #constant.other.character-class.set',
            '#constant.character.character-class.regexp')

## JAVASCRIPT ##

source('js')
rec(KEYWORD,     'meta.instance.constructor keyword.operator.new',
                 'meta.for keyword.operator')
rec(STORAGE,     'variable.type')
rec(LIGHT_BLUE,  'meta.object-literal.key')
rec(OPERATOR,    'storage.type.function.arrow')
rec(ORANGE,      '#support.type.object',
                 'meta.template.expression')
rec(DARK_ORANGE, 'meta.template.expression #punctuation.definition.template-expression')
rec(FOREGROUND,  '#support.function')

## REGEXP IN JAVASCRIPT ##

rec(YELLOW, '#keyword.operator.or.regexp',
            '#punctuation.definition.group.regexp')
rec(PURPLE, '#keyword.operator.quantifier.regexp',
            '#constant.other.character-class.escape.backslash.regexp')
rec(PINK,   '#keyword.operator.quantifier.regexp')

## REGEXP ##

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

## JAVA ##

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
rec(DARK_GRAY,         '#keyword.documentation.inline')
rec(DARK_VIOLET,       'meta.tag.javadoc')

## JAVA LOG ##

group('text.log', 'java')
rec(CRIMSON, '#entity.name.exception')

## POWERSHELL ##

source('powershell')

## C++ ##

source('c++')
rec(USER_CONSTANT, 'entity.name.constant.preprocessor')
rec(KEYWORD,       'keyword.operator.word')
rec(OPERATOR,      'punctuation.accessor')

## XML ##

source('xml')
rec(TAG,         'entity.name.tag',
                 '#keyword',
                 '#punctuation.definition')
rec(STRING,      'meta.attribute #string')
rec(PUNCTUATION, 'meta.cdata #punctuation.definition')
rec(YELLOW,      '#entity.name.attribute',
                 'entity.name.doctype.element')
rec(DARK_ORANGE, 'punctuation.definition.substitution')

## YAML ##

source('yaml')
rec(PUNCTUATION, '#keyword.operator')

## MARKDOWN ##

group('text.html', 'markdown')
rec(PARAMETER,   'meta.link.inline.description',
                 'meta.link.reference.literal.description',
                 'meta.link.reference.description',
                 'meta.image.inline.description',
                 'meta.image.reference.description',
                 'constant.other.reference.link')
rec(TAG,         '#meta.tag')
rec(PUNCTUATION, '#meta.link.inline #punctuation.definition',
                 '#meta.link.reference #punctuation.definition',
                 '#punctuation.definition.list_item',
                 'markup.list.numbered.bullet',
                 '#punctuation.definition.raw.code-fence',
                 'punctuation.definition.blockquote',
                 '#punctuation.definition.constant',
                 '#punctuation.definition.image',
                 '#punctuation.separator',
                 'punctuation.definition.thematic-break')
rec(STRING,      '#punctuation.definition.string')
rec(YELLOW,      'meta.link.email.lt-gt',
                 'meta.link.inet',
                 '#entity.other.attribute-name.class.html')
rec(FOREGROUND,  '#punctuation.separator.key-value.html')

## DIFF ##

source('diff')
rec(META,    '#meta.diff.range')
rec(BLUE,    '#meta.diff.header')
rec(GREEN,   'markup.inserted')
rec(CRIMSON, 'markup.deleted')

## COMMON ##

no_group()

## MARKUP ##

rec(STRING,  'markup.raw')
rec(BLUE,    'markup.heading')
rec(YELLOW,  'markup.underline.link')
rec(PINK,    'markup.italic')
rec(CRIMSON, 'markup.bold')

## ETC ##

rec(GREEN,       'meta.not-commited-yet.git constant.numeric.line-number')
rec(DARK_VIOLET, 'constant.date.git')

## ICONS ##

icons = []

def icon(name, *scopes):
  for scope in scopes:
    icons.append(dict(
      scope = scope,
      settings = dict(icon = 'file_type_' + name)
    ))

icon('cpp', 'source.c++')
icon('css', 'source.css')
icon('git', 'source.git')
icon('groovy', 'source.groovy')
icon('java', 'source.java')
icon('javascript', 'source.js')
icon('json', 'source.json')
icon('markup', 'text.html.markdown', 'text.rfc', 'text.restructuredtext')
icon('powershell', 'source.powershell')
icon('properties', 'source.ini', 'source.java-props')
icon('python', 'source.python')
icon('xml', 'source.xml')
icon('yaml', 'source.yaml')

## GENERATOR ##

theme_settings.append(dict(settings=theme_globals))
settings.write_plist(os.path.join("..", "Disco.tmTheme"),
    dict(name="Disco", settings=theme_settings))

widget_settings.append(dict(settings=widget_globals))
settings.write_plist(os.path.join("..", "Widget - Disco.tmTheme"),
    dict(name="Disco", settings=widget_settings))

settings.cleanup()
for icon in icons:
  settings.generate_settings_file(icon["scope"], icon)
