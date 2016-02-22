import os, hashlib, plistlib, shutil

shutil.rmtree("generated", ignore_errors=True)
os.mkdir("generated")

def settings(scope, **settings):
  filename = hashlib.sha1(scope.encode('ascii')).hexdigest() + ".tmPreferences"
  print("{}: {}".format(filename, scope))
  with open(os.path.join("generated", filename), "wb") as pfile:
    plistlib.dump(dict(scope=scope, settings=settings), pfile)

## CSS ##

settings("source.css",
  shellVariables = [
    dict(name = "TM_COMMENT_START", value = "/*"),
    dict(name = "TM_COMMENT_END",   value = "*/")
  ]
)

settings("source.css meta.rule.selector.css",
  showInSymbolList = 1,
  symbolTransformation = ';'.join([
    r"s/\n/ /",
    r"s/\s{2,}/ /g",
    r"s/^@//g"
  ])
)

settings("source.css meta.at-rule.body.css meta.rule.selector.css",
  showInSymbolList = 1,
  symbolTransformation = ';'.join([
    r"s/\n/ /",
    r"s/\s{2,}/ /g",
    r"s/^@//g",
    r"s/^/    /g"
  ])
)
