import os
import json


class Style:
    def __init__(self, foreground=None, **settings):
        self.settings = settings
        if foreground:
            self.settings['foreground'] = foreground


def alpha(color, value):
    return 'color({} alpha({}))'.format(color, value)


WHITE        = "#C4C4C4"
CLEAR_WHITE  = "#FFFFFF"

GRAY         = "#9090A0"
PURPLE       = "#E572D2"
PINK         = "#EF51AA"
BLUE         = "#6699FF"
GREEN        = "#C5CC4B"
YELLOW       = "#EDC61A"
ORANGE       = "#FF9A41"
DARK_ORANGE  = "#FF8147"
CRIMSON      = "#E5476C"

BLUISH_BLACK = "#202830"
DARK_BLUE    = "#384868"

FADED_GRAY   = "#51515D"
FADED_WHITE  = "#B0B0B0"
FADED_BLUE   = "#41415D"
FADED_VIOLET = "#5E5E8E"
FADED_GREEN  = "#949B43"


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
RAINBOW = Style([GREEN, PINK])
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

    if not isinstance(style, Style):
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

    print('Generated {}'.format(path))


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
rec(VARIABLE,
    'variable.language',
    'support.constant',
    'support.variable')
rec(PUNCTUATION,
    'punctuation.separator.continuation -source.c++')
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
rec(STRING,
    'string keyword.operator')
rec(FADED_GREEN,
    'string keyword')

#### PYLINT ####

txt('log.pylint')
rec(RAINBOW, 'constant.language.classifier')

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

rec(YELLOW,
    'string.regexp punctuation.definition.group',
    'keyword.operator.or.regexp')
rec(PURPLE,
    'string.regexp constant.other.character-class')
rec(PINK,
    'string.regexp && (keyword.control | keyword.operator)',
    'constant.other.character-class.set.regexp constant.other.character-class.escape')

#### REGEXP ####

src('regexp')
rec(TAG,
    'meta.group keyword.other.named-capture-group punctuation.definition.capture-group-name')
rec(YELLOW,
    'keyword.control.group',
    'keyword.other.conditional',
    'constant.other.assertion',
    'keyword.operator.alternation',
    'keyword.other.named-capture-group')
rec(PURPLE,
    'meta.set',
    'keyword.control.set',
    'keyword.control.character-class')
rec(PINK,
    'meta.set keyword.control.character-class',
    'keyword.control',
    'keyword.operator')
rec(CRIMSON,
    'storage.modifier.mode')

#### JAVA ####

src('java')
rec(META,
    'punctuation.definition.annotation',
    'variable.annotation',
    'meta.annotation variable.parameter')
rec(COMMENT_HIGHLIGHT,
    'comment.block.documentation keyword',
    'meta.block-tag variable.parameter')
rec(USER_CONSTANT,
    'entity.name.constant',
    'constant.other')
rec(STORAGE,
    'keyword.operator.wildcard')
rec(PRIMITIVE,
    'string.quoted.single')
rec(CRIMSON,
    'entity.name.namespace',
    'keyword.operator.wildcard.asterisk',
    'meta.class.body.anonymous.java punctuation.section.braces')
rec(FADED_VIOLET,
    'text.html meta.tag entity.name',
    'text.html constant.character.entity',
    'text.html meta.tag punctuation.definition.tag')
rec(FADED_BLUE,
    'text.html meta.tag punctuation',
    'text.html meta.tag punctuation.separator',
    'text.html meta.tag string',
    'text.html meta.tag string.quoted.single',
    'text.html meta.tag entity.other.attribute-name',
    'text.html meta.tag.inline',
    'source.css support.type',
    'source.css support.constant',
    'source.css string.quoted.single')
rec(FADED_GRAY,
    'meta.inline-tag & (keyword.other | punctuation.section)')
rec(FADED_WHITE,
    'markup.underline.link')
rec(COMMENT,
    'markup.raw')
rec(FOREGROUND,
    'storage.modifier.array',
    'support.function.import',
    'storage.type.function.anonymous')

#### JAVA PROPERTIES ####

src('java-props')
rec(FOREGROUND, 'string.unquoted')

#### JAVA LOG ####

txt('log.java')
rec(CRIMSON, 'entity.name.exception')

#### GROOVY ####

src('groovy')
rec(META, 'storage.type.annotation')

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
rec(VARIABLE,
    'variable.other.readwrite.assignment')
rec(PUNCTUATION,
    'punctuation.definition.variable',
    'punctuation.section.group',
    'string punctuation.section.parens',
    'punctuation.section.expansion.parameter',
    'keyword.operator.expansion',
    'keyword.operator.logical.pipe',
    'keyword.operator.assignment.redirection')
rec(FOREGROUND,
    'keyword.control.case.item',
    'support.function.double-brace',
    'support.function.test',
    'variable.language.tilde')

#### C++ ####

src('c++')
rec(USER_CONSTANT,
    'entity.name.constant.preprocessor')
rec(META,
    'meta.preprocessor keyword')
rec(KEYWORD,
    'keyword.operator.word')

#### YAML ####

src('yaml')
rec(PUNCTUATION,
    'punctuation.definition.block.sequence.item',
    'entity.other.document',
    'keyword.control.flow.block-scalar',
    'storage.modifier.chomping-indicator')
rec(VARIABLE,
    'variable.other.substitution.sublime-syntax',
    'variable.other.alias',
    'punctuation.definition.alias')
rec(TAG,
    'punctuation.definition.directive.begin',
    'keyword.other.directive.yaml')
rec(CRIMSON,
    'entity.name.other.anchor',
    'punctuation.definition.anchor')

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
    'variable.other.substitution -comment')
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
rec(PARAMETER,
    'meta.link.inline.description',
    'meta.link.reference.literal.description',
    'meta.link.reference.description',
    'meta.image.inline.description',
    'meta.image.reference.description',
    'constant.other.reference.link',
    'entity.name.reference.link.markdown')
rec(TAG,
    'meta.tag')
rec(PUNCTUATION,
    'meta.link.inline punctuation.definition.link',
    'meta.link.reference punctuation.definition.link',
    'punctuation.definition.list_item',
    'markup.list.numbered.bullet',
    'punctuation.definition.blockquote',
    'punctuation.definition.constant',
    'punctuation.definition.image',
    'punctuation.separator',
    'punctuation.definition.thematic-break')
rec(STRING,
    'punctuation.definition.string')
rec(YELLOW,
    'meta.link',
    'meta.image',
    'entity.other.attribute-name.class.html')
rec(FOREGROUND,
    'punctuation.separator.key-value.html')

#### DIFF ####

src('diff')
rec(META,    'meta.diff.range')
rec(BLUE,    'meta.diff.header')
rec(GREEN,   'markup.inserted')
rec(CRIMSON, 'markup.deleted')

#### GIT ####

txt('git.config')
rec(YELLOW,
    'meta.brackets',
    'entity.name.section')
rec(INDEXED,
    'variable.other.readwrite')

txt('git.merge-conflict')
rec(Style(foreground=CLEAR_WHITE, background=alpha(CLEAR_WHITE, 0.2)),
    'meta.upsteam',
    'meta.changes',
    'meta.separator')

txt('git.ignore')
rec(PUNCTUATION,
    'keyword.operator')
rec(FOREGROUND,
    'entity.name')

txt('git')
rec(FADED_VIOLET, 'constant.date')
rec(RAINBOW, 'constant.numeric.hash')

#### INI ####

src('ini')
rec(YELLOW,
    'meta.section',
    'entity.name.section')
rec(FOREGROUND, 'string.unquoted')

generate()
