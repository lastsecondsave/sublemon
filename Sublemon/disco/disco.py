import os
import sys

sys.path.append("../lib")
from settings import write_plist


GRAY         = "#9090A0"
DARK_GRAY    = "#51515D"
WHITE        = "#C4C4C4"
CLEAR_WHITE  = "#FFFFFF"
DARK_VIOLET  = "#5E5E8E"
PURPLE       = "#E572D2"
PINK         = "#EF51AA"
BLUE         = "#6699FF"
DARK_BLUE    = "#384868"
BLUISH_BLACK = "#202830"
GREEN        = "#C5CC4B"
YELLOW       = "#EDC61A"
ORANGE       = "#FF9A41"
DARK_ORANGE  = "#FF8147"
CRIMSON      = "#E5476C"


BACKGROUND        = BLUISH_BLACK
FOREGROUND        = WHITE
KEYWORD           = PURPLE
STORAGE           = PINK
INDEXED           = BLUE
OPERATOR          = WHITE
PUNCTUATION       = DARK_ORANGE
COMMENT           = GRAY
COMMENT_HIGHLIGHT = WHITE
PRIMITIVE         = DARK_ORANGE
STRING            = GREEN
META              = YELLOW
TAG               = BLUE
TAG_ATTRIBUTE     = YELLOW
PARAMETER         = ORANGE
USER_CONSTANT     = CRIMSON
VARIABLE          = ORANGE
INHERITED         = CRIMSON


def alpha(color, value):
    return color + '{:02X}'.format(round(255 * value))


def group(category, lang):
    global current_lang, current_category
    current_lang, current_category = lang, category


def source(lang):
    group('source', lang)


def no_group():
    group(None, None)


def rec(color, *scopes, **settings):
    global theme_settings

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


def generate():
    global theme_settings

    path = os.path.join('..', 'Disco.tmTheme')
    write_plist(path, {'name': "Disco", 'settings': theme_settings})


theme_settings = [{
    'settings': {
        'background'         : BACKGROUND,
        'foreground'         : FOREGROUND,
        'caret'              : CLEAR_WHITE,
        'highlight'          : CLEAR_WHITE,
        'selection'          : DARK_BLUE,
        'lineHighlight'      : alpha(CRIMSON, 0.2),
        'findHighlight'      : YELLOW,
        'minimapBorder'      : FOREGROUND,
        'bracketsForeground' : PUNCTUATION
    }
}]

#### FOUNDATION ####

no_group()
rec(COMMENT,
    'comment')
rec(PRIMITIVE,
    'constant.numeric',
    'constant.character',
    'constant.language',
    'punctuation.separator.decimal')
rec(STRING,
    'string')
rec(STORAGE,
    'storage',
    'support.type',
    'support.class',
    'support.function')
rec(KEYWORD,
    'keyword',
    'keyword.operator.alphanumeric',
    'keyword.operator.word',
    'storage.modifier')
rec(OPERATOR,
    'keyword.operator')
rec(INDEXED,
    'entity.name')
rec(FOREGROUND,
    'punctuation.separator',
    'punctuation.terminator')
rec(PARAMETER,
    'variable.parameter')
rec(USER_CONSTANT,
    'constant.user')
rec(VARIABLE,
    'variable.language',
    'support.constant',
    'support.variable')
rec(INHERITED,
    'entity.other.inherited-class')
rec(FOREGROUND,
    'invalid',
    background=alpha(CRIMSON, 0.5))

#### PYTHON ####

source('python')
rec(KEYWORD,     'keyword.operator.logical')
rec(INDEXED,     'entity.name.function support.function.magic',
                 'entity.name.function.decorator',
                 'entity.name.function.decorator support.function.builtin')
rec(META,        'meta.annotation -meta.annotation.arguments -punctuation.section',
                 'meta.annotation support.function')
rec(PUNCTUATION, 'punctuation.separator.continuation.line')

#### JAVASCRIPT ####

source('js')
rec(KEYWORD,     'meta.instance.constructor keyword.operator.new',
                 'meta.for meta.group #keyword.operator', # 'of' and 'in' in for-cycle
                 'keyword.operator.word.new')
rec(STORAGE,     'variable.type')
rec(BLUE,        'meta.object-literal.key')
rec(OPERATOR,    'storage.type.function.arrow')
rec(ORANGE,      'support.type.object',
                 'meta.template.expression')
rec(DARK_ORANGE, 'meta.template.expression punctuation.definition.template-expression')
rec(FOREGROUND,  'support.function')

#### REGEXP IN JAVASCRIPT ####

rec(YELLOW, 'keyword.operator.or.regexp',
            'punctuation.definition.group.regexp')
rec(PURPLE, 'keyword.operator.quantifier.regexp',
            'constant.other.character-class.escape.backslash.regexp')
rec(PINK,   'keyword.operator.quantifier.regexp')

#### REGEXP ####

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

#### JAVA ####

source('java')
rec(META,
    'punctuation.definition.annotation',
    'variable.annotation.java',
    'meta.annotation variable.parameter')
rec(COMMENT_HIGHLIGHT,
    'comment.block.documentation keyword',
    'comment.block.documentation variable.parameter')
rec(USER_CONSTANT,
    'entity.name.constant',
    'constant.other')
rec(STORAGE,
    'keyword.operator.wildcard',
    'support.class punctuation.accessor.dot',
    'constant.other punctuation.accessor.dot')
rec(CRIMSON,
    'support.other.package')
rec(DARK_VIOLET,
    'text.html constant.character.entity',
    'text.html meta.tag punctuation',
    'text.html meta.tag punctuation.separator',
    'text.html meta.tag punctuation.definition.tag',
    'text.html meta.tag string',
    'text.html meta.attribute-with-value.style source.css',
    'text.html meta.tag entity.other.attribute-name',
    'text.html meta.tag entity.name')
rec(DARK_GRAY,
    'meta.directive keyword',
    'meta.directive punctuation.definition')
rec(COMMENT,
    'meta.directive markup.raw',
    'meta.directive markup.underline.link',
    'meta.directive.link string.other.link.title',
    'meta.directive.linkplain string.other.link.title')
rec(FOREGROUND,
    'storage.modifier.array',
    'storage.type.function.anonymous')

#### JAVA LOG ####

group('text.log', 'java')
rec(CRIMSON, 'entity.name.exception')

#### LOG ####

group('text', 'log')
rec(CRIMSON, 'meta.indicator.error')
rec(ORANGE,  'meta.indicator.warning')
rec(GREEN,   'meta.indicator.success')
rec(YELLOW,  'meta.message')

#### POWERSHELL ####

source('powershell')
rec(PUNCTUATION, 'punctuation.definition.expression',
                 'keyword.operator.pipe',
                 'keyword.operator.stream')
rec(CRIMSON,     'keyword.operator.execute',
                 'keyword.operator.escape')
rec(OPERATOR,    'punctuation.separator.static-call')
rec(VARIABLE,    'string.quoted.double variable.user')
rec(FOREGROUND,  'variable.user')

#### SHELL ####

source('shell')
rec(KEYWORD,     'punctuation.definition.command-substitution',
                 'punctuation.definition.parameter-expansion')
rec(VARIABLE,    'variable.other.definition')
rec(PUNCTUATION, 'meta.block.command-substitution punctuation.section',
                 'meta.block.parameter-expansion punctuation.section',
                 'keyword.operator.pipe',
                 'keyword.operator.logical',
                 'punctuation.separator.continuation')

#### C++ ####

source('c++')
rec(USER_CONSTANT, 'entity.name.constant.preprocessor')
rec(KEYWORD,       'keyword.operator.word')
rec(OPERATOR,      'punctuation.accessor')

#### YAML ####

source('yaml')
rec(PUNCTUATION, 'keyword.operator')
rec(VARIABLE,    'variable.other')

#### CSS ####

source('css')
rec(PRIMITIVE,
    'constant.numeric keyword.other',
    'constant.other.color')
rec(TAG_ATTRIBUTE,
    'entity.other.attribute-name')
rec(FOREGROUND,
    'support.function')
rec(CRIMSON,
    'support.type.vendor-prefix')

#### XML ####

group('text', 'xml')
rec(TAG,
    'meta.tag punctuation.definition.tag')
rec(TAG_ATTRIBUTE,
    'meta.tag entity.other.attribute-name')
rec(PUNCTUATION,
    'string.unquoted.cdata punctuation')
rec(FOREGROUND,
    'string.unquoted.cdata')
rec(VARIABLE,
    'meta.tag.sgml.doctype variable',
    'variable.other.substitution')
rec(CRIMSON,
    'meta.tag.sgml.doctype keyword',
    'meta.tag.sgml.doctype punctuation.definition.tag')
rec(DARK_ORANGE,
    'meta.block.substitution punctuation -comment.block')
rec(COMMENT,
    'comment.block meta.block.substitution variable.other')

#### HTML ####

group('text', 'html')
rec(TAG,           'meta.tag punctuation.definition.tag',
                   'meta.tag.sgml.doctype')
rec(TAG_ATTRIBUTE, 'meta.tag entity.other.attribute-name')
rec(STRING,        'meta.attribute-with-value.style source.css')

#### MARKDOWN ####

group('text.html', 'markdown')
rec(PARAMETER,   'meta.link.inline.description',
                 'meta.link.reference.literal.description',
                 'meta.link.reference.description',
                 'meta.image.inline.description',
                 'meta.image.reference.description',
                 'constant.other.reference.link')
rec(TAG,         'meta.tag')
rec(PUNCTUATION, 'meta.link.inline punctuation.definition.link',
                 'meta.link.reference punctuation.definition.link',
                 'punctuation.definition.list_item',
                 'markup.list.numbered.bullet',
                 'punctuation.definition.raw.code-fence',
                 'punctuation.definition.blockquote',
                 'punctuation.definition.constant',
                 'punctuation.definition.image',
                 'punctuation.separator',
                 'punctuation.definition.thematic-break')
rec(STRING,      'punctuation.definition.string')
rec(YELLOW,      'meta.link',
                 'meta.image',
                 'entity.other.attribute-name.class.html')
rec(FOREGROUND,  'punctuation.separator.key-value.html')

#### DIFF ####

source('diff')
rec(META,    'meta.diff.range')
rec(BLUE,    'meta.diff.header')
rec(GREEN,   'markup.inserted')
rec(CRIMSON, 'markup.deleted')

#### COMMON ####

no_group()

#### MARKUP ####

rec(STRING,  'markup.raw')
rec(BLUE,    'markup.heading')
rec(YELLOW,  'markup.underline.link')
rec(ORANGE,  'markup.italic')
rec(CRIMSON, 'markup.bold')

#### ETC ####

rec(GREEN,       'meta.not-commited-yet.git constant.numeric.line-number')
rec(DARK_VIOLET, 'constant.date.git')
rec(YELLOW,      'meta.section.ini',
                 'entity.name.section.ini')


generate()
