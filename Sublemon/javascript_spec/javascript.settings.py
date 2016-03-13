import os, hashlib, plistlib, shutil

shutil.rmtree("generated", ignore_errors=True)
os.mkdir("generated")

def settings(scope, **settings):
  filename = hashlib.sha1(scope.encode('ascii')).hexdigest() + ".tmPreferences"
  print("{}: {}".format(filename, scope))
  with open(os.path.join("generated", filename), "wb") as pfile:
    plistlib.dump(dict(scope=scope, settings=settings), pfile)

## JAVASCRIPT ##

settings("source.js",
  increaseIndentPattern = r".*(?>[\{\[])\s*$",
  decreaseIndentPattern = r"\s*(?>[\}\]]).*$",
  indentParens = True,
  shellVariables = [
    dict(name = "TM_COMMENT_START",   value = "// "),
    dict(name = "TM_COMMENT_START_2", value = "/*"),
    dict(name = "TM_COMMENT_END_2",   value = "*/")
  ]
)

settings("meta.function.identifier.javascript",
  showInSymbolList = 1,
  symbolTransformation = r's/\.prototype\./\./g;'
)

settings("meta.function.body.javascript entity.name.function",
  showInSymbolList = 0,
  showInIndexedSymbolList = 0
)
