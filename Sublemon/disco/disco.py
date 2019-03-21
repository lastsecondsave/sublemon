import os
import json


class Style:
    def __init__(self, foreground=None, font_style=None, **settings):
        self.settings = settings
        if foreground:
            self.settings['foreground'] = foreground
        if font_style:
            self.settings['font_style'] = font_style

    def __add__(self, other):
        settings = self.settings.copy()
        settings.update(other.settings)
        return Style(**settings)

    def __radd__(self, other):
        settings = self.settings.copy()
        settings['foreground'] = other
        return Style(**settings)


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
ORANGE       = "#FFAD3A"
DARK_ORANGE  = "#FF8147"
CRIMSON      = "#E5476C"

BLUISH_BLACK = "#202830"
DARK_BLUE    = "#384868"

FADED_GRAY   = "#51515D"
FADED_VIOLET = "#5E5E8E"


BACKGROUND = Style(background=BLUISH_BLACK)
FOREGROUND = Style(WHITE)

ITALIC = Style(font_style='italic')
BOLD = Style(font_style='bold')
BOLD_ITALIC = Style(font_style='bold italic')

FADED_HIGHLIGHT = Style(background=alpha(FADED_GRAY, 0.5))
INVALID_HIGHLIGHT = Style(background=alpha(CRIMSON, 0.5))

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
VARIABLE_MARKER = Style(DARK_ORANGE)

RAINBOW = Style([GREEN, PINK])
INVALID = CLEAR_WHITE + INVALID_HIGHLIGHT

REGEXP_GROUP = Style(ORANGE)
REGEXP_CHARACTER_CLASS = Style(PURPLE)
REGEXP_CONTROL = Style(PINK)


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
    path = os.path.abspath(path)

    with open(path, 'w') as json_file:
        json.dump(color_scheme, json_file, indent=2)

    print('Generated {}'.format(path))


color_scheme = {
    'name': 'Disco',

    'globals': {
        'background': BLUISH_BLACK,
        'foreground': WHITE,
        'caret': CLEAR_WHITE,
        'highlight': CLEAR_WHITE,
        'selection': DARK_BLUE,
        'line_highlight': alpha(CRIMSON, 0.2),
        'find_highlight': YELLOW,
        'minimap_border': CLEAR_WHITE,
        'brackets_foreground': DARK_ORANGE,

        'line_diff_width': '2',
        'line_diff_added': alpha(FADED_GRAY, 0.5),
        'line_diff_modified': alpha(FADED_VIOLET, 0.5),
        'line_diff_deleted': alpha(FADED_VIOLET, 0.5)
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
rec(PRIMITIVE,
    'constant.character.escape')
rec(STRING,
    'string')
rec(STORAGE,
    'storage',
    'support.type',
    'support.class',
    'entity.other.inherited-class')
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
rec(ITALIC, 'markup.italic -punctuation')
rec(BOLD, 'markup.bold -punctuation')

#### INLINE DIFF ####

rec(BACKGROUND, 'diff.inserted')
rec(FADED_HIGHLIGHT, 'diff.inserted.char')
rec(GRAY + ITALIC + BACKGROUND, 'diff.deleted')
rec(INVALID_HIGHLIGHT, 'diff.deleted.char')

#### PYTHON ####

src('python')
rec(KEYWORD,
    'keyword.operator.logical')
rec(INDEXED,
    'entity.name.function.decorator')
rec(META,
    'meta.annotation & (-meta.annotation.arguments -punctuation.section | support.function)')
rec(ITALIC,
    'meta.annotation')
rec(BOLD,
    'support.function -support.function.magic')
rec(STRING,
    'string keyword.operator')
rec(STRING + BOLD_ITALIC,
    'string source.sql keyword')
rec(STRING + ITALIC,
    'string source.sql storage')

#### REGEXP IN PYTHON ####

rec(REGEXP_GROUP,
    'source.regexp punctuation.definition.group',
    'source.regexp keyword.operator.or')
rec(REGEXP_CHARACTER_CLASS,
    'source.regexp constant.character.character-class',
    'source.regexp constant.other.character-class.set')

#### PYLINT ####

txt('log.pylint')
rec(RAINBOW, 'constant.language.classifier')

#### JAVASCRIPT ####

src('js')
rec(TAG + ITALIC,
    'meta.object-literal.key')
rec(STORAGE,
    'variable.type',
    'support.constant.builtin')
rec(OPERATOR,
    'storage.type.function.arrow')
rec(STRING,
    'meta.template.expression')
rec(VARIABLE,
    'support.type.object.dom')
rec(PUNCTUATION,
    'punctuation.definition.template-expression')
rec(FOREGROUND,
    'meta.binding.name variable.other.readwrite')

#### REGEXP IN JAVASCRIPT ####

rec(REGEXP_GROUP,
    'string.regexp punctuation.definition.group',
    'keyword.operator.or.regexp')
rec(REGEXP_CHARACTER_CLASS,
    'string.regexp constant.other.character-class')
rec(REGEXP_CONTROL,
    'string.regexp && (keyword.control | keyword.operator)',
    'constant.other.character-class.set.regexp constant.other.character-class.escape')

#### REGEXP ####

src('regexp')
rec(TAG,
    'meta.group keyword.other.named-capture-group punctuation.definition.capture-group-name')
rec(REGEXP_GROUP,
    'keyword.control.group',
    'keyword.other.conditional',
    'constant.other.assertion',
    'keyword.operator.alternation',
    'keyword.other.named-capture-group')
rec(REGEXP_CHARACTER_CLASS,
    'meta.set',
    'keyword.control.set',
    'keyword.control.character-class')
rec(REGEXP_CONTROL,
    'meta.set keyword.control.character-class',
    'keyword.control',
    'keyword.operator',
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
    'keyword.operator.wildcard',
    'keyword.other.package')
rec(PRIMITIVE,
    'string.quoted.single')
rec(CRIMSON,
    'keyword.operator.wildcard.asterisk',
    'meta.class.body.anonymous.java punctuation.section.braces')
rec(FADED_VIOLET,
    'text.html meta.tag entity.name',
    'text.html constant.character.entity',
    'constant.character.entity.named punctuation.terminator.entity',
    'text.html meta.tag punctuation.definition.tag')
rec(FADED_GRAY,
    'meta.inline-tag & (keyword.other | punctuation.section)')
rec(COMMENT + ITALIC,
    'markup.underline.link')
rec(COMMENT,
    'markup.raw')
rec(FOREGROUND,
    'storage.modifier.array',
    'storage.type.function.anonymous')
rec(ITALIC,
    'meta.annotation',
    'variable.parameter.javadoc')

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
rec(ORANGE, 'meta.indicator.warning')
rec(GREEN, 'meta.indicator.success')
rec(YELLOW, 'meta.message')

#### C# ####

src('cs')
rec(KEYWORD,
    'keyword.operator.new')
rec(FADED_VIOLET,
    'comment.block.documentation punctuation.definition.tag',
    'comment.block.documentation entity.name.tag',
    'comment.block.documentation entity.other',
    'comment.block.documentation punctuation.separator')
rec(FOREGROUND,
    'comment.block.documentation string.quoted.double')

#### POWERSHELL ####

src('powershell')
rec(VARIABLE_MARKER,
    'punctuation.definition.variable')
rec(PUNCTUATION,
    'keyword.operator.other',
    'variable.other punctuation.section.braces',
    'string.quoted.double punctuation.section.group -interpolated',
    'string.quoted.double punctuation.section.braces -interpolated')
rec(META,
    'support.function.attribute',
    'meta.attribute variable.parameter.attribute')
rec(ITALIC,
    'meta.attribute - punctuation.section.bracket',
    'keyword.operator.comparison',
    'keyword.operator.logical',
    'keyword.operator.unary')
rec(VARIABLE,
    'variable storage.modifier.scope')
rec(FOREGROUND,
    'string.quoted.double interpolated.complex -string.quoted.single',
    'support.constant variable.other')

#### SHELL ####

src('shell')
rec(VARIABLE_MARKER,
    'punctuation.definition.variable')
rec(PUNCTUATION,
    'meta.group.expansion punctuation.section',
    'keyword.operator.expansion',
    'keyword.operator.logical.pipe',
    'keyword.operator.assignment.redirection')
rec(FOREGROUND,
    'keyword.control.case.item',
    'variable.language.tilde',
    'variable.parameter.option',
    'string.quoted.double meta.group.expansion.command -string.quoted.single')

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
    'punctuation.definition.alias')
rec(TAG,
    'punctuation.definition.directive.begin',
    'constant.language.merge',
    'keyword.other.directive.yaml')
rec(CRIMSON + ITALIC,
    'variable.other.alias',
    'punctuation.definition.alias',
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
rec(ITALIC,
    'support.type.property-name')

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
rec(ITALIC,
    'meta.tag.sgml -comment')
rec(TAG + BOLD_ITALIC,
    'meta.tag.sgml.doctype keyword')
rec(PUNCTUATION,
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
rec(FADED_GRAY,
    'punctuation.definition.bold',
    'punctuation.definition.italic')
rec(FOREGROUND,
    'punctuation.separator.key-value.html')

#### DIFF ####

src('diff')
rec(META + ITALIC, 'meta.diff.range')
rec(CLEAR_WHITE + BOLD_ITALIC, 'entity.name.section')
rec(BLUE, 'meta.diff.header')
rec(GREEN, 'markup.inserted')
rec(CRIMSON, 'markup.deleted')
rec(CRIMSON, 'markup.changed')

#### GIT ####

txt('git.config')
rec(YELLOW,
    'meta.brackets',
    'entity.name.section')
rec(INDEXED,
    'variable.other.readwrite')

txt('git.merge-conflict')
rec(FADED_HIGHLIGHT,
    'meta.branch',
    'meta.separator')
rec(CLEAR_WHITE + BOLD,
    'variable.other.branch')

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
