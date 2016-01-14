import os, hashlib, plistlib, shutil

shutil.rmtree("generated", ignore_errors=True)
os.mkdir("generated")

def settings(scope, **settings):
  filename = hashlib.sha1(scope.encode('ascii')).hexdigest() + ".tmPreferences"
  print("{}: {}".format(filename, scope))
  with open(os.path.join("generated", filename), "wb") as pfile:
    plistlib.dump(dict(scope=scope, settings=settings), pfile)


settings("comment.mark",
  showInSymbolList = 1,
  symbolTransformation = "s/^/> /;"
)

settings("source.groovy",
  shellVariables = [
    dict(name = "TM_COMMENT_START",   value = "// "),
    dict(name = "TM_COMMENT_START_2", value = "/*"),
    dict(name = "TM_COMMENT_END_2",   value = "*/")
  ]
)

settings("source.ini",
  shellVariables = [
    dict(name = "TM_COMMENT_START",   value = "; "),
    dict(name = "TM_COMMENT_START_2", value = "# ")
  ]
)

settings("source.ini entity.name.section",
  showInSymbolList = 1
)

settings("source.unix",
  shellVariables = [
    dict(name = "TM_COMMENT_START", value = "# ")
  ]
)

settings("text.markdown markup.heading.markdown",
  showInSymbolList = 1,
  symbolTransformation = \
    r"s/\s*#*$//;" + \
    r"s/(?<=#)#/   /g;" + \
    r"s/^#//;"
)

settings("text.rfc entity.name.title",
  showInSymbolList = 1
)
