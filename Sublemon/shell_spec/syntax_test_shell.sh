# SYNTAX TEST "Packages/Sublemon/shell_spec/shell.sublime-syntax"

$(echo 'a')
# <- punctuation.definition.command-substitution.shell
 # <- punctuation.section.block.begin.shell
#         ^ punctuation.section.block.end.shell

`echo 'a'`
# <- punctuation.section.block.begin.shell
#        ^ punctuation.section.block.end.shell

a='23'b='43'#c='42'
# <- variable.parameter.shell
 # <- keyword.operator.assignment.shell
#     ^ -variable.parameter.shell
#      ^ -keyword.operator.assignment.shell

x="xxx$(a='23')ccc"
# <- variable.parameter.shell
 # <- keyword.operator.assignment.shell
#     ^ punctuation.definition.command-substitution.shell
#      ^ punctuation.section.block.begin.shell
#             ^ punctuation.section.block.end.shell
#        ^ keyword.operator.assignment.shell

y=
# <- variable.parameter.shell
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

if if echo cd

echo if

echo cd '~/x/y/z'

cd ~/x/cd/z

echo 'aaa' echo

echo 'aaa' | echo
#          ^ keyword.operator.pipe

echo 'aaa' || echo
#          ^^ keyword.operator.logical

echo 'aaa' && echo
#          ^^ keyword.operator.logical

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
