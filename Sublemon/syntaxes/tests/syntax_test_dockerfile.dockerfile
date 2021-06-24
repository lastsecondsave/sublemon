# SYNTAX TEST "Packages/Sublemon/syntaxes/Dockerfile.sublime-syntax"

RUN apt update && apt install sudo
#^^ keyword.control.dockerfile
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
#^^ keyword.control.dockerfile
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
#^^ keyword.control.dockerfile
#       ^^^^^^^^^^^^^^^^^^^ string.quoted.double.dockerfile
#            ^ punctuation.definition.variable.dockerfile
#             ^ variable.other.readwrite.dockerfile
#               ^ punctuation.definition.variable.dockerfile
#                ^^ variable.other.readwrite.dockerfile
#                   ^ punctuation.definition.variable.dockerfile
#                     ^^^ variable.other.readwrite.dockerfile

ARG version 1.2.1
#   ^^^^^^^ variable.other.readwrite.dockerfile

LABEL com.example.vendor="ACME Incorporated"
#     ^^^^^^^^^^^^^^^^^^ variable.other.readwrite.dockerfile

CMD ["sudo", "apt", "update"]
#   ^^^^^^^^^^^^^^^^^^^^^^^^^ meta.json.dockerfile source.json

CMD sudo apt update
#   ^^^^^^^^^^^^^^^ meta.shell-command.dockerfile source.shell.bash

ONBUILD CMD apt update
#^^^^^^ storage.type.onbuild.dockerfile
#       ^^^ keyword.control.dockerfile
#           ^^^^^^^^^^ meta.shell-command.dockerfile source.shell.bash

HEALTHCHECK NONE
#^^^^^^^^^^ keyword.control.dockerfile
#           ^^^^ constant.language.dockerfile

HEALTHCHECK --interval=5m --timeout=3s \
#^^^^^^^^^^ keyword.control.dockerfile
  CMD curl -f http://localhost/ || exit 1
# ^^^ keyword.control.dockerfile
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ meta.shell-command.dockerfile source.shell.bash


HEALTHCHECK --interval=5m --timeout=3s CMD ["check"]
#                                      ^^^ keyword.control.dockerfile
#                                          ^^^^^^^^^ meta.json.dockerfile source.json
