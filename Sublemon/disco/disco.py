# pylint: disable=bad-whitespace,global-statement,line-too-long

import json
import os


class Style:
    def __init__(self, foreground=None, **settings):
        self.settings = settings
        if foreground:
            self.settings['foreground'] = foreground

    def __add__(self, other):
        settings = self.settings.copy()
        settings.update(other.settings)
        return Style(**settings)

    def __radd__(self, other):
        settings = self.settings.copy()
        settings['foreground'] = other
        return Style(**settings)


class Highlight(Style):
    def __init__(self, background, background_alpha=0.5, foreground_adjust=None, **settings):
        settings['background'] = alpha(background, background_alpha)
        if foreground_adjust:
            settings['foreground_adjust'] = foreground_adjust
        super().__init__(**settings)


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


KEYWORD = Style(PURPLE)
STORAGE = Style(PINK)
INDEXED = Style(BLUE)
OPERATOR = Style(WHITE)
PUNCTUATION = Style(DARK_ORANGE)
COMMENT = Style(GRAY)
COMMENT_HIGHLIGHT = Style(WHITE)
PRIMITIVE = Style(DARK_ORANGE)
STRING = Style(GREEN)
META = Style(YELLOW) + ITALIC
TAG = Style(BLUE)
TAG_ATTRIBUTE = Style(YELLOW)
SECTION = Style(YELLOW)
PARAMETER = Style(ORANGE)
USER_CONSTANT = Style(CRIMSON)
VARIABLE = Style(ORANGE)

RAINBOW = Style([PINK, CRIMSON])
INVALID = Style(CLEAR_WHITE, background=CRIMSON)

REGEXP_GROUP = Style(ORANGE)
REGEXP_CHARACTER_CLASS = Style(PURPLE)
REGEXP_CONTROL = Style(PINK)

COLOR_SCHEME = {
    'name': 'Disco',

    'globals': {
        'background': BLUISH_BLACK,
        'foreground': WHITE,
        'caret': CLEAR_WHITE,
        'highlight': CLEAR_WHITE,
        'selection': DARK_BLUE,
        'line_highlight': alpha(FADED_GRAY, 0.3),
        'find_highlight': YELLOW,
        'minimap_border': CLEAR_WHITE,
        'brackets_foreground': DARK_ORANGE,

        'line_diff_width': '2',
        'line_diff_added': FADED_GRAY,
        'line_diff_modified': FADED_VIOLET,
        'line_diff_deleted': FADED_VIOLET
    },

    'rules': []
}

GLOBAL_SCOPE = None


def sec(scope=None):
    global GLOBAL_SCOPE
    GLOBAL_SCOPE = scope


def src(lang):
    sec('source.' + lang)


def txt(lang):
    sec('text.' + lang)


def rec(style, *scopes):
    global GLOBAL_SCOPE
    global COLOR_SCHEME

    if not isinstance(style, Style):
        style = Style(style)

    for scope in scopes:
        if GLOBAL_SCOPE:
            scope = ' '.join([GLOBAL_SCOPE, scope])

        COLOR_SCHEME['rules'].append(dict(style.settings, scope=scope))


def generate():
    global COLOR_SCHEME

    path = os.path.join('..', 'Disco.sublime-color-scheme')
    path = os.path.abspath(path)

    with open(path, 'w') as json_file:
        json.dump(COLOR_SCHEME, json_file, indent=2)

    print('Generated', path)


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
    'string',
    'string.quoted')
rec(FOREGROUND,
    'string.unquoted')
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
    'entity.name.class',
    'entity.name.function -meta.function-call',
    'entity.name.filename',
    'entity.name.namespace',
    'entity.name.key')
rec(FOREGROUND,
    'punctuation.separator',
    'punctuation.terminator',
    'punctuation.accessor')
rec(PARAMETER,
    'variable.parameter')
rec(VARIABLE,
    'variable.language',
    'support.constant',
    'support.variable',
    'variable.other.substitution')
rec(PUNCTUATION,
    'punctuation.separator.continuation -source.c++',
    'punctuation.definition.template-expression')
rec(INVALID,
    'invalid')
rec(TAG,
    'entity.name.tag',
    'punctuation.definition.tag')
rec(TAG_ATTRIBUTE,
    'entity.other.attribute-name')
rec(PUNCTUATION,
    'punctuation.definition.variable')

#### MARKUP ####

rec(STRING,
    'markup.raw -markup.raw.code-fence -markup.raw.block')
rec(BLUE,
    'markup.heading')
rec(ITALIC,
    'markup.italic -punctuation',
    'markup.underline.link',
    'markup.quote')
rec(BOLD,
    'markup.bold -punctuation')

#### INLINE DIFF ####

rec(BACKGROUND, 'diff.inserted')
rec(Highlight(FADED_VIOLET, 0.6, 'l(+ 10%)'), 'diff.inserted.char')
rec(GRAY + BACKGROUND, 'diff.deleted')
rec(WHITE + Highlight(FADED_GRAY, 0.6, 'l(+ 10%)'), 'diff.deleted.char')

#### PYTHON ####

src('python')
rec(KEYWORD,
    'keyword.operator.logical')
rec(META,
    'meta.annotation & (-meta.annotation.arguments -punctuation.section | support.function)')
rec(ITALIC,
    'support.function -support.function.magic -variable.annotation')
rec(STRING,
    'string keyword.operator')
rec(STRING + BOLD_ITALIC,
    'string source.sql keyword')
rec(STRING + ITALIC,
    'string source.sql storage')
rec(PUNCTUATION,
    'meta.string.interpolated punctuation.section.interpolation')
rec(PARAMETER + ITALIC,
    'variable.parameter & -meta.function.inline & (meta.annotation.arguments | meta.function-call.arguments)')
rec(REGEXP_GROUP,
    'source.regexp & (punctuation.definition.group | keyword.operator.or)')
rec(REGEXP_CHARACTER_CLASS,
    'source.regexp & (constant.character.character-class | constant.other.character-class.set)')

#### JAVASCRIPT ####

src('js')
rec(TAG + ITALIC,
    'meta.object-literal.key')
rec(STORAGE,
    'variable.type',
    'support.constant.builtin')
rec(OPERATOR,
    'storage.type.function.arrow')
rec(KEYWORD,
    'keyword.operator.js')
rec(STRING,
    'meta.template.expression',
    'string.regexp keyword.other.js')
rec(VARIABLE,
    'support.type.object.dom')
rec(FOREGROUND,
    'meta.binding.name variable.other.readwrite')
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
rec(Highlight(BLUISH_BLACK, 1, 's(25%)'),
    'text.html & (meta.tag | constant.character.entity)')
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
    'variable.parameter.javadoc')

#### JAVA LOG ####

txt('log.java')
rec(CRIMSON, 'entity.name.exception')

#### CLOJURE ####

src('clojure')
rec(TAG + ITALIC, 'constant.other.keyword')
rec(PUNCTUATION, 'keyword.operator.macro')

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
rec(KEYWORD, 'keyword.operator.new')

#### POWERSHELL ####

src('powershell')
rec(PUNCTUATION,
    'keyword.operator.other',
    'variable.other punctuation.section.braces',
    'string.quoted.double punctuation.section.group -interpolated',
    'string.quoted.double punctuation.section.braces -interpolated')
rec(META,
    'meta.attribute & (support.function | variable.parameter.attribute)')
rec(ITALIC,
    'keyword.operator.comparison',
    'keyword.operator.logical',
    'keyword.operator.unary')
rec(VARIABLE,
    'variable storage.modifier.scope')
rec(FOREGROUND,
    'support.constant variable.other')

#### SHELL ####

src('shell')
rec(PUNCTUATION,
    'meta.group.expansion punctuation.section',
    'keyword.operator.expansion',
    'keyword.operator.logical.pipe',
    'keyword.operator.assignment.redirection')
rec(FOREGROUND,
    'keyword.control.case.item',
    'variable.language.tilde',
    'variable.parameter.option')

#### C++ ####

src('c++')
rec(USER_CONSTANT,
    'entity.name.constant.preprocessor')
rec(META,
    'meta.preprocessor keyword')
rec(KEYWORD,
    'keyword.operator.word')
rec(INDEXED,
    'entity.name.struct')

#### YAML ####

src('yaml')
rec(PUNCTUATION,
    'punctuation.definition.block.sequence.item',
    'entity.other.document',
    'keyword.control.flow.block-scalar',
    'storage.modifier.chomping-indicator')
rec(TAG,
    'punctuation.definition.directive.begin',
    'constant.language.merge',
    'keyword.other.directive.yaml')
rec(META,
    'variable.other.alias',
    'punctuation.definition.alias',
    'entity.name.other.anchor',
    'punctuation.definition.anchor')

#### CSS ####

src('css')
rec(PRIMITIVE,
    'constant.numeric keyword.other',
    'constant.other.color')
rec(CRIMSON,
    'support.type.vendor-prefix')
rec(ITALIC,
    'support.type.property-name')

#### XML ####

txt('xml')
rec(PUNCTUATION,
    'string.unquoted.cdata punctuation')
rec(VARIABLE,
    'meta.tag.sgml.doctype variable')
rec(ITALIC,
    'meta.tag.sgml -comment')
rec(TAG + BOLD_ITALIC,
    'meta.tag.sgml.doctype keyword')

#### HTML ####

txt('html')
rec(TAG,
    'meta.tag.sgml.doctype')

#### MARKDOWN ####

txt('html.markdown')
rec(PUNCTUATION,
    'punctuation.definition.list_item',
    'punctuation.definition.blockquote',
    'meta.link punctuation',
    'markup.list.numbered.bullet')
rec(FADED_GRAY,
    'punctuation.definition.bold',
    'punctuation.definition.italic',
    'punctuation.definition.raw.code-fence',
    'meta.code-fence.definition constant.other.language-name')

#### DIFF ####

src('diff')
rec(SECTION, 'meta.diff.range')
rec(BOLD_ITALIC, 'entity.name.section')
rec(BLUE, 'meta.diff.header')
rec(GREEN, 'markup.inserted')
rec(CRIMSON, 'markup.deleted')

#### GIT ####

txt('git')
rec(Style([PINK, PURPLE]) + ITALIC,
    'constant.numeric.hash')

txt('git.config')
rec(SECTION,
    'meta.brackets',
    'entity.name.section')
rec(INDEXED,
    'variable.other.readwrite')

txt('git.merge-conflict')
rec(Highlight(FADED_GRAY, 0.5),
    'meta.branch',
    'meta.separator')
rec(CLEAR_WHITE + BOLD,
    'variable.other.branch')

txt('git.ignore')
rec(KEYWORD, 'keyword.operator')

#### INI ####

src('ini')
rec(SECTION, 'meta.section')

generate()
