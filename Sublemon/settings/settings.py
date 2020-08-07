from settings_lib import settings

settings("meta.context.sublime-syntax entity.name.tag",
         show_in_symbol_list=1,
         show_in_indexed_symbol_list=1)

settings("meta.variables.sublime-syntax entity.name.tag",
         show_in_symbol_list=1,
         show_in_indexed_symbol_list=1,
         symbol_transformation='/.*/[var] $0/')

settings("source.ini",
         line_comment=(';', '#'))

settings("source.ini entity.name.section",
         show_in_symbol_list=1)

settings("source.unix",
         line_comment='#')

settings("text.rfc entity.name.title",
         show_in_symbol_list=1)

settings("source.powershell",
         line_comment='#',
         block_comment=('<#', '#>'))

settings("source.python",
         increase_indent_pattern=r"^(\s*(class|(\basync\s+)?(def|for|with)|elif|else|except|finally|if|try|while)\b.*:|.*[\{\[])\s*$",
         decrease_indent_pattern=r"^\s*((elif|else|except|finally)\b.*:|[\}\]])")
