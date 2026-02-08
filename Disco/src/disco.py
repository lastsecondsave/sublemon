# pylint: disable=global-statement,line-too-long

import json
import re
from itertools import chain
from pathlib import Path


class Style:
    def __init__(self, foreground=None, **settings):
        self.settings = settings
        if foreground:
            self.settings["foreground"] = foreground

    def __add__(self, other):
        settings = self.settings.copy()

        for key, val in other.settings.items():
            if key == "font_style" and "font_style" in settings:
                val += " " + settings["font_style"]

            settings[key] = val

        return Style(**settings)

    def __radd__(self, foreground):
        return Style(foreground, **self.settings)


class Highlight(Style):
    def __init__(self, background, foreground_adjust=None):
        settings = {"background": background}
        if foreground_adjust:
            settings["foreground_adjust"] = foreground_adjust
        super().__init__(**settings)


def color(value, mod):
    return f"color({value} {mod})"


WHITE = "#AEB7BF"
GRAY = "#9090A0"
PURPLE = "#E572D2"
PINK = "#EF51AA"
VIOLET = "#8888BC"
BLUE = "#6699FF"
GREEN = "#C5CC4B"
YELLOW = "#EDC61A"
ORANGE = "#FFAD3A"
DARK_ORANGE = "#FF8147"
CRIMSON = "#E5476C"

CLEAR_WHITE = "#FFFFFF"
BRIGHTER_WHITE = "#C6DFD7"
LIGHT_YELLOW = "#EFE1A1"

FADED_GRAY = "#51515D"
FADED_VIOLET = "#5E5E8E"

BLUISH_BLACK = "#1E262E"
DARK_BLUE = "#384868"

FOREGROUND = Style(WHITE)

ITALIC = Style(font_style="italic")
BOLD = Style(font_style="bold")
UNDERLINE = Style(font_style="underline")

KEYWORD = Style(PURPLE)
STORAGE = Style(PINK)
SUPPORT = Style(BRIGHTER_WHITE)
INDEXED = Style(BLUE)
OPERATOR = Style(VIOLET)
GENERIC_PUNCTUATION = Style(VIOLET)
PUNCTUATION = Style(DARK_ORANGE)
ACCESSOR = Style(VIOLET)
COMMENT = Style(GRAY)
COMMENT_DIM = Style(FADED_VIOLET)
COMMENT_LIGHT = Style(VIOLET)
COMMENT_HIGHLIGHT = Style(WHITE)
PRIMITIVE = Style(DARK_ORANGE)
STRING = Style(GREEN)
TAG = Style(BLUE)
TAG_ATTRIBUTE = Style(YELLOW)
PARAMETER = Style(ORANGE)
VARIABLE = Style(ORANGE)
META = Style(YELLOW)
SPECIAL1 = Style(CRIMSON)
SPECIAL2 = Style(LIGHT_YELLOW)

INVALID = CLEAR_WHITE + Highlight("#E62020", "l(- 5%)")

REGEXP_GROUP = Style(ORANGE)
REGEXP_CHARACTER_CLASS = Style(PURPLE)
REGEXP_CONTROL = Style(PINK)

COLOR_SCHEME = {
    "name": "Disco",

    "globals": {
        "background": BLUISH_BLACK,
        "foreground": WHITE,
        "caret": CLEAR_WHITE,
        "line_highlight": color(FADED_GRAY, "a(30%) l(+ 3%) s(+ 3%)"),
        "fold_marker": LIGHT_YELLOW,
        "brackets_foreground": VIOLET,
        "tags_foreground": VIOLET,

        "selection": DARK_BLUE,
        "inactive_selection": color(DARK_BLUE, "a(80%)"),
        "selection_corner_radius": "2",
        "selection_border_width": "0",
        "invisibles": color(DARK_BLUE, "l(+ 10%)"),

        "highlight": color(CLEAR_WHITE, "l(- 25%)"),
        "find_highlight": LIGHT_YELLOW,
        "find_highlight_foreground": BLUISH_BLACK,
        "scroll_highlight": WHITE,
        "scroll_selected_highlight": YELLOW,

        "guide": color(FADED_GRAY, "a(20%)"),
        "active_guide": color(FADED_GRAY, "a(40%)"),
        "stack_guide": color(FADED_GRAY, "a(20%)"),
        "rulers": color(FADED_GRAY, "a(40%)"),

        "line_diff_width": "2",
        "line_diff_added": FADED_GRAY,
        "line_diff_modified": FADED_VIOLET,
        "line_diff_deleted": FADED_VIOLET
    },

    "rules": []
}

ROOT_SCOPES = None


def sec(*scopes):
    global ROOT_SCOPES
    ROOT_SCOPES = scopes


def src(*scopes):
    sec(*(f"source.{s}" for s in scopes))


def txt(*scopes):
    sec(*(f"text.{s}" for s in scopes))


def regroup(scopes):
    if len(scopes) <= 1:
        return scopes

    simple_scopes = " | ".join(scope for scope in scopes if " " not in scope)
    scopes = [scope for scope in scopes if " " in scope]

    if simple_scopes:
        scopes.append(simple_scopes)

    return scopes


def expand_glob(match):
    prefix = match.group(1)
    chunks = match.group(2).split("|")
    suffix = match.group(3)

    return " | ".join(f"{prefix}{chunk}{suffix}" for chunk in chunks)


def expand(scope):
    scope = re.sub(r"([\w.-]*)\{([\w.|-]+)\}([\w.-]*)", expand_glob, scope)

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
        COLOR_SCHEME["rules"].append({"scope": scope, **style.settings})


def generate():
    path = Path(__file__).resolve().parent.parent / "Disco.sublime-color-scheme"

    with path.open(mode="w") as json_file:
        json.dump(COLOR_SCHEME, json_file, indent=2)

    print("Generated", path)


rec(COMMENT,
    'comment',
    'punctuation.definition.comment',
    'comment.line.shebang constant.language.shebang')
rec(PRIMITIVE,
    'constant.{character|language|numeric}',
    'storage.type.numeric',
    'punctuation.separator.decimal')
rec(STRING,
    'string -string.unquoted',
    'string.quoted',
    'punctuation.definition.string')
rec(STORAGE,
    'storage',
    'entity.other.inherited-class')
rec(KEYWORD,
    'keyword',
    'keyword.operator.{alphanumeric|word}',
    'storage.modifier')
rec(OPERATOR,
    'keyword.operator -string')
rec(INDEXED,
    'entity.name -comment -meta.function-call',
    'markup.heading')
rec(PARAMETER,
    'variable.parameter')
rec(VARIABLE,
    'variable.{language|other.substitution}',
    'support.{constant|variable}')
rec(GENERIC_PUNCTUATION,
    '(punctuation.{section|separator|terminator|definition.generic}) -string')
rec(PUNCTUATION,
    'punctuation.separator.continuation',
    'punctuation.definition.{template-expression|variable}',
    'punctuation.section.interpolation')
rec(ACCESSOR,
    'punctuation.accessor')
rec(INVALID,
    'invalid -text.html.markdown')
rec(TAG,
    'entity.name.tag -comment',
    'punctuation.definition.tag -comment')
rec(TAG_ATTRIBUTE,
    'entity.other.attribute-name -comment')

rec(ITALIC, 'style.italic')
rec(BOLD, 'style.bold')
rec(UNDERLINE, 'style.underline')
rec(CRIMSON, 'style.crimson')
rec(ORANGE, 'style.orange')
rec(DARK_ORANGE, 'style.darkorange')
rec(BLUE, 'style.blue')
rec(GREEN, 'style.green')
rec(GRAY, 'style.gray')

rec(Highlight("hsla(170, 45%, 40%, 0.15)", 'l(+ 10%)'), 'diff.inserted')
rec(Highlight("hsla(170, 65%, 40%, 0.30)", 'l(+ 10%)'), 'diff.inserted.char')
rec(Highlight("hsla(357, 45%, 60%, 0.15)", 'l(+ 10%)'), 'diff.deleted')
rec(Highlight("hsla(357, 65%, 60%, 0.30)", 'l(+ 10%)'), 'diff.deleted.char')

src('python')
rec(KEYWORD,
    'keyword.operator.{logical|iteration}')
rec(META,
    '{punctuation.definition|variable}.annotation')
rec(ITALIC,
    'meta.function-call.arguments variable.parameter -meta.function.inline')
rec(PARAMETER,
    'meta.interpolation constant.other.format-spec')
rec(STORAGE,
    'support.type -comment.line.number-sign')
rec(COMMENT_LIGHT,
    'comment.line.number-sign & (keyword | constant.language | support.type)')
rec(SUPPORT,
    'keyword.other.print',
    'support.function.builtin')

src('regexp.python')
rec(REGEXP_GROUP,
    'punctuation.definition.group | keyword.operator.or')
rec(REGEXP_CHARACTER_CLASS,
    'constant.character.character-class | constant.other.character-class.set')
rec(REGEXP_CONTROL,
    'punctuation.definition.character-class')

src('js', 'ts', 'tsx')
rec(TAG + ITALIC,
    'meta.mapping.key -variable -support')
rec(STORAGE,
    'variable.type',
    'support.{constant|class}.builtin')
rec(OPERATOR,
    'keyword.declaration.function.arrow',
    'meta.type keyword.declaration.function',
    'storage.modifier.array')
rec(KEYWORD,
    'keyword.operator.js')
rec(STRING,
    'meta.template.expression',
    'string.regexp keyword.other.js')
rec(VARIABLE,
    'support.type.object.dom')

sec('string.regexp.js')
rec(REGEXP_GROUP,
    'punctuation.definition.group',
    'keyword.operator.or')
rec(REGEXP_CHARACTER_CLASS,
    'constant.other.character-class',
    '{punctuation.definition|support.constant}.unicode-property')
rec(REGEXP_CONTROL,
    'keyword.{control|operator}',
    'punctuation.definition.character-class')

src('regexp')
rec(TAG,
    'meta.group keyword.other.named-capture-group punctuation.definition.capture-group-name')
rec(REGEXP_GROUP,
    'punctuation.section.group',
    'constant.other.assertion',
    'keyword.control.group',
    'keyword.operator.alternation',
    'keyword.other.{conditional|named-capture-group}')
rec(REGEXP_CHARACTER_CLASS,
    'meta.set',
    'meta.set punctuation.separator.sequence',
    'keyword.control.character-class')
rec(REGEXP_CONTROL,
    'keyword.{control|operator}')
rec(SPECIAL1,
    'storage.modifier.mode',
    'punctuation.definition.modifier')

src('java')
rec(META,
    'punctuation.definition.annotation',
    'variable.annotation')
rec(COMMENT_LIGHT,
    'meta.tag.block entity.name.tag.documentation')
rec(COMMENT_HIGHLIGHT + ITALIC,
    'comment.block.documentation variable.parameter')
rec(COMMENT_DIM,
    'meta.tag.inline & (entity.name | punctuation.definition)',
    'comment.block.documentation meta.tag.html',
    'comment.block.documentation meta.tag.html punctuation.separator')
rec(COMMENT_LIGHT,
    'comment.block.documentation & (string.quoted | punctuation.definition.string)')
rec(ITALIC,
    'comment.block.documentation markup.underline.link',
    'meta.annotation.parameters variable.parameter')
rec(STORAGE,
    'meta.import entity.name.class',
    'support.class',
    'constant.other.wildcard.asterisk')
rec(OPERATOR,
    'keyword.declaration.function.arrow',
    'storage.modifier.array')
rec(FOREGROUND,
    'entity.name.{constant|namespace}',
    'meta.import entity.name.function')

src('clojure')
rec(TAG + ITALIC, 'constant.other.keyword')
rec(PUNCTUATION, 'keyword.operator.macro')

src('groovy')
rec(META, 'storage.type.annotation')

src('cs')
rec(KEYWORD,
    'keyword.operator.{new|reflection}')
rec(SPECIAL1,
    'entity.name.constant',
    'constant.other.flag',
    'storage.type.nullable')
rec(META,
    'meta.annotation variable.annotation')
rec(OPERATOR,
    'punctuation.definition.annotation',
    'keyword.declaration.function.arrow')
rec(FOREGROUND,
    'storage.type.function.lambda')

src('powershell')
rec(ITALIC,
    "variable.parameter.option",
    "keyword.operator.{string|comparison|logical}")
rec(PUNCTUATION,
    "keyword.operator.pipe")
rec(KEYWORD,
    "keyword.operator.call")
rec(STORAGE,
    "support.type")
rec(META,
    'meta.attribute support.function.attribute')

src('shell')
rec(PUNCTUATION,
    'meta.group.expansion & (punctuation.section | keyword.operator.substitution | variable.parameter.switch)',
    'keyword.operator.expansion',
    'keyword.operator.assignment.{pipe|redirection|herestring}',
    'meta.interpolation.parameter keyword.operator.assignment')
rec(STORAGE,
    'keyword.declaration.{alias|variable}')
rec(META,
    'entity.name.tag.heredoc',
    'punctuation.definition.tag')
rec(VARIABLE,
    'meta.conditional.case.clause.commands meta.variable variable.other.readwrite',
    'meta.variable variable.other.readwrite - (meta.{arithmetic|conditional|interpolation})',
    'meta.declaration.variable variable.other.readwrite -meta.interpolation',
    'meta.assignment.l-value variable.other.readwrite')
rec(KEYWORD,
    'keyword.operator.iteration.in')
rec(SUPPORT,
    'support.function.shell')
rec(STRING,
    'meta.function-call punctuation.definition.quoted')
rec(FOREGROUND,
    'variable.language.tilde',
    'variable.parameter.option',
    'keyword.control.conditional.patterns',
    'punctuation.separator.path',
    'constant.language.null')
rec(ITALIC,
    'meta.statement.conditional.case meta.clause.patterns meta.string.glob')

src('makefile')
rec(PUNCTUATION,
    'meta.interpolation keyword.other.block')
rec(VARIABLE,
    'variable.other')
rec(FOREGROUND,
    'variable.parameter',
    'meta.function-call constant.language')

src('cmake')
rec(VARIABLE,
    'variable.other.readwrite.assignment')
rec(PUNCTUATION,
    'meta.text-substitution punctuation.section.braces',
    'punctuation.section.block.{begin|end}',
    'punctuation.separator.generator-expression')
rec(KEYWORD,
    'keyword.operator.logical',
    'support.function.{endfunction|endmacro|function|macro}')
rec(INDEXED,
    'entity.name.function')
rec(SPECIAL2,
    'support.function.{add_library|add_executable|add_custom_target}')
rec(SUPPORT,
    'support.function')

src('dockerfile')
rec(VARIABLE,
    'meta.declaration.variable variable.other.readwrite -meta.interpolation')
rec(META,
    '{entity.name.tag|keyword.operator}.heredoc')

src('c++', 'c')
rec(SPECIAL1,
    'meta.preprocessor keyword.control.import',
    'meta.preprocessor keyword.control -meta.preprocessor.macro')
rec(SPECIAL1 + ITALIC,
    'entity.name.label')
rec(STORAGE,
    'support.type.{stdint|stddef|time}')
rec(KEYWORD,
    'keyword.operator.word')
rec(VARIABLE,
    'entity.name.constant')

src('objc++', 'objc')
rec(PARAMETER + ITALIC,
    'meta.function-call support.function.any-method -punctuation')
rec(SPECIAL1,
    'keyword.control.import')
rec(FOREGROUND,
    'support.constant.cocoa',
    'punctuation.separator.arguments')

src('go')
rec(KEYWORD,
    'support.function.builtin')
rec(STORAGE,
    'support.type.builtin',
    'meta.function.declaration variable.other.type')
rec(META,
    '{punctuation.definition|variable}.annotation')
rec(FOREGROUND,
    'variable.parameter.type')

src('rust')
rec(STORAGE,
    'meta.macro support.function -meta.block.macro-body',
    'meta.annotation meta.group',
    'support.type')
rec(KEYWORD,
    'variable.annotation')
rec(SPECIAL1,
    'storage.modifier.lifetime')
rec(GENERIC_PUNCTUATION,
    'punctuation.definition.annotation')

src('yaml')
rec(PUNCTUATION,
    'punctuation.definition.block.sequence.item',
    'entity.other.document',
    'keyword.control.flow.block-scalar',
    'storage.modifier.chomping-indicator')
rec(GENERIC_PUNCTUATION,
    'punctuation.definition.{sequence|mapping}')
rec(TAG,
    'punctuation.definition.directive.begin',
    'constant.language.merge',
    'keyword.other.directive.yaml',
    'meta.mapping.key meta.string string')
rec(META,
    'variable.other.alias',
    'entity.name.other.anchor',
    'punctuation.definition.{alias|anchor}')

src('toml')
rec(META,
    'entity.name.section',
    'punctuation.section.brackets',
    'meta.section punctuation.accessor')
rec(TAG,
    'meta.mapping.key meta.string string.unquoted')
rec(VARIABLE,
    'constant.other.{datetime|date|time}',
    'constant.other punctuation.separator')
rec(PUNCTUATION,
    'constant.other.datetime & (punctuation.separator.datetime | keyword.operator | storage.modifier)')

src('ini')
rec(META,
    '{entity.name|punctuation.definition}.section')

src('proto')
rec(STORAGE,
    'support.type')
rec(GENERIC_PUNCTUATION,
    'punctuation.definition.block')

src('css')
rec(STRING,
    'meta.selector string.unquoted')
rec(PRIMITIVE,
    'constant.numeric keyword.other',
    'constant.other.color')
rec(SPECIAL1,
    'support.type.vendor-prefix')
rec(STORAGE,
    'meta.property-name')
rec(VARIABLE,
    'entity.other.pseudo-class -punctuation')

txt('xml', 'html')
rec(PUNCTUATION,
    'meta.tag.sgml.cdata punctuation.definition.tag',
    'keyword.declaration.cdata')
rec(VARIABLE,
    'meta.tag.sgml.doctype variable')
rec(TAG,
    'meta.tag.sgml.doctype keyword')

txt('html.markdown')
rec(PUNCTUATION,
    'punctuation.definition.{blockquote|image|link|list_item}',
    'markup.list.numbered.bullet')
rec(GENERIC_PUNCTUATION,
    'punctuation.definition.{attributes|bold|constant|italic|metadata}',
    'meta.link punctuation.definition.{link|reference}')
rec(COMMENT,
    'meta.code-fence.definition')
rec(STRING,
    'markup.raw.inline')
rec(VARIABLE,
    '({meta.image.inline|meta.link.inline|meta.link.reference}.description) -markup.underline -punctuation',
    'meta.link.reference.def entity.name.reference.link',
    'meta.link.reference constant.other.reference.link')
rec(ITALIC,
    'markup.italic -punctuation',
    'markup.heading.3 entity.name')
rec(BOLD,
    'markup.bold -punctuation',
    'markup.heading.1 entity.name')
rec(BOLD + ITALIC,
    'markup.heading.2 entity.name')
rec(UNDERLINE,
    'markup.underline.link')
rec(FOREGROUND,
    'entity.name.reference.link',
    'markup.underline.link punctuation.separator.path')

src('diff')
rec(META, 'meta.diff.range')
rec(META + UNDERLINE, 'entity.name.section')
rec(BLUE, 'meta.diff.header')
rec(GREEN,
    'markup.inserted',
    'punctuation.definition.to-file')
rec(CRIMSON,
    'markup.deleted',
    'punctuation.definition.from-file')

txt('output')
rec(Style([PINK, FADED_VIOLET]) + ITALIC, 'storage.category.hash')
rec(COMMENT, 'punctuation.formatting')
rec(DARK_ORANGE, 'punctuation.definition.marker')
rec(COMMENT + ITALIC, 'comment.category')
rec(COMMENT_LIGHT, 'comment.highlight')
rec(COMMENT_LIGHT + ITALIC, 'comment.highlight.italic')
rec(COMMENT_DIM, 'comment.highlight.dim')
rec(META, 'entity.name.section')
rec(SPECIAL1, 'support.type.exception')
rec(CRIMSON, 'constant.other.indicator.error')
rec(ORANGE, 'constant.other.indicator.warning')
rec(GREEN, 'constant.other.indicator.success')
rec(PURPLE, 'constant.other.indicator.note')
rec(COMMENT, 'constant.other.indicator.info')
rec(FOREGROUND, 'constant.numeric.date')

generate()
