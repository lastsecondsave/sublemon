# SYNTAX TEST "Packages/Sublemon/shell_spec/shell.sublime-syntax"

$(echo 'a')
# <- punctuation.definition.command-substitution.shell
 # <- punctuation.section.block.begin.shell
#         ^ punctuation.section.block.end.shell

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

alias xyz="echo xyz"
# <- storage.type.alias.shell
#     ^^^ entity.name.alias.shell
#        ^ keyword.operator.assignment.shell

unalias xyz
# <- support.function.builtin

if echo cd

if if echo cd

echo if

echo cd '~/x/y/z'

cd ~/x/cd/z
