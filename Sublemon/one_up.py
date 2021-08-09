import re
from enum import Enum, auto, unique

from sublime import Region
from sublime_plugin import TextCommand

HEX_NUMBER_PATTERN = re.compile(r"0[xX][0-9A-Fa-f]+")


@unique
class Token(Enum):
    NUMBER = auto()
    HEX_NUMBER = auto()
    BOOLEAN = auto()
    ON_OFF = auto()
    YES_NO = auto()


PAIRS = {
    Token.BOOLEAN: ("true", "false"),
    Token.ON_OFF: ("on", "off"),
    Token.YES_NO: ("yes", "no"),
}


class OneUpCommand(TextCommand):
    def run(self, edit, negative=False):  # pylint: disable=arguments-differ
        adjusted_regions = []

        for region in self.view.sel():
            if not region.empty():
                category = classify(self.view.substr(region))
            else:
                region, category = self.expand_region(region.end())

            if not category:
                continue

            token = self.view.substr(region)
            replacement = toggle(token, category, negative)
            self.view.replace(edit, region, replacement)

            begin = region.begin()
            adjusted_regions.append(Region(begin, begin + len(replacement)))

        self.view.sel().add_all(adjusted_regions)

    def expand_region(self, pos):
        region = self.view.word(pos)

        if category := classify(self.view.substr(region)):
            if category is Token.NUMBER and self.view.substr(region.a - 1) == "-":
                region.a -= 1

            return (region, category)

        char_to_the_right = self.view.substr(pos)

        if char_to_the_right == "-":
            region = self.view.word(pos + 1)
            region.a -= 1

            if category := classify(self.view.substr(region)):
                return (region, category)

        elif char_to_the_right.isnumeric():
            return (self.cover_number(pos), Token.NUMBER)

        if self.view.substr(pos - 1).isnumeric():
            return (self.cover_number(pos - 1), Token.NUMBER)

        return (None, None)

    def cover_number(self, pos):
        left = pos
        right = pos + 1

        while self.view.substr(left - 1).isnumeric():
            left -= 1

        while self.view.substr(right).isnumeric():
            right += 1

        return Region(left, right)


def classify(token):
    if not token:
        return None

    if (token[0] == "-" and token[1:].isnumeric()) or token.isnumeric():
        return Token.NUMBER

    if HEX_NUMBER_PATTERN.match(token):
        return Token.HEX_NUMBER

    for category in (Token.BOOLEAN, Token.ON_OFF, Token.YES_NO):
        if token.lower() in PAIRS[category]:
            return category

    return None


def toggle(token, category, negative):
    delta = 1 if not negative else -1

    if category is Token.NUMBER:
        return toggle_number(token, delta)

    if category is Token.HEX_NUMBER:
        return toggle_hex_number(token, delta)

    return toggle_pair(token, *PAIRS[category])


def toggle_pair(token, first, second):
    replacement = first if token.lower() == second else second
    if token.isupper():
        replacement = replacement.upper()
    elif token[0].isupper():
        replacement = replacement.title()

    return replacement


def toggle_number(token, delta):
    number = int(token) + delta

    if len(token) > 1 and token[0] == "0":
        if number == -1:
            return "9" * len(token)
        return str(number).zfill(len(token))

    return str(number)


def toggle_hex_number(token, delta):
    prefix = token[:2]
    token = token[2:]
    number = int(token, 16) + delta

    if number == -1:
        replacement = "f" * len(token)
    else:
        template = "{{:0{}x}}".format(len(token))
        replacement = template.format(number)

    if token.isupper():
        replacement = replacement.upper()

    return prefix + replacement
