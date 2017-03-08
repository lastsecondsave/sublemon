import sys
sys.path.append("../lib")
import settings

settings.cleanup()

settings.entry("source.css",
  block_comment = ['/*', '*/']
)

settings.entry("source.css meta.rule.selector.css",
  showInSymbolList = 1,
  symbolTransformations = [
    r"s/\n/ /",
    r"s/\s{2,}/ /g",
    r"s/^@//g"
  ]
)

settings.entry("source.css meta.at-rule.body.css meta.rule.selector.css",
  showInSymbolList = 1,
  symbolTransformations = [
    r"s/\n/ /",
    r"s/\s{2,}/ /g",
    r"s/^@//g",
    r"s/^/    /g"
  ]
)
