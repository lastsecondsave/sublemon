import sys
sys.path.append('../lib')
from snippets import Snippets

FILENAME = r'${TM_FILENAME/(.*?)(\..+)/$1/}'

java = Snippets('source.java')
pre = java.with_suffix(' ')
bl = java.with_suffix(' {\n\t$0\n}')
javadoc = java.subscope('comment.block.documentation.javadoc')

pre.f = 'final'
pre.st = 'static'
pre.pr = 'private'
pre.pu = 'public'
pre.pro = 'protected'
pre.th = 'throws'

pre.im = 'import'
java.ima = ('import *', 'import $0.*;')

java.sf = ('static final CONSTANT', 'static final ${1:String} ${2:CONSTANT} = ${3:null};')
java.con = ('continue', 'continue;')
java.this = ('this.x = x', 'this.$1 = $1;')

pre.ret = 'return'
java.rtt = ('return this', 'return this;')
java.te = ('throw new Exception', 'throw new ${1:Exception}($2);')

java.vv = ('variable', '${1:String} ${2:${1/./\l$0/}}')
java.varn = ('variable new', '${1:String} ${2:${1/./\l$0/}} = new $1($3)')
java.varv = ('variable with value', '${1:String} ${2:${1/./\l$0/}} = ${3:null}')

java.pl = ('println', 'System.out.println(${0:$SELECTION});')
java.lgg = ('logger', 'private static final Logger log = LoggerFactory.getLogger(' + FILENAME + '.class);')

pre.List = ('List<>', 'List<${1:String}>')
pre.Set = ('Set<>', 'Set<${1:String}>')
pre.Map = ('Map<>', 'Map<${1:String}, ${2:String}>')

pre.Optional = ('Optional<>', 'Optional<${1:String}>')
java.opo = ('Optional.of()', 'Optional.of(${0:$SELECTION})')
java.opn = ('Optional.ofNullable()', 'Optional.ofNullable(${0:$SELECTION})')

java.over = '@Override'
java.sw = ('@SuppressWarnings', '@SuppressWarnings("${1:unchecked}")')

javadoc['@code'] = ('@code', '{@code ${1:$SELECTION}}$0')
javadoc['@link'] = ('@link', '{@link ${1:$SELECTION}}$0')

java.td = ('TODO', '// TODO: ')
java.fm = ('FIXME', '// FIXME: ')

bl['if'] = ('if', 'if ($1)')
bl['else'] = 'else'
bl['elif'] = ('else if', 'else if ($1)')
bl['switch'] = ('switch', 'switch ($1)')
bl['while'] = ('while', 'while ($1)')

bl['for'] = ('for', 'for ($1; $2; $3)')
bl['fore'] = ('for each', 'for ($1 : $2)')
bl['fori'] = ('for i', 'for (int ${1:i} = 0; $1 < ${2:imax}; ${3:$1++})')
bl['form'] = ('for imax', 'for (int ${1:i} = 0, $1max = ${2:count}; $1 < $1max; ${3:$1++})')
bl['fort'] = ('for iterator', 'for (Iterator<$1> ${2:itr} = ${3:list}.iterator(); $2.hasNext(); )')
bl['try'] = 'try'
bl['trr'] = ('try with resources', 'try ($1)')
bl['catch'] = ('catch', 'catch (${1:Exception} e)')
bl['finally'] = 'finally'

bl.syn = ('synchronized', 'synchronized (${1:this})')

bl['class'] = ('class', 'class ${1:' + FILENAME + '}')
bl['interface'] = ('interface', 'interface ${1:' + FILENAME + '}')
bl['enum'] = ('enum', 'enum ${1:' + FILENAME + '}')

bl.ctor = ('constructor', FILENAME + '($1)')
bl.ff = ('method', '${1:void} ${2:run}($3)')
bl.main = ('main', 'public static void main(String[] args)')

java.jd = ('javadoc',
r"""
/**
${SELECTION/^\s*/ * /mg}$0
 */
""")

java.get = ('getter',
r"""
public ${1:String} ${1/boolean|(.*)/(?1:get:is)/}${2/./\u$0/}() {
    return ${2:property};
}
""")

java.set = ('setter',
r"""
public void set${2/./\u$0/}(${1:String} ${2/.*/$0/}) {
    this.${2:property} = ${2/.*/$0/};
}
""")

java.gs = ('getter-setter',
r"""
public ${1:String} ${1/boolean|(.*)/(?1:get:is)/}${2/./\u$0/}() {
    return ${2:property};
}

public void set${2/./\u$0/}(${1/.*/$0/} ${2/.*/$0/}) {
    this.${2/.*/$0 = $0/};
}
""")
