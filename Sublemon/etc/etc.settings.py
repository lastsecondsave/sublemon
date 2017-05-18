import sys
sys.path.append("../lib")
import settings

settings.cleanup()

settings.entry("source.ini",
  line_comment = [';', '#']
)

settings.entry("source.ini entity.name.section",
  show_in_symbol_list = 1
)

settings.entry("source.unix",
  line_comment = '#'
)

settings.entry("text.rfc entity.name.title",
  show_in_symbol_list = 1
)
