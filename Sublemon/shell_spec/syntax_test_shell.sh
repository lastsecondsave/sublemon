# SYNTAX TEST "Packages/Sublemon/shell_spec/shell.sublime-syntax"

$(echo 'a')
# <- punctuation.definition.command-substitution.shell
 # <- punctuation.section.block.begin.shell
#         ^ punctuation.section.block.end.shell

`echo 'a'`
# <- punctuation.section.block.begin.shell
#        ^ punctuation.section.block.end.shell

xxx
# <- variable.function

aaa'bbb'ccc
# <- -variable.function
#  ^^^^^^^^ -variable.function

xxx \
  yyy
# ^^^ -variable.function

a='23'b='43'#c='42'
# <- variable.other.shell
 # <- keyword.operator.assignment.shell
#     ^ -variable.other.shell
#      ^ -keyword.operator.assignment.shell

x="xxx$(a='23')ccc"
# <- variable.other.shell
 # <- keyword.operator.assignment.shell
#     ^ punctuation.definition.command-substitution.shell
#      ^ punctuation.section.block.begin.shell
#             ^ punctuation.section.block.end.shell
#        ^ keyword.operator.assignment.shell

y=
# <- variable.other.shell
 # <- keyword.operator.assignment.shell

z=$(sss)

z=$(ss \
#  ^ punctuation.section.block.begin
#      ^ punctuation.separator.continuation
s)
# <- meta.block.command-substitution.braces
 # <- punctuation.section.block.end

alias xyz="echo xyz"
# <- storage.type.alias.shell
#     ^^^ entity.name.alias.shell
#        ^ keyword.operator.assignment.shell

unalias xyz
# <- support.function.builtin

local jar=$(__find_application_jar) #aaa
# ^^^ storage.type
#                                   ^^^ comment.line

${xxx_yyy}
# <- punctuation.definition.parameter-expansion
 # <- punctuation.section.block.begin
#        ^ punctuation.section.block.end
#^^^^^^^^^ meta.block.parameter-expansion

  if echo cd
# ^^ keyword.control
#    ^^^^ support.function
#         ^^ -keyword -support -variable

if if echo cd
#  ^^ keyword.control
#     ^^^^ support.function
#          ^^ -keyword -support -variable

  echo if
# ^^^^ support.function
#      ^^ -keyword -support -variable

  echo cd '~/x/y/z'
# ^^^^ support.function
#      ^^ -keyword -support -variable
#         ^^^^^^^^^ string.quoted

cd ~/x/cd/z
# <- variable.function
#  ^^^^^^^^ -keyword -support -variable

echo 'aaa' echo
#          ^^^^ -keyword -support -variable

echo 'aaa' | echo
#          ^ keyword.operator.pipe

echo 'aaa' || echo
#          ^^ keyword.operator.logical

echo 'aaa' && echo
#          ^^ keyword.operator.logical

echo 'aaa' && cd /a/b/c
#             ^^ variable.function

if.
# <- -keyword

if
# <- keyword

return 'aaa' #xxx
# ^^^^ keyword.control
#      ^^^^^ -string.quoted
#            ^^^^ comment.line

echo \; echo
#    ^^ constant.character.escape

while true; do
#     ^^^^ constant.language
#         ^ punctuation.terminator
#           ^^ keyword.control

. /path/to/script
# <- storage.type

echo 'sss' >> echo; echo xxx
#          ^^ keyword.operator.redirection
#             ^^^^ -support
#                 ^ punctuation.terminator
#                   ^^^^ support.function
