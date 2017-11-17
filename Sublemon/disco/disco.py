import os
import json


class Style:
    def __init__(self, foreground=None, **settings):
        self.settings = settings
        if foreground:
            self.settings['foreground'] = foreground


def alpha(color, value):
    return 'color({} alpha({}))'.format(color, value)


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


BACKGROUND = Style(BLUISH_BLACK)
FOREGROUND = Style(WHITE)
KEYWORD = Style(PURPLE)
STORAGE = Style(PINK)
INDEXED = Style(BLUE)
OPERATOR = Style(WHITE)
PUNCTUATION = Style(DARK_ORANGE)
COMMENT = Style(GRAY)
COMMENT_HIGHLIGHT = Style(WHITE)
PRIMITIVE = Style(DARK_ORANGE)
STRING = Style(GREEN)
META = Style(YELLOW)
TAG = Style(BLUE)
TAG_ATTRIBUTE = Style(YELLOW)
PARAMETER = Style(ORANGE)
USER_CONSTANT = Style(CRIMSON)
VARIABLE = Style(ORANGE)
SUPPORT = Style(PINK)
INVALID = Style(foreground=CLEAR_WHITE,
                background=alpha(CRIMSON, 0.5))


def sec(scope=None):
    global global_scope
    global_scope = scope


def src(lang):
    sec('source.' + lang)


def txt(lang):
    sec('text.' + lang)


def rec(style, *scopes):
    global global_scope
    global color_scheme

    if type(style) is not Style:
        style = Style(style)

    for scope in scopes:
        if global_scope:
            scope = ' '.join([global_scope, scope])

        color_scheme['rules'].append(dict(style.settings, scope=scope))


def generate():
    global color_scheme

    path = os.path.join('..', 'Disco.sublime-color-scheme')
    with open(path, 'w') as json_file:
        json.dump(color_scheme, json_file, indent=2)


color_scheme = {
    'name': 'Disco',

    'globals': {
        'background' : BLUISH_BLACK,
        'foreground' : WHITE,
        'caret' : CLEAR_WHITE,
        'highlight' : CLEAR_WHITE,
        'selection' : DARK_BLUE,
        'line_highlight' : alpha(CRIMSON, 0.2),
        'find_highlight' : YELLOW,
        'minimapBorder' : CLEAR_WHITE,
        'brackets_foreground' : DARK_ORANGE
    },

    'rules': []
}

global_scope = None

#### FOUNDATION ####

rec(COMMENT,
    'comment')
rec(PRIMITIVE,
    'constant.numeric',
    'constant.character',
    'constant.language',
    'storage.type.numeric',
    'punctuation.separator.decimal')
rec(STRING,
    'string')
rec(STORAGE,
    'storage',
    'entity.other.inherited-class')
rec(SUPPORT,
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
    'punctuation.terminator',
    'punctuation.accessor')
rec(PARAMETER,
    'variable.parameter')
rec(USER_CONSTANT,
    'constant.user')
rec(VARIABLE,
    'variable.language',
    'support.constant',
    'support.variable')
rec(PUNCTUATION,
    'punctuation.separator.continuation')
rec(INVALID,
    'invalid')

#### MARKUP ####

rec(STRING, 'markup.raw')
rec(BLUE, 'markup.heading')
rec(YELLOW, 'markup.underline.link')
rec(ORANGE, 'markup.italic')
rec(CRIMSON, 'markup.bold')

#### PYTHON ####

src('python')
rec(KEYWORD,
    'keyword.operator.logical')
rec(INDEXED,
    'entity.name.function support.function.magic',
    'entity.name.function.decorator',
    'entity.name.function.decorator support.function.builtin')
rec(META,
    'meta.annotation & (-meta.annotation.arguments -punctuation.section | support.function)')
rec(Style(foreground=GREEN, background=alpha(CLEAR_WHITE, 0.1)),
    'string keyword', 'string keyword.operator')

#### JAVASCRIPT ####

src('js')
rec(KEYWORD,     'meta.instance.constructor keyword.operator.new',
                 'meta.for meta.group keyword.operator', # 'of' and 'in' in for-cycle
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

src('regexp')
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

src('java')
rec(META,
    'punctuation.definition.annotation',
    'variable.annotation.java',
    'meta.annotation variable.parameter')
rec(COMMENT_HIGHLIGHT,
    'comment.block.documentation & (keyword | variable.parameter)')
rec(USER_CONSTANT,
    'entity.name.constant',
    'constant.other')
rec(STORAGE,
    'keyword.operator.wildcard')
rec(PRIMITIVE,
    'string.quoted.single')
rec(CRIMSON,
    'support.other.package')
rec(DARK_VIOLET,
    'text.html constant.character.entity',
    'text.html meta.tag punctuation',
    'text.html meta.tag punctuation.separator',
    'text.html meta.tag punctuation.definition.tag',
    'text.html meta.tag string',
    'text.html meta.tag entity.other.attribute-name',
    'text.html meta.tag entity.name',
    'text.html meta.tag.inline',
    'text.html meta.attribute-with-value.style source.css')
rec(DARK_GRAY,
    'meta.directive keyword',
    'meta.directive punctuation.definition')
rec(COMMENT,
    'meta.directive markup.raw',
    'meta.directive markup.underline.link',
    'meta.directive.link string.other.link.title',
    'meta.directive.linkplain string.other.link.title',
    'markup.underline.link')
rec(FOREGROUND,
    'storage.modifier.array',
    'storage.type.function.anonymous')

#### JAVA LOG ####

txt('log.java')
rec(CRIMSON, 'entity.name.exception')

#### LOG ####

txt('log')
rec(CRIMSON, 'meta.indicator.error')
rec(ORANGE,  'meta.indicator.warning')
rec(GREEN,   'meta.indicator.success')
rec(YELLOW,  'meta.message')

#### POWERSHELL ####

src('powershell')
rec(PUNCTUATION, 'punctuation.definition.expression',
                 'keyword.operator.pipe',
                 'keyword.operator.stream')
rec(CRIMSON,     'keyword.operator.execute',
                 'keyword.operator.escape')
rec(OPERATOR,    'punctuation.separator.static-call')
rec(VARIABLE,    'string.quoted.double variable.user')
rec(FOREGROUND,  'variable.user')

#### SHELL ####

src('shell')
rec(KEYWORD,     'punctuation.definition.command-substitution',
                 'punctuation.definition.parameter-expansion')
rec(VARIABLE,    'variable.other.definition')
rec(PUNCTUATION, 'meta.block.command-substitution punctuation.section',
                 'meta.block.parameter-expansion punctuation.section',
                 'keyword.operator.pipe',
                 'keyword.operator.logical',
                 'punctuation.separator.continuation')

#### C++ ####

src('c++')
rec(USER_CONSTANT, 'entity.name.constant.preprocessor')
rec(KEYWORD,       'keyword.operator.word')
rec(OPERATOR,      'punctuation.accessor')

#### YAML ####

src('yaml')
rec(PUNCTUATION, 'keyword.operator')
rec(VARIABLE,    'variable.other')

#### CSS ####

src('css')
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

txt('xml')
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
    'meta.tag.sgml keyword',
    'meta.tag.sgml punctuation.definition.tag')
rec(DARK_ORANGE,
    'meta.block.substitution punctuation -comment.block')
rec(COMMENT,
    'comment.block meta.block.substitution variable.other')

#### HTML ####

txt('html')
rec(TAG,
    'meta.tag punctuation.definition.tag',
    'meta.tag.sgml.doctype')
rec(TAG_ATTRIBUTE,
    'meta.tag entity.other.attribute-name')
rec(STRING,
    'meta.attribute-with-value.style source.css')

#### MARKDOWN ####

txt('html.markdown')
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

src('diff')
rec(META,    'meta.diff.range')
rec(BLUE,    'meta.diff.header')
rec(GREEN,   'markup.inserted')
rec(CRIMSON, 'markup.deleted')

txt('git.merge-conflict')
rec(Style(foreground=CLEAR_WHITE, background=alpha(YELLOW, 0.2)),
    'meta.upsteam',
    'meta.changes')
rec(Style(foreground=CLEAR_WHITE, background=alpha(DARK_ORANGE, 0.2)),
    'meta.separator')

#### ETC ####

sec()
rec(YELLOW,
    'meta.section.ini',
    'entity.name.section.ini')

rec(DARK_VIOLET, 'constant.date.git')
rec([GREEN, PINK], 'text.git.blame constant.numeric.hash')

generate()
