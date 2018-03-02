import sys
sys.path.append('../lib')
from snippets import Snippets

xml = Snippets('text.xml')

xml['<'] = ('tag', '<${1:p}>${2:$SELECTION}</${1/([^ ]+).*/$1/}>')
xml['>'] = ('empty tag', '<${1:name}/>')

xml.cdata = ('CDATA', '<![CDATA[${0:$SELECTION}]]>')
xml.xml = ('xml declaration', '<?xml version="1.0" encoding="UTF-8"?>')

tag = xml.subscope('meta.tag')

tag.a = ('attribute', '${1:name}="$2"')
