import sys
sys.path.append("../lib")
from settings import setup, settings

setup()

settings("source.java",
  increase_indent_pattern = [
    r".*[\{\[]\s*$",        # '{' and '[' braces
    r"\s*+[^.@].*\)\s*$",   # ')' at the end and no ';'
    r".*[=]\s*$"            # '=' at the end
  ],
  decrease_indent_pattern = [
    r"\s*[\}\]].*$"
  ],
  indent_parens = True,
  line_comment = '//',
  block_comment = ['/*', '*/']
)

settings("source.java constant.user.enum",
  show_in_indexed_symbol_list = 1
)

method_transformations = [
  r"s/\/\*.*?\*\// /g",
  r"s/(?>\bfinal\b|<.*>|@\S+)//g",
  r"s/\s{2,}/ /g",
  r"s/(?<=\() | (?=[,()])//g"
]

anonymous_method_transformations = method_transformations + [r"s/^/\? /"]
anonymous_class_transformations = [r"s/\{/class \?/"]

def indent(x):
  return [r"s/^/{}/".format(' ' * x * 4)]

anonymous_class_scope  = " meta.class.body.anonymous punctuation.definition.class.begin"
anonymous_method_scope = " meta.class.body.anonymous meta.method.identifier"

for i in range(5):
  settings("source.java" + " meta.class.body"*i + " meta.class.identifier",
    show_in_symbol_list = 1,
    symbol_transformation = [r"s/\s{2,}/ /g"] + indent(i)
  )

  j = i + 1

  settings("source.java" + " meta.class.body"*j + " meta.method.identifier",
    show_in_symbol_list = 1,
    symbol_transformation = method_transformations + indent(j)
  )

  settings("source.java" + " meta.class.body"*j + " constant.user.enum",
    show_in_symbol_list = 1,
    symbol_transformation = indent(j)
  )

  settings("source.java" + " meta.class.body.java"*j + anonymous_class_scope,
    show_in_symbol_list = 1,
    symbol_transformation = anonymous_class_transformations + indent(j)
  )

  settings("source.java" + " meta.class.body.java"*j + anonymous_method_scope,
    show_in_symbol_list = 1,
    symbol_transformation = anonymous_method_transformations + indent(j + 1)
  )

  settings("source.java" + " meta.class.body.java"*j + " meta.method.body" + anonymous_class_scope,
    show_in_symbol_list = 1,
    symbol_transformation = anonymous_class_transformations + indent(j + 1)
  )

  settings("source.java" + " meta.class.body.java"*j + " meta.method.body" + anonymous_method_scope,
    show_in_symbol_list = 1,
    symbol_transformation = anonymous_method_transformations + indent(j + 2)
  )

  settings("source.java" + " meta.method.body"*j + anonymous_class_scope,
    show_in_symbol_list = 1,
    symbol_transformation = anonymous_class_transformations + indent(j*2)
  )

  settings("source.java" + " meta.method.body"*j + anonymous_method_scope,
    show_in_symbol_list = 1,
    symbol_transformation = anonymous_method_transformations + indent(j*2 + 1)
  )

settings("text.log.java entity.name.exception",
  show_in_symbol_list = 1
)

settings("source.java-props",
  line_comments = ["#", "!"]
)

settings("source.java-props entity.name.key.java-props",
  show_in_symbol_list = 1,
  symbol_transformation = ["s/\\//g"]
)
