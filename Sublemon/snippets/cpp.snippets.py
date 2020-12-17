from snippets_lib import *

cpp = Snippets('source.c++')

cpp/'pl' - ('std::cout', r"std::cout << ${0:$SELECTION} << '\n';")

cpp/ind/'dc' - ('doc comment', r'/**==>${SELECTION/^\s*/ * /mg}$0==> */')

cpp/'inc' - ('#include', '#include $0')
cpp/'#in' - ('#include', '#include $0')
cpp/'ifdef' - ('#ifdef', '#ifdef $1\n${0:$SELECTION}\n#endif')
