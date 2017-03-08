import sys
sys.path.append("../lib")
import settings

settings.cleanup()

settings.entry("source.java",
  increaseIndentPatterns = [
    r".*[\{\[]\s*$"
  ],
  decreaseIndentPatterns = [
    r"\s*[\}\]].*$"
  ],
  indentParens = True,
  line_comment = '// ',
  block_comment = ['/*', '*/']
)

settings.entry("source.java constant.user.enum",
  showInIndexedSymbolList = 1
)

method_transformations = [
  r"s/\/\*.*?\*\// /g",
  r"s/(?>\bfinal\b|<.*>|@\S+)//g",
  r"s/\s{2,}/ /g",
  r"s/(?<=\() | (?=[,()])//g"
]

anonymous_method_transformations = method_transformations + [r"s/^/\? /"]
anonymous_class_transformations = [r"s/\{/class \?/"]

def indent(x): return [r"s/^/{}/".format(' ' * x * 4)]

anonymous_class_scope  = " meta.class.body.anonymous punctuation.definition.class.begin"
anonymous_method_scope = " meta.class.body.anonymous meta.method.identifier"

for i in range(5):
  settings.entry("source.java" + " meta.class.body"*i + " meta.class.identifier",
    showInSymbolList = 1,
    symbolTransformations = [r"s/\s{2,}/ /g"] + indent(i)
  )

  j = i + 1

  settings.entry("source.java" + " meta.class.body"*j + " meta.method.identifier",
    showInSymbolList = 1,
    symbolTransformations = method_transformations + indent(j)
  )

  settings.entry("source.java" + " meta.class.body"*j + " constant.user.enum",
    showInSymbolList = 1,
    symbolTransformations = indent(j)
  )

  settings.entry("source.java" + " meta.class.body.java"*j + anonymous_class_scope,
    showInSymbolList = 1,
    symbolTransformations = anonymous_class_transformations + indent(j)
  )

  settings.entry("source.java" + " meta.class.body.java"*j + anonymous_method_scope,
    showInSymbolList = 1,
    symbolTransformations = anonymous_method_transformations + indent(j + 1)
  )

  settings.entry("source.java" + " meta.class.body.java"*j + " meta.method.body" + anonymous_class_scope,
    showInSymbolList = 1,
    symbolTransformations = anonymous_class_transformations + indent(j + 1)
  )

  settings.entry("source.java" + " meta.class.body.java"*j + " meta.method.body" + anonymous_method_scope,
    showInSymbolList = 1,
    symbolTransformations = anonymous_method_transformations + indent(j + 2)
  )

  settings.entry("source.java" + " meta.method.body"*j + anonymous_class_scope,
    showInSymbolList = 1,
    symbolTransformations = anonymous_class_transformations + indent(j*2)
  )

  settings.entry("source.java" + " meta.method.body"*j + anonymous_method_scope,
    showInSymbolList = 1,
    symbolTransformations = anonymous_method_transformations + indent(j*2 + 1)
  )

settings.entry("text.log.java entity.name.exception",
  showInSymbolList = 1
)

settings.entry("source.java-props",
  line_comments = ["# ", "! "]
)

settings.entry("source.java-props entity.name.key.java-props",
  showInSymbolList = 1,
  symbolTransformations = ["s/\\//g"]
)
