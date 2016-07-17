# SYNTAX TEST "Packages/Sublemon/shell_spec/shell.sublime-syntax"

action() {
# <-- entity.name.function
}

var1=value;var2=another_value
# <-- variable.user.shell
#   ^ keyword.operator.shell
#          ^ variable.user.shell
#              ^ keyword.operator.shell

$var1=
# <-- invalid.illegal
 # <-- variable.user.shell

export var1
# <-- keyword.shell
#      ^variable.user.shell

export $var1=value
