import os, hashlib, plistlib, shutil

shutil.rmtree("generated", ignore_errors=True)
os.mkdir("generated")

def settings(scope, **settings):
  filename = hashlib.sha1(scope.encode('ascii')).hexdigest() + ".tmPreferences"
  print("{}: {}".format(filename, scope))
  with open(os.path.join("generated", filename), "wb") as pfile:
    plistlib.dump(dict(scope=scope, settings=settings), pfile)

## YAML ##

settings("source.yaml",
  increaseIndentPattern = r"^(.*:\s*[>|]?\s*|\s*-\s+.*)$",
  decreaseIndentPattern = r"^\s*-\s+.*$",
  shellVariables = [
    dict(name = "TM_COMMENT_START", value = "# ")
  ]
)
