# pylint: disable=bad-whitespace,global-statement,line-too-long

import json
from itertools import chain
from pathlib import Path


class Style:
    def __init__(self, foreground=None, **settings):
        self.settings = settings
        if foreground:
            self.settings['foreground'] = foreground

    def __add__(self, other):
        settings = self.settings.copy()

        for key, val in other.settings.items():
            if key == "font_style" and "font_style" in settings:
                val += " " + settings["font_style"]

            settings[key] = val

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
    return f'color({color} alpha({value}))'


WHITE = "#C4C4C4"
GRAY = "#9090A0"
PURPLE = "#E572D2"
PINK = "#EF51AA"
BLUE = "#6699FF"
GREEN = "#C5CC4B"
YELLOW = "#EDC61A"
ORANGE = "#FFAD3A"
DARK_ORANGE = "#FF8147"
CRIMSON = "#E5476C"

CLEAR_WHITE = "#FFFFFF"
FADED_GRAY = "#51515D"
FADED_VIOLET = "#5E5E8E"

BLUISH_BLACK = "#202830"
DARK_BLUE = "#384868"

FOREGROUND = Style(WHITE)

ITALIC = Style(font_style='italic')
BOLD = Style(font_style='bold')
UNDERLINE = Style(font_style='underline')

KEYWORD = Style(PURPLE)
STORAGE = Style(PINK)
INDEXED = Style(BLUE)
OPERATOR = Style(WHITE)
PUNCTUATION = Style(DARK_ORANGE)
COMMENT = Style(GRAY)
COMMENT_HIGHLIGHT = Style(WHITE)
PRIMITIVE = Style(DARK_ORANGE)
STRING = Style(GREEN)
TAG = Style(BLUE)
TAG_ATTRIBUTE = Style(YELLOW)
PARAMETER = Style(ORANGE)
VARIABLE = Style(ORANGE)
META = Style(YELLOW)
SPECIAL = Style(CRIMSON)

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
        'selection_corner_radius': '2',

        'line_diff_width': '2',
        'line_diff_added': FADED_GRAY,
        'line_diff_modified': FADED_VIOLET,
        'line_diff_deleted': FADED_VIOLET
    },

    'rules': []
}

ROOT_SCOPES = None


def src(*scopes):
    global ROOT_SCOPES
    ROOT_SCOPES = list(f"source.{s}" for s in scopes)


def txt(*scopes):
    global ROOT_SCOPES
    ROOT_SCOPES = list(f"text.{s}" for s in scopes)


def regroup(scopes):
    if len(scopes) <= 1:
        return scopes

    simple_scopes = " | ".join(scope for scope in scopes if " " not in scope)
    scopes = [scope for scope in scopes if " " in scope]

    if simple_scopes:
        scopes.append(simple_scopes)

    return scopes


def expand(scope):
    if not ROOT_SCOPES:
        yield scope
        return

    if "|" in scope and "&" not in scope:
        scope = f"& ({scope})"
    elif "&" in scope:
        scope = f"& {scope}"

    for root_scope in ROOT_SCOPES:
        yield f"{root_scope} {scope}"


def rec(style, *scopes):
    if not isinstance(style, Style):
        style = Style(style)

    for scope in chain.from_iterable(expand(s) for s in regroup(scopes)):
        COLOR_SCHEME['rules'].append({'scope': scope, **style.settings})


def generate():
    path = Path(__file__).resolve().parent.parent / "Disco.sublime-color-scheme"

    with path.open(mode='w') as json_file:
        json.dump(COLOR_SCHEME, json_file, indent=2)

    print('Generated', path)


rec(COMMENT,
    'comment')
rec(PRIMITIVE,
    'constant.numeric',
    'constant.character',
    'constant.language',
    'storage.type.numeric',
    'punctuation.separator.decimal')
rec(STRING,
    'string -string.unquoted',
    'string.quoted')
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
    'keyword.operator -string.quoted',
    'punctuation.separator')
rec(INDEXED,
    'entity.name -comment -meta.function-call',
    'markup.heading')
rec(PARAMETER,
    'variable.parameter')
rec(VARIABLE,
    'variable.language',
    'support.constant',
    'support.variable',
    'variable.other.substitution')
rec(PUNCTUATION,
    'punctuation.separator.continuation',
    'punctuation.definition.template-expression',
    'punctuation.definition.variable',
    'punctuation.section.interpolation')
rec(INVALID,
    'invalid')
rec(TAG,
    'entity.name.tag -comment',
    'punctuation.definition.tag -comment')
rec(TAG_ATTRIBUTE,
    'entity.other.attribute-name -comment')

rec(ITALIC, 'style.italic')
rec(BOLD, 'style.bold')
rec(UNDERLINE, 'style.underline')

rec(Highlight(GREEN, 0.1), 'diff.inserted')
rec(Highlight(GREEN, 0.3, 'l(+ 10%)'), 'diff.inserted.char')
rec(Highlight(CRIMSON, 0.2), 'diff.deleted')
rec(Highlight(CRIMSON, 0.4, 'l(+ 10%)'), 'diff.deleted.char')

src('python')
rec(KEYWORD,
    'keyword.operator.logical')
rec(META,
    'meta.annotation & (-meta.annotation.arguments -punctuation.section | support.function)')
rec(STRING,
    'source.sql & (keyword | storage | storage.modifier | variable.language | entity.name | constant.numeric)')
rec(REGEXP_GROUP,
    'source.regexp & (punctuation.definition.group | keyword.operator.or)')
rec(REGEXP_CHARACTER_CLASS,
    'source.regexp & (constant.character.character-class | constant.other.character-class.set)')
rec(ITALIC,
    '(meta.function-call.arguments variable.parameter) & -meta.function.inline')

src('js')
rec(TAG + ITALIC,
    'meta.mapping.key -variable')
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
rec(REGEXP_GROUP,
    'string.regexp punctuation.definition.group',
    'keyword.operator.or.regexp')
rec(REGEXP_CHARACTER_CLASS,
    'string.regexp constant.other.character-class')
rec(REGEXP_CONTROL,
    'string.regexp & (keyword.control | keyword.operator)',
    'constant.other.character-class.set.regexp constant.other.character-class.escape')

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

src('java')
rec(META,
    'punctuation.definition.annotation',
    'variable.annotation')
rec(COMMENT_HIGHLIGHT,
    'meta.block-tag keyword')
rec(COMMENT_HIGHLIGHT + ITALIC,
    'meta.block-tag variable.parameter')
rec(SPECIAL,
    'entity.name.constant',
    'constant.other',
    'meta.class.body.anonymous.java punctuation.section.braces')
rec(STORAGE,
    'keyword.operator.wildcard',
    'keyword.other.package')
rec(FADED_GRAY,
    'meta.inline-tag & (keyword.other | punctuation.section)')
rec(FOREGROUND,
    'storage.modifier.array',
    'storage.type.function.anonymous',
    'punctuation.accessor.dot')

txt('log.java')
rec(SPECIAL, 'entity.name.exception')

src('clojure')
rec(TAG + ITALIC, 'constant.other.keyword')
rec(PUNCTUATION, 'keyword.operator.macro')

src('groovy')
rec(META, 'storage.type.annotation')

txt('log')
rec(CRIMSON, 'meta.indicator.error')
rec(ORANGE, 'meta.indicator.warning')
rec(GREEN, 'meta.indicator.success')
rec(YELLOW, 'meta.message', 'meta.title')

src('cs')
rec(KEYWORD,
    'keyword.operator.new | keyword.operator.reflection')
rec(SPECIAL,
    'entity.name.constant',
    'constant.other.flag',
    'storage.type.nullable')
rec(FOREGROUND,
    'storage.type.function.lambda')
rec(META,
    'meta.annotation variable.annotation')

src('powershell')
rec(PUNCTUATION,
    'keyword.operator.other',
    'variable.other punctuation.section.braces',
    'string.quoted.double punctuation.section.group -interpolated',
    'string.quoted.double punctuation.section.braces -interpolated')
rec(META,
    'meta.attribute support.function.attribute')
rec(ITALIC,
    'keyword.operator.comparison | keyword.operator.logical | keyword.operator.unary')
rec(VARIABLE,
    'variable storage.modifier.scope')
rec(FOREGROUND,
    'support.constant variable.other')

src('shell')
rec(PUNCTUATION,
    'meta.group.expansion & (punctuation.section | keyword.operator.substitution | variable.parameter.switch)',
    'keyword.operator.expansion',
    'keyword.operator.logical.pipe',
    'keyword.operator.logical.job',
    'keyword.operator.assignment.redirection',
    'keyword.operator.end-of-options')
rec(STORAGE,
    'support.function.alias | support.function.export | support.function.source')
rec(VARIABLE,
    'meta.variable variable.other.readwrite')
rec(KEYWORD,
    'support.function.trap')
rec(COMMENT,
    'constant.language.shebang')
rec(FOREGROUND,
    'keyword.control.case.item',
    'keyword.control.conditional.patterns.end',
    'variable.language.tilde',
    'variable.parameter.option')

src('makefile')
rec(PUNCTUATION,
    'keyword.other.single-character-variable',
    'variable.parameter keyword.other.block')
rec(VARIABLE,
    'variable.other')
rec(FOREGROUND,
    'variable.parameter')

src('cmake')
rec(VARIABLE,
    'variable.other.readwrite.assignment')
rec(PUNCTUATION,
    'meta.text-substitution punctuation.section.braces')
rec(KEYWORD,
    'keyword.operator.logical',
    'support.function.function',
    'support.function.endfunction',
    'support.function.macro',
    'support.function.endmacro')
rec(INDEXED,
    'entity.name.function')

src('c++')
rec(SPECIAL,
    'meta.preprocessor keyword.control.import')
rec(KEYWORD,
    'keyword.operator.word')
rec(VARIABLE,
    'entity.name.constant.preprocessor')

src('rust')
rec(STORAGE,
    'meta.macro support.function -meta.block.macro-body')
rec(META,
    'variable.annotation | punctuation.definition.annotation')
rec(SPECIAL,
    'storage.modifier.lifetime')

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

src('toml')
rec(META,
    'entity.name.table | punctuation.definition.table')

src('ini')
rec(META,
    'entity.name.section | punctuation.definition.section')

src('css')
rec(STRING,
    'meta.selector string.unquoted')
rec(PRIMITIVE,
    'constant.numeric keyword.other',
    'constant.other.color')
rec(SPECIAL,
    'support.type.vendor-prefix')
rec(ITALIC,
    'meta.property-name')
rec(VARIABLE,
    'entity.other.pseudo-class -punctuation')

txt('xml')
rec(PUNCTUATION,
    'meta.tag.sgml.cdata punctuation.definition.tag',
    'keyword.declaration.cdata')
rec(VARIABLE,
    'meta.tag.sgml.doctype variable')
rec(TAG + BOLD + ITALIC,
    'meta.tag.sgml.doctype keyword')

txt('html')
rec(TAG,
    'meta.tag.sgml.doctype')

txt('html.markdown')
rec(PUNCTUATION,
    'punctuation.definition.list_item',
    'punctuation.definition.blockquote',
    'meta.link punctuation',
    'markup.list.numbered.bullet')
rec(GRAY,
    'punctuation.definition.bold',
    'punctuation.definition.italic',
    'punctuation.definition.raw.code-fence',
    'meta.code-fence.definition constant.other.language-name')
rec(STRING,
    'markup.raw.inline')
rec(ITALIC,
    'markup.italic -punctuation')
rec(BOLD,
    'markup.bold -punctuation')
rec(UNDERLINE,
    'markup.underline.link')

src('diff')
rec(META, 'meta.diff.range')
rec(META + UNDERLINE, 'entity.name.section')
rec(BLUE, 'meta.diff.header')
rec(GREEN, 'markup.inserted')
rec(CRIMSON, 'markup.deleted')

txt('git')
rec(Style([PINK, FADED_VIOLET]) + ITALIC,
    'constant.numeric.hash')
rec(Highlight(FADED_GRAY, 0.5),
    'meta.marker.git.merge-conflict')
rec(CLEAR_WHITE + BOLD,
    'variable.other.revision.git.merge-conflict')

generate()
