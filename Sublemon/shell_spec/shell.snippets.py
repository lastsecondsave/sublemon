import sys
sys.path.append('../lib')
from snippets import Snippets

sh = Snippets('source.shell')

sh.awk = ('awk', "awk '{$0}'")

sh.case = ('case',
"""
case $1 in
    $0
esac
""")

sh['if'] = ('if',
"""
if [[ $1 ]]; then
    $0
fi
""")

sh.ff = ('function',
"""
$1() {
    $0
}
""")
