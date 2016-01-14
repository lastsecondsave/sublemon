import os, hashlib, plistlib, shutil

shutil.rmtree("generated", ignore_errors=True)
os.mkdir("generated")

def settings(scope, **settings):
  filename = hashlib.sha1(scope.encode('ascii')).hexdigest() + ".tmPreferences"
  print("{}: {}".format(filename, scope))
  with open(os.path.join("generated", filename), "wb") as pfile:
    plistlib.dump(dict(scope=scope, settings=settings), pfile)


settings("source.java",
  bracketIndentNextLinePattern = r"^\s*\b(if|while|else)\b[^;]*$|^\s*\b(for)\b.*$",
  increaseIndentPattern        = r"^\s*(.*\{[^}]*|\b(case\s+\w+|default):)\s*$",
  decreaseIndentPattern        = r"^\s*((.*\*/\s*)?\};?|\b(case\s+\w+|default):)\s*$",
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
  r"s/(?<=\() | (?=[,()])//g;" + \
  r"s/(?=.{100,})([^(]+).*/$1\(...\)/;"

indent = lambda x: r"s/^/{}/;".format(' ' * x * 2)

for i in range(5):
  settings("source.java" + " meta.class.body"*i + " meta.class.identifier",
    showInSymbolList = 1,
    symbolTransformation = r"s/\s{2,}/ /g;" + indent(i)
  )

  m = i + 1

  settings("source.java" + " meta.class.body"*m + " meta.method.identifier",
    showInSymbolList = 1,
    symbolTransformation = method_transformation + indent(m)
  )

  settings("source.java" + " meta.class.body"*m + " constant.user.enum",
    showInSymbolList = 1,
    symbolTransformation = indent(m)
  )

  settings("source.java" + " meta.method.body"*m + " meta.class.body.anonymous punctuation.definition.class.begin",
    showInSymbolList = 1,
    symbolTransformation = r"s/\{/class \?/;" + indent(m*2)
  )

  settings("source.java" + " meta.method.body"*m + " meta.class.body.anonymous meta.method.identifier",
    showInSymbolList = 1,
    symbolTransformation = method_transformation + r"s/^/\? /;" + indent(m*2 + 1)
  )

settings("text.log.java entity.name.exception",
  showInSymbolList = 1
)

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
