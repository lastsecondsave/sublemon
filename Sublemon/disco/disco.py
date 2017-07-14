import os
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
TAG_ATTRIBUTE     = YELLOW
PARAMETER         = ORANGE
USER_CONSTANT     = CRIMSON
CONSTANT          = ORANGE
INHERITED         = CRIMSON

def alpha(color, value):
  return color + '{:02X}'.format(round(255 * value))

theme_settings = [
  {'settings': {
    'background'         : BACKGROUND,
    'foreground'         : FOREGROUND,
    'caret'              : CLEAR_WHITE,
    'selection'          : DARK_BLUE,
    'lineHighlight'      : alpha(CRIMSON, 0.2),
    'findHighlight'      : YELLOW,
    'minimapBorder'      : FOREGROUND,
    'bracketsForeground' : PUNCTUATION
  }}
]

def group(category, lang):
  global current_lang, current_category
  current_lang, current_category = lang, category

def source(lang):
  group('source', lang)

def no_group():
  group(None, None)

def rec(color, *scopes, **settings):
  settings['foreground'] = color

  for scope in scopes:
    chunks = [current_category + '.' + current_lang] if current_category != None else []
    chunks += scope.split()

    for i, chunk in enumerate(chunks):
      if chunk.startswith('#') and current_lang != None:
        chunks[i] = chunk[1:] + '.' + current_lang

    theme_settings.append({
      'scope':  ' '.join(chunks),
      'settings': settings
    })

## FOUNDATION ##

no_group()
rec(COMMENT,       'comment')
rec(PRIMITIVE,     'constant.numeric',
                   'constant.character',
                   'punctuation.separator.decimal')
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
                   'support.constant',
                   'support.variable',
                   'variable.language',
                   'variable.user')
rec(INHERITED,     'entity.other.inherited-class')
rec(FOREGROUND,    'invalid', background=CRIMSON)

## PYTHON ##

source('python')
rec(KEYWORD,     'keyword.operator.logical')
rec(INDEXED,     'entity.name.function support.function.magic',
                 'entity.name.function.decorator',
                 'entity.name.function.decorator support.function.builtin')
rec(META,        'meta.annotation -meta.annotation.arguments -punctuation.section',
                 'meta.annotation support.function')
rec(PUNCTUATION, 'punctuation.separator.continuation.line')

## REGEXP IN PYTHON ##

rec(YELLOW, 'source.regexp punctuation.definition.group')
rec(PURPLE, 'source.regexp constant.other.character-class.set',
            'constant.character.character-class.regexp')

## JAVASCRIPT ##

source('js')
rec(KEYWORD,     'meta.instance.constructor keyword.operator.new',
                 'meta.for meta.group #keyword.operator') # 'of' and 'in' in for-cycle
rec(STORAGE,     'variable.type')
rec(LIGHT_BLUE,  'meta.object-literal.key')
rec(OPERATOR,    'storage.type.function.arrow')
rec(ORANGE,      'support.type.object',
                 'meta.template.expression')
rec(DARK_ORANGE, 'meta.template.expression punctuation.definition.template-expression')
rec(FOREGROUND,  'support.function')

## REGEXP IN JAVASCRIPT ##

rec(YELLOW, 'keyword.operator.or.regexp',
            'punctuation.definition.group.regexp')
rec(PURPLE, 'keyword.operator.quantifier.regexp',
            'constant.other.character-class.escape.backslash.regexp')
rec(PINK,   'keyword.operator.quantifier.regexp')

## REGEXP ##

source('regexp')
rec(YELLOW,  'keyword.operator.or',
             'punctuation.definition.group')
rec(PURPLE,  'constant.language.character-class',
             'constant.character -constant.character.escape')
rec(PINK,    'constant.language.character-class constant.language.character-class', # Character classes in group
             'keyword.control',
             'keyword.operator')
rec(CRIMSON, 'keyword.modifier',
             'meta.group.modifier punctuation.definition.group.modifier')

## JAVA ##

source('java')
rec(META,              'punctuation.definition.annotation',
                       'meta.annotation.identifier storage.type',
                       'variable.parameter.annotation')
rec(COMMENT_HIGHLIGHT, 'comment.block.documentation keyword',
                       'comment.block.documentation variable.parameter')
rec(CRIMSON,           'meta.package storage.type',
                       'storage.type.asterisk',
                       'keyword.control.assert',
                       'meta.class.body.anonymous punctuation.definition.class',
                       'meta.extends.statement storage.type -meta.generic',
                       'meta.implements.statement storage.type -meta.generic',
                       'meta.throws.statement storage.type -meta.generic')
rec(DARK_ORANGE,       'storage.type.generic')
rec(DARK_GRAY,         'keyword.documentation.inline')
rec(DARK_VIOLET,       'meta.tag.javadoc')

## JAVA LOG ##

group('text.log', 'java')
rec(CRIMSON, 'entity.name.exception')

## LOG ##

group('text', 'log')
rec(CRIMSON, 'meta.indicator.error')
rec(ORANGE,  'meta.indicator.warning')
rec(GREEN,   'meta.indicator.success')
rec(YELLOW,  'meta.message')

## POWERSHELL ##

source('powershell')
rec(PUNCTUATION, 'punctuation.definition.expression',
                 'keyword.operator.pipe',
                 'keyword.operator.stream')
rec(CRIMSON,     'keyword.operator.execute',
                 'keyword.operator.escape')
rec(OPERATOR,    'punctuation.separator.static-call')

## C++ ##

source('c++')
rec(USER_CONSTANT, 'entity.name.constant.preprocessor')
rec(KEYWORD,       'keyword.operator.word')
rec(OPERATOR,      'punctuation.accessor')

## XML ##

source('xml')
rec(TAG,           'entity.name.tag',
                   'keyword',
                   'punctuation.definition')
rec(STRING,        'meta.attribute string')
rec(PUNCTUATION,   'meta.cdata punctuation.definition')
rec(TAG_ATTRIBUTE, 'entity.name.attribute',
                   'entity.name.doctype.element')
rec(DARK_ORANGE,   'punctuation.definition.substitution')

## YAML ##

source('yaml')
rec(PUNCTUATION, 'keyword.operator')

## CSS ##

source('css')
rec(PINK,        'meta.rule.selector entity.name.general')
rec(YELLOW,      'meta.rule.selector entity.name.id')
rec(CRIMSON,     'meta.rule.selector entity.name.class')
rec(PURPLE,      'meta.rule.selector entity.name.pseudo-class')
rec(DARK_ORANGE, 'keyword.other.important')

## HTML ##

group('text', 'html')
rec(TAG,           'meta.tag punctuation.definition.tag',
                   'meta.tag.sgml.doctype')
rec(TAG_ATTRIBUTE, 'meta.tag entity.other.attribute-name')
rec(STRING,        'meta.attribute-with-value.style source.css')

## MARKDOWN ##

group('text.html', 'markdown')
rec(PARAMETER,   'meta.link.inline.description',
                 'meta.link.reference.literal.description',
                 'meta.link.reference.description',
                 'meta.image.inline.description',
                 'meta.image.reference.description',
                 'constant.other.reference.link')
rec(TAG,         'meta.tag')
rec(PUNCTUATION, 'meta.link.inline punctuation.definition',
                 'meta.link.reference punctuation.definition',
                 'punctuation.definition.list_item',
                 'markup.list.numbered.bullet',
                 'punctuation.definition.raw.code-fence',
                 'punctuation.definition.blockquote',
                 'punctuation.definition.constant',
                 'punctuation.definition.image',
                 'punctuation.separator',
                 'punctuation.definition.thematic-break')
rec(STRING,      'punctuation.definition.string')
rec(YELLOW,      'meta.link.email.lt-gt',
                 'meta.link.inet',
                 'entity.other.attribute-name.class.html')
rec(FOREGROUND,  'punctuation.separator.key-value.html')

## DIFF ##

source('diff')
rec(META,    'meta.diff.range')
rec(BLUE,    'meta.diff.header')
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
rec(YELLOW,      'meta.section.ini',
                 'entity.name.section.ini')

## ICONS ##

icons = []

def icon(name, *scopes):
  for scope in scopes:
    icons.append({
      'scope': scope,
      'settings': {'icon': 'file_type_' + name}
    })

icon('source', 'source')
icon('text',   'text',
               'text.html.markdown',
               'text.rfc',
               'text.restructuredtext')
icon('markup', 'text.html',
               'source.xml',
               'source.json',
               'source.yaml')
icon('css',    'source.css')

## GENERATOR ##

settings.write_plist(os.path.join('..', 'Disco.tmTheme'),
                     {'name': "Disco", 'settings': theme_settings})

settings.cleanup()
for icon in icons:
  settings.generate_settings_file(icon["scope"], icon)
