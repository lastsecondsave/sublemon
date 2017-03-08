import sys
sys.path.append("../lib")
import settings

settings.cleanup()

## COMMON ##

settings.scope("comment.mark",
  showInSymbolList = 1,
  symbolTransformation = "s/^/> /;"
)

## SOURCE ##

settings.scope("source.groovy",
  shellVariables = [
    dict(name = "TM_COMMENT_START",   value = "// "),
    dict(name = "TM_COMMENT_START_2", value = "/*"),
    dict(name = "TM_COMMENT_END_2",   value = "*/")
  ]
)

settings.scope("source.ini",
  shellVariables = [
    dict(name = "TM_COMMENT_START",   value = "; "),
    dict(name = "TM_COMMENT_START_2", value = "# ")
  ]
)

settings.scope("source.ini entity.name.section",
  showInSymbolList = 1
)

settings.scope("source.unix",
  shellVariables = [
    dict(name = "TM_COMMENT_START", value = "# ")
  ]
)

## TEXT ##

settings.scope("text.markdown markup.heading entity.name.section",
  showInSymbolList = 1,
  symbolTransformation = \
    r"s/\s*#*$//;" + \
    r"s/(?<=#)#/   /g;" + \
    r"s/^#//;"
)

settings.scope("text.rfc entity.name.title",
  showInSymbolList = 1
)
