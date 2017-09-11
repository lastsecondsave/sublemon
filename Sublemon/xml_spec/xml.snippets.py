import sys
sys.path.append('../lib')
from snippets import setup, scope, snippet

setup()

scope('source.xml')

snippet(tabTrigger='<', description='tag', content=
'<${1:p}>${2:$SELECTION}</${1/([^ ]+).*/$1/}>'
)

snippet(tabTrigger='>', description='empty tag', content=
'<${1:name}/>'
)

snippet(tabTrigger='a', description='attribute', scope='source.xml meta.tag.xml', content=
'${1:name}="$2"'
)

snippet(tabTrigger='cdata', description='CDATA', content=
'<![CDATA[${0:$SELECTION}]]>'
)

snippet(tabTrigger='xml', description='xml declaration', content=
'<?xml version="1.0" encoding="UTF-8"?>'
)
