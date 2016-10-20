# SYNTAX TEST "Packages/Sublemon/etc/regexp.sublime-syntax"

  \w \W \s \S \d \D \h \H \v \V \X \t
# ^^ constant.language.character-class.regexp
#    ^^ constant.language.character-class.regexp
#       ^^ constant.language.character-class.regexp
#          ^^ constant.language.character-class.regexp
#             ^^ constant.language.character-class.regexp
#                ^^ constant.language.character-class.regexp
#                   ^^ constant.language.character-class.regexp
#                      ^^ constant.language.character-class.regexp
#                         ^^ constant.language.character-class.regexp
#                            ^^ constant.language.character-class.regexp
#                               ^^ constant.language.character-class.regexp
#                                  ^^ constant.language.character-class.regexp

  \x61 \x{4312}
# ^^^^ constant.character.hex.regexp
#      ^^^^^^^^ constant.character.hex.regexp

  \Q .^abc(\E
# ^^ keyword.control.anchor.regexp
#   ^^^^^^^ source.regexp
#          ^^ keyword.control.anchor.regexp
