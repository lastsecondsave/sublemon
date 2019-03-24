from snippets import *

xml = Snippets('text.xml')
tag = xml.subscope('meta.tag')

xml/'<' - ('tag', '<${1:p}>${2:$SELECTION}</${1/([^ ]+).*/$1/}>')
xml/'>' - ('empty tag', '<${1:name}/>')

xml/'cdata' - ('CDATA', '<![CDATA[${0:$SELECTION}]]>')
xml/'xml' - ('xml declaration', '<?xml version="1.0" encoding="UTF-8"?>')

tag/'a' - ('attribute', '${1:name}="$2"')
