# SYNTAX TEST "Packages/Sublemon/syntaxes/Dockerfile.sublime-syntax"

RUN apt update && apt install sudo
#^^ keyword.control.RUN.dockerfile
#   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ meta.shell-command.dockerfile source.shell.bash

RUN apt update \
 && apt install sudo
#^^^^^^^^^^^^^^^^^^^ meta.shell-command.dockerfile source.shell.bash

RUN apt update \
#   ^^^^^^^^^^^^ meta.shell-command.dockerfile source.shell.bash
#              ^ punctuation.separator.continuation.line.shell
 && apt install sudo
#^^^^^^^^^^^^^^^^^^^ meta.shell-command.dockerfile source.shell.bash

RUN apt update
#   ^^^^^^^^^^ meta.shell-command.dockerfile source.shell.bash
 && apt install sudo
#^^^^^^^^^^^^^^^^^^^ -meta.shell-command.dockerfile -source.shell.bash

ENV ver=10.01
#^^ keyword.control.ENV.dockerfile
#   ^^^^^^^^^ meta.declaration.variable.dockerfile
#   ^^^ variable.other.readwrite.dockerfile

ENV one=001 two=002
#      ^^^^^ -variable.other.readwrite.dockerfile
#           ^^^ variable.other.readwrite.dockerfile

ENV one=001 \
#           ^ punctuation.separator.continuation.line.dockerfile
    two=002
#   ^^^ variable.other.readwrite.dockerfile

ARG one="xxx $y $zz ${zzz}"
#^^ keyword.control.ARG.dockerfile
#       ^^^^^^^^^^^^^^^^^^^ string.quoted.double.dockerfile
#            ^ punctuation.definition.variable.dockerfile
#             ^ variable.other.readwrite.dockerfile
#               ^ punctuation.definition.variable.dockerfile
#                ^^ variable.other.readwrite.dockerfile
#                   ^ punctuation.definition.variable.dockerfile
#                     ^^^ variable.other.readwrite.dockerfile
