import sys
sys.path.append('../lib')
from snippets import setup, scope, snippet

setup()

scope('source.shell')

snippet(tabTrigger='awk', description='awk', content=
"awk '{$0}'"
)

snippet(tabTrigger='case', description='case', content=
"""
case $1 in
    $0
esac
""")

snippet(tabTrigger='if', description='if', content=
"""
if [[ $1 ]]; then
    $0
fi
""")

snippet(tabTrigger='ff', description='function', content=
"""
$1() {
    $0
}
""")

