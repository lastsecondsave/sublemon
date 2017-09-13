import sys
sys.path.append('../lib')
from snippets import setup, scope, snippet

setup()

scope('source.powershell')

## KEYWORDS ##

snippet(tabTrigger='man', content='Mandatory')
snippet(tabTrigger='valp', content='ValueFromPipeline')

## ONE-LINERS ##

snippet(tabTrigger='%', description='ForEach-Object', content=
'%{ ${0:$SELECTION} }'
)

snippet(tabTrigger='?', description='Where-Object', content=
'?{ ${0:$SELECTION} }'
)

snippet(tabTrigger='pm', description='Parameter', content=
'[Parameter($1)]$0'
)

## BLOCKS ##

snippet(tabTrigger='begin', description='begin', content=
"""
begin {
    $0
}
""")

snippet(tabTrigger='process', description='process', content=
"""
process {
    $0
}
""")

snippet(tabTrigger='end', description='end', content=
"""
end {
    $0
}
""")

snippet(tabTrigger='fun', description='function', content=
"""
function ${1:run} {
    $0
}
""")

snippet(tabTrigger='param', description='param', content=
"""
param (
    $0
)
""")
