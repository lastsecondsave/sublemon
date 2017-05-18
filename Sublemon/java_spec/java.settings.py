import sys
sys.path.append("../lib")
import settings

settings.cleanup()

settings.entry("source.java",
  increase_indent_pattern = [
    r".*[\{\[]\s*$"
  ],
  decrease_indent_pattern = [
    r"\s*[\}\]].*$"
  ],
  indent_parens = True,
  line_comment = '//',
  block_comment = ['/*', '*/']
)

settings.entry("source.java constant.user.enum",
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
  settings.entry("source.java" + " meta.class.body"*i + " meta.class.identifier",
    show_in_symbol_list = 1,
    symbol_transformation = [r"s/\s{2,}/ /g"] + indent(i)
  )

  j = i + 1

  settings.entry("source.java" + " meta.class.body"*j + " meta.method.identifier",
    show_in_symbol_list = 1,
    symbol_transformation = method_transformations + indent(j)
  )

  settings.entry("source.java" + " meta.class.body"*j + " constant.user.enum",
    show_in_symbol_list = 1,
    symbol_transformation = indent(j)
  )

  settings.entry("source.java" + " meta.class.body.java"*j + anonymous_class_scope,
    show_in_symbol_list = 1,
    symbol_transformation = anonymous_class_transformations + indent(j)
  )

  settings.entry("source.java" + " meta.class.body.java"*j + anonymous_method_scope,
    show_in_symbol_list = 1,
    symbol_transformation = anonymous_method_transformations + indent(j + 1)
  )

  settings.entry("source.java" + " meta.class.body.java"*j + " meta.method.body" + anonymous_class_scope,
    show_in_symbol_list = 1,
    symbol_transformation = anonymous_class_transformations + indent(j + 1)
  )

  settings.entry("source.java" + " meta.class.body.java"*j + " meta.method.body" + anonymous_method_scope,
    show_in_symbol_list = 1,
    symbol_transformation = anonymous_method_transformations + indent(j + 2)
  )

  settings.entry("source.java" + " meta.method.body"*j + anonymous_class_scope,
    show_in_symbol_list = 1,
    symbol_transformation = anonymous_class_transformations + indent(j*2)
  )

  settings.entry("source.java" + " meta.method.body"*j + anonymous_method_scope,
    show_in_symbol_list = 1,
    symbol_transformation = anonymous_method_transformations + indent(j*2 + 1)
  )

settings.entry("text.log.java entity.name.exception",
  show_in_symbol_list = 1
)

settings.entry("source.java-props",
  line_comments = ["#", "!"]
)

settings.entry("source.java-props entity.name.key.java-props",
  show_in_symbol_list = 1,
  symbol_transformation = ["s/\\//g"]
)
