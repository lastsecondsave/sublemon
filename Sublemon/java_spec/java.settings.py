import os, hashlib, plistlib, shutil

shutil.rmtree("generated", ignore_errors=True)
os.mkdir("generated")

def settings(scope, **settings):
  filename = hashlib.sha1(scope.encode('ascii')).hexdigest() + ".tmPreferences"
  print("{}: {}".format(filename, scope))
  with open(os.path.join("generated", filename), "wb") as pfile:
    plistlib.dump(dict(scope=scope, settings=settings), pfile)

## JAVA ##

settings("source.java",
  increaseIndentPattern = r".*(?>[\{\[])\s*$",
  decreaseIndentPattern = r"\s*(?>[\}\]]).*$",
  indentParens = True,
  shellVariables = [
    dict(name = "TM_COMMENT_START",   value = "// "),
    dict(name = "TM_COMMENT_START_2", value = "/*"),
    dict(name = "TM_COMMENT_END_2",   value = "*/")
  ]
)

settings("source.java constant.user.enum",
  showInIndexedSymbolList = 1
)

method_transformation = \
  r"s/\/\*.*?\*\// /g;" + \
  r"s/(?>\bfinal\b|<.*>|@\S+)//g;" + \
  r"s/\s{2,}/ /g;" + \
  r"s/(?<=\() | (?=[,()])//g;"

anonymous_method_transformation = method_transformation + r"s/^/\? /;"
anonymous_class_transformation = r"s/\{/class \?/;"

indent = lambda x: r"s/^/{}/;".format(' ' * x * 2)

anonymous_class_scope  = " meta.class.body.anonymous punctuation.definition.class.begin"
anonymous_method_scope = " meta.class.body.anonymous meta.method.identifier"

for i in range(5):
  settings("source.java" + " meta.class.body"*i + " meta.class.identifier",
    showInSymbolList = 1,
    symbolTransformation = r"s/\s{2,}/ /g;" + indent(i)
  )

  j = i + 1

  settings("source.java" + " meta.class.body"*j + " meta.method.identifier",
    showInSymbolList = 1,
    symbolTransformation = method_transformation + indent(j)
  )

  settings("source.java" + " meta.class.body"*j + " constant.user.enum",
    showInSymbolList = 1,
    symbolTransformation = indent(j)
  )

  settings("source.java" + " meta.class.body.java"*j + anonymous_class_scope,
    showInSymbolList = 1,
    symbolTransformation = anonymous_class_transformation + indent(j)
  )

  settings("source.java" + " meta.class.body.java"*j + anonymous_method_scope,
    showInSymbolList = 1,
    symbolTransformation = anonymous_method_transformation + indent(j + 1)
  )

  settings("source.java" + " meta.class.body.java"*j + " meta.method.body" + anonymous_class_scope,
    showInSymbolList = 1,
    symbolTransformation = anonymous_class_transformation + indent(j + 1)
  )

  settings("source.java" + " meta.class.body.java"*j + " meta.method.body" + anonymous_method_scope,
    showInSymbolList = 1,
    symbolTransformation = anonymous_method_transformation + indent(j + 2)
  )

  settings("source.java" + " meta.method.body"*j + anonymous_class_scope,
    showInSymbolList = 1,
    symbolTransformation = anonymous_class_transformation + indent(j*2)
  )

  settings("source.java" + " meta.method.body"*j + anonymous_method_scope,
    showInSymbolList = 1,
    symbolTransformation = anonymous_method_transformation + indent(j*2 + 1)
  )

## JAVA LOG ##

settings("text.log.java entity.name.exception",
  showInSymbolList = 1
)

## JAVA PROPERTIES ##

settings("source.java-props",
  shellVariables = [
    dict(name = "TM_COMMENT_START",   value = "# "),
    dict(name = "TM_COMMENT_START_2", value = "! ")
  ]
)

settings("source.java-props entity.name.key.java-props",
  showInSymbolList = 1,
  symbolTransformation = "s/\\//g;"
)
