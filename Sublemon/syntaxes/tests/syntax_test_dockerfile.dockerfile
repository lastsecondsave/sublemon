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

RUN --mount=type=secret,id=mysecret cat /run/secrets/mysecret
#   ^^^^^^^ variable.parameter.flag.dockerfile
#           ^^^^ constant.language.flag.attribute-name.dockerfile
#               ^ keyword.operator.assignment.flag.dockerfile
#                      ^ punctuation.separator.arguments.dockerfile
#                       ^^ constant.language.flag.attribute-name.dockerfile
#                         ^ keyword.operator.assignment.flag.dockerfile
#                                    ^^^^^^^^^^^ source.shell.bash

RUN python3 <<EOF > /test.txt
#           ^^ keyword.operator.heredoc.dockerfile
#             ^^^ entity.name.tag.heredoc.dockerfile
#                   ^^^^^^^^^ -meta.string.heredoc.dockerfile
print("test")
# <- -source.shell.bash
# ^^^^^^^^^^^ meta.shell-command.dockerfile meta.string.heredoc.dockerfile
EOF
#^^ entity.name.tag.heredoc.dockerfile

RUN <<EOF
#   ^^ keyword.operator.heredoc.dockerfile
#     ^^^ entity.name.tag.heredoc.dockerfile
echo "test"
# ^^^^^^^^^ meta.shell-command.dockerfile
# ^^^^^^^^^ source.shell.bash
EOF
#^^ entity.name.tag.heredoc.dockerfile

ENV ver=10.01
#^^ keyword.control.dockerfile
#   ^^^^^^^^^ meta.declaration.variable.dockerfile
#   ^^^ variable.other.readwrite.dockerfile
#      ^ -variable.other.readwrite.dockerfile

ENV one=001 two=002
#      ^^^^^ -variable.other.readwrite.dockerfile
#           ^^^ variable.other.readwrite.dockerfile
#       ^^^ constant.numeric.dockerfile
#               ^^^ constant.numeric.dockerfile

ENV one=001 \
#           ^ punctuation.separator.continuation.line.dockerfile
    two=002 \
#   ^^^ variable.other.readwrite.dockerfile
#       ^^^ constant.numeric.dockerfile
    three="001 002"
#          ^^^^^^^ string.quoted.double.dockerfile

ARG one="xxx $y $zz ${zzz}"
#^^ keyword.control.dockerfile
#       ^^^^^^^^^^^^^^^^^^^ meta.string.dockerfile
#       ^^^^ string.quoted.double.dockerfile
#                         ^ string.quoted.double.dockerfile
#            ^ punctuation.definition.variable.dockerfile
#             ^ variable.other.readwrite.dockerfile
#               ^ punctuation.definition.variable.dockerfile
#                ^^ variable.other.readwrite.dockerfile
#                   ^ punctuation.definition.variable.dockerfile
#                     ^^^ variable.other.readwrite.dockerfile

ENV ver='xxx'
#       ^^^^^ string.quoted.single.dockerfile

ENV ver=yyy.10
#           ^^ -constant.numeric.dockerfile

ENV ver=10.y'yy'
#       ^^ -constant.numeric.dockerfile
#           ^^^^ string.quoted.single.dockerfile

ARG version
#   ^^^^^^^ variable.other.readwrite.dockerfile

ARG version 1.2.1 ext
#   ^^^^^^^ variable.other.readwrite.dockerfile
#           ^^^^^^^^^ -variable.other.readwrite.dockerfile

ENV ver= ${VERSION}=x
#        ^^^^^^^^^^ variable.other.readwrite.dockerfile meta.interpolation.parameter.dockerfile
#                   ^ meta.value.dockerfile

ENV ver'si'o"n"=${VERSION}
#   ^^^^^^^^^^^ variable.other.readwrite.dockerfile
#      ^^^^ string.quoted.single.dockerfile
#           ^^^ string.quoted.double.dockerfile

ARG HOME=${xxx:+'yyy zz yyy'}
#             ^^ keyword.operator.assignment.dockerfile
#               ^^^^^^^^^^^^ string.quoted.single.dockerfile

ARG message="\
     hello\n\
#         ^^ string.quoted.double.dockerfile constant.character.escape.dockerfile
     ${world}"
#    ^^^^^^^^ -string.quoted.double.dockerfile meta.interpolation.parameter.dockerfile
#            ^ string.quoted.double.dockerfile

ENV message='\n\n\n\
#           ^^^^^^^ string.quoted.single.dockerfile -constant.character.escape.dockerfile
    xxx\
'
#<- string.quoted.single.dockerfile

LABEL com.example.vendor="ACME Incorporated"
#     ^^^^^^^^^^^^^^^^^^ variable.other.readwrite.dockerfile

CMD ["sudo", "apt", "update"]
#   ^ punctuation.section.json-sequence.begin.dockerfile
#                           ^ punctuation.section.json-sequence.end.dockerfile
#          ^ punctuation.separator.json-sequence.dockerfile
#    ^^^^^^ string.quoted.double.dockerfile
#            ^^^^^ string.quoted.double.dockerfile

SHELL ["powershell", \
       "-command"]
#      ^^^^^^^^^^^ meta.json-sequence.dockerfile

CMD sudo apt update
#   ^^^^^^^^^^^^^^^ meta.shell-command.dockerfile source.shell.bash

CMD \[ -n $HOME ] && echo 1
#   ^^^^^^^^^^^^^^^^^^^^^^^ meta.shell-command.dockerfile

ONBUILD CMD apt update
#^^^^^^ storage.type.onbuild.dockerfile
#       ^^^ keyword.control.dockerfile
#           ^^^^^^^^^^ meta.shell-command.dockerfile source.shell.bash

HEALTHCHECK NONE
#^^^^^^^^^^ keyword.control.dockerfile
#           ^^^^ constant.language.dockerfile

HEALTHCHECK --interval=5m --timeout=3s \
#^^^^^^^^^^ keyword.control.dockerfile
#           ^^^^^^^^^^ variable.parameter.flag.dockerfile
#                     ^ keyword.operator.assignment.flag.dockerfile
#                          ^^^^^^^^ variable.parameter.flag.dockerfile
#                                  ^ keyword.operator.assignment.flag.dockerfile

  CMD curl -f http://localhost/ || exit 1
# ^^^ keyword.control.dockerfile
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ meta.shell-command.dockerfile source.shell.bash


HEALTHCHECK --interval=5m --timeout=3s CMD ["check"]
#                                      ^^^ keyword.control.dockerfile
#                                          ^^^^^^^^^ meta.json-sequence.dockerfile

FROM image:42
#^^ keyword.control.dockerfile
#         ^ punctuation.separator.dockerfile

FROM --platform=amd64 image:42
#^^ keyword.control.dockerfile
#    ^^^^^^^^^^ variable.parameter.flag.dockerfile
#              ^ keyword.operator.assignment.flag.dockerfile
#                          ^ punctuation.separator.dockerfile

FROM image:42 AS name
#^^ keyword.control.dockerfile
#             ^^ keyword.control.dockerfile
#                ^^^^ entity.name.stage.dockerfile

FROM ${FROM}:42 \
#               ^ punctuation.separator.continuation.line.dockerfile
#           ^ punctuation.separator.dockerfile
#    ^^^^^^^ meta.interpolation.parameter.dockerfile

     AS name
#    ^^ keyword.control.dockerfile
#       ^^^^ entity.name.stage.dockerfile

COPY file.txt ${OTHER} dir/${BUILD}/file.txt
#^^^ keyword.control.dockerfile
#             ^^^^^^^^ meta.interpolation.parameter.dockerfile
#                          ^^^^^^^^ meta.interpolation.parameter.dockerfile

COPY ["file with space.txt", "dir/file.txt"]
#    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ meta.json-sequence.dockerfile
#^^^ keyword.control.dockerfile

COPY --chown=user:group file.txt dir/file.txt
#    ^^^^^^^ variable.parameter.flag.dockerfile

COPY --chown=user:group ["file.txt", "dir/file.txt"]
#    ^^^^^^^ variable.parameter.flag.dockerfile
#                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^ meta.json-sequence.dockerfile

COPY <<EOF ${BUILD}/run.sh
#    ^^ keyword.operator.heredoc.dockerfile
#      ^^^ entity.name.tag.heredoc.dockerfile
#          ^^^^^^^^ meta.interpolation.parameter.dockerfile
#!/usr/bin/env bash
# <- -comment
echo \${BUILD}
#    ^^ constant.character.escape.dockerfile
echo ${BUILD}
#    ^^^^^^^^ meta.interpolation.parameter.dockerfile
EOF
#^^ entity.name.tag.heredoc.dockerfile

WORKDIR ${HOME}/app
#       ^^^^^^^ meta.interpolation.parameter.dockerfile
