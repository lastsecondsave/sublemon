from snippets_lib import *

cpp = Snippets('source.c++')

cpp/'pl' - ('std::cout', r"std::cout << ${0:$SELECTION} << '\n';")
cpp/'inc' - ('#include', '#include <$0>')
