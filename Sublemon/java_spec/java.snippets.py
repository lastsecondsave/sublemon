import sys
sys.path.append('../lib')
from snippets import setup, scope, snippet

setup()

scope('source.java')

## KEYWORDS ##

snippet(tabTrigger='f',   content='final ')
snippet(tabTrigger='st',  content='static ')
snippet(tabTrigger='pr',  content='private ')
snippet(tabTrigger='pu',  content='public ')
snippet(tabTrigger='pro', content='protected ')

snippet(tabTrigger='im', content='import ')

snippet(tabTrigger='th',  content='throws ')
snippet(tabTrigger='ret', content='return ')

## ONE-LINERS ##

snippet(tabTrigger='const', description='static final CONSTANT', content=
'static final ${1:String} ${2:CONSTANT} = ${3:null};'
)

snippet(tabTrigger='con', description='continue', content=
'continue;'
)

snippet(tabTrigger='this', description='this.x = x', content=
'this.$1 = $1;'
)

snippet(tabTrigger='rtt', description='return this', content=
'return this;'
)

snippet(tabTrigger='vv', description='variable', content=
'${1:String} ${2:${1/./\l$0/}}'
)

snippet(tabTrigger='varn', description='variable new', content=
'${1:String} ${2:${1/./\l$0/}} = new $1($3)'
)

snippet(tabTrigger='varv', description='variable with value', content=
'${1:String} ${2:${1/./\l$0/}} = ${3:null}'
)

snippet(tabTrigger='te', description='throw new Exception', content=
'throw new ${1:Exception}($2);'
)

snippet(tabTrigger='pl', description='println', content=
'System.out.println(${0:$SELECTION});'
)

snippet(tabTrigger='log', description='logger', content=
r'private static final Logger LOG = LoggerFactory.getLogger(${1:${TM_FILENAME/(.*?)(\..+)/$1/}}.class);'
)

snippet(tabTrigger='List', description='List<>', content=
'List<${1:String}> '
)

snippet(tabTrigger='Set', description='Set<>', content=
'Set<${1:String}> '
)

snippet(tabTrigger='Map', description='Map<>', content=
'Map<${1:String}, ${2:String}> '
)

snippet(tabTrigger='over', description='@Override', content=
'@Override'
)

snippet(tabTrigger='sw', description='@SuppressWarnings', content=
'@SuppressWarnings("${1:unchecked}")'
)

snippet(tabTrigger='code', description='@code', scope='comment.block.documentation.javadoc', content=
'{@code ${1:$SELECTION}}$0'
)

snippet(tabTrigger='link', description='@link', scope='comment.block.documentation.javadoc', content=
'{@link ${1:$SELECTION}}$0'
)

snippet(tabTrigger='td', description='TODO', content=
'// TODO: '
)

snippet(tabTrigger='ima', description='import *', content=
'import ${0}.*;'
)

## BLOCKS ##

snippet(tabTrigger='if', description='if', content=
"""
if ($1) {
    $0
}
""")

snippet(tabTrigger='else', description='else', content=
"""
else {
    $0
}
""")

snippet(tabTrigger='elif', description='else if', content=
"""
else if ($1) {
    $0
}
""")

snippet(tabTrigger='switch', description='switch', content=
"""
switch ($1) {
    $0
}
""")

snippet(tabTrigger='while', description='while', content=
"""
while ($1) {
    $0
}
""")

snippet(tabTrigger='for', description='for', content=
"""
for ($1; $2; $3) {
    $0
}
""")

snippet(tabTrigger='fore', description='for each', content=
"""
for ($1 : $2) {
    $0
}
""")

snippet(tabTrigger='fori', description='for i', content=
"""
for (int ${1:i} = 0; $1 < ${2:imax}; ${3:$1++}) {
    $0
}
""")

snippet(tabTrigger='form', description='for imax', content=
"""
for (int ${1:i} = 0, $1max = ${2:count}; $1 < $1max; ${3:$1++}) {
    $0
}
""")

snippet(tabTrigger='fort', description='for iterator', content=
"""
for (Iterator<$1> ${2:itr} = ${3:list}.iterator(); $2.hasNext(); ) {
    $0
}
""")

snippet(tabTrigger='try', description='try', content=
"""
try {
    $0
}
""")

snippet(tabTrigger='tryr', description='try with resources', content=
"""
try ($1) {
    $0
}
""")

snippet(tabTrigger='catch', description='catch', content=
"""
catch (${1:Exception} e) {
    $0
}
""")

snippet(tabTrigger='finally', description='finally', content=
"""
finally {
    $0
}
""")

snippet(tabTrigger='syn', description='synchronized', content=
"""
synchronized (${1:this}) {
    $0
}
""")

## GISTS ##

snippet(tabTrigger='class', description='class', content=
r"""
class ${1:${TM_FILENAME/(.*?)(\..+)/$1/}} {
    $0
}
""")

snippet(tabTrigger='interface', description='interface', content=
r"""
interface ${1:${TM_FILENAME/(.*?)(\..+)/$1/}} {
    $0
}
""")

snippet(tabTrigger='ctor', description='constructor', content=
r"""
${TM_FILENAME/(.*?)(\..+)/$1/}($1) {
    $0
}
""")

snippet(tabTrigger='ff', description='method', content=
"""
${1:void} ${2:run}($3) {
    $0
}
""")

snippet(tabTrigger='main', description='main', content=
r"""
public static void main(String[] args) {
    $0
}
""")

snippet(tabTrigger='jd', description='javadoc', content=
r"""
/**
${SELECTION/^\s*/ * /mg}$0
 */
""")

snippet(tabTrigger='get', description='getter', content=
r"""
public ${1:String} ${1/boolean|(.*)/(?1:get:is)/}${2/./\u$0/}() {
    return ${2:property};
}
""")

snippet(tabTrigger='set', description='setter', content=
r"""
public void set${2/./\u$0/}(${1:String} ${2/.*/$0/}) {
    this.${2:property} = ${2/.*/$0/};
}
""")

snippet(tabTrigger='gs', description='getter-setter', content=
r"""
public ${1:String} ${1/boolean|(.*)/(?1:get:is)/}${2/./\u$0/}() {
    return ${2:property};
}

public void set${2/./\u$0/}(${1/.*/$0/} ${2/.*/$0/}) {
    this.${2/.*/$0 = $0/};
}
""")
