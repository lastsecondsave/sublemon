import sys
sys.path.append('../lib')
from snippets import Snippets


java = Snippets('source.java')
java_bl = java.with_braces()
java_par = java.with_selection_in_parentheses()
java_sp = java.with_space()
java_sc = java.with_semicolon()

java_sp.f = 'final'
java_sp.st = 'static'
java_sp.pr = 'private'
java_sp.pu = 'public'
java_sp.pro = 'protected'
java_sp.th = 'throws'

java_sp.im = 'import'
java.ima = ('import *', 'import $0.*;')

java.sf = ('static final CONSTANT', 'static final ${1:String} ${2:CONSTANT} = ${3:null};')
java_sc.con = 'continue'
java.tt = ('this.x = x', 'this.$1 = $1;')

java_sp.ret = 'return'
java_sc.rt = 'return'
java_sc.rtt = 'return this'
java.te = ('throw new Exception();', 'throw new ${1:Exception}($2);')
java.tre = 'throw new RuntimeException($1);'

vv = r'${1:String} ${2:${1/./\l$0/}}'
java.vv = ('variable', vv)
java.vvn = (':new: variable', vv + ' = new $1($3)')
java.vvv = (':value: variable', vv + ' = ${3:null}')

java.pl = 'System.out.println(${0:$SELECTION});'
java.lgg = ('logger', 'private static final Logger log = LoggerFactory.getLogger($FILENAME.class);')

java_sp.List = 'List<${1:String}>'
java_sp.Set = 'Set<${1:String}>'
java_sp.Map = ('Map<>', 'Map<${1:String}, ${2:String}>')

java_sp.Optional = 'Optional<${1:String}>'
java_par.opo = 'Optional.of'
java_par.opn = 'Optional.ofNullable'
java.ope = 'Optional.empty()'

java_par.rnn = 'Objects.requireNonNull'

java.over = '@Override'
java.sw = ('@SuppressWarnings', '@SuppressWarnings("${1:unchecked}")')

java.td = ('TODO', '// TODO: ')

java_bl['if'] = 'if ($1)'
java_bl['else'] = 'else'
java_bl['elif'] = 'else if ($1)'
java_bl['switch'] = 'switch ($1)'
java_bl['while'] = 'while ($1)'

java_bl['for'] = ('for () {}', 'for ($1)')
java_bl.fori = (':i: for () {}', 'for (int ${1:i} = 0; $1 < ${2:imax}; ${3:$1++})')
java_bl.form = (':imax: for () {}', 'for (int ${1:i} = 0, $1max = ${2:count}; $1 < $1max; ${3:$1++})')
java_bl.fore = (':each: for () {}', 'for ($1 : $2)')
java_bl.fort = (':iterator: for () {}', 'for (Iterator<$1> ${2:itr} = ${3:list}.iterator(); $2.hasNext(); )')

java_bl['try'] = 'try'
java_bl.tryr = 'try ($1)'
java_bl['catch'] = 'catch (${1:Exception} e)'
java_bl['finally'] = 'finally'

java_bl.syn = 'synchronized (${1:this})'

java_bl['class'] = 'class ${1:$FILENAME}'
java_bl.interface = 'interface ${1:$FILENAME}'
java_bl.enum = 'enum ${1:$FILENAME}'

java_bl.ctor = ('constructor {}', '$FILENAME($1)')
java_bl.ff = ('method {}', '${1:void} ${2:run}($3)')
java_bl.main = ('main {}', 'public static void main(String[] args)')

getter = r"""
public ${1:String} ${1/boolean|(.*)/(?1:get:is)/}${2/./\u$0/}() {
    return ${2:property};
}
"""

setter = r"""
public void set${2/./\u$0/}(${1:String} ${2/.*/$0/}) {
    this.${2:property} = ${2/.*/$0/};
}
"""

java.get = ('getX() {}', getter)
java.geto = (':optional: getX() {}', getter.replace('public ${1:String}', 'public Optional<${1:String}>'))

java.set = ('setX() {}', setter)

java.gs = ('getX + setX', getter + setter)

java.jd = ('javadoc',
r"""
/**
${SELECTION/^\s*/ * /mg}$0
 */
""")

javadoc = java.subscope('comment.block.documentation.javadoc')
javadoc_sp = javadoc.with_space()

javadoc.code = ('@code', '{@code ${1:$SELECTION}}')
javadoc.link = ('@link', '{@link ${1:$SELECTION}}')
javadoc_sp.par = '@param'
javadoc_sp.ret = '@return'
