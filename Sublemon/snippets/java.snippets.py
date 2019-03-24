from snippets import *

java = Snippets('source.java')

java/spc/'f' - 'final'
java/spc/'st' - 'static'
java/spc/'pr' - 'private'
java/spc/'pu' - 'public'
java/spc/'pro' - 'protected'
java/spc/'th' - 'throws'

java/spc/'im' - 'import'
java/'ima' - ('import *', 'import $0.*;')

java/'sf' - ('static final CONSTANT', 'static final ${1:String} ${2:CONSTANT} = ${3:null};')
java/scl/'con' - 'continue'
java/'tt' - ('this.x = x', 'this.$1 = $1;')

java/spc/'ret' - 'return'
java/scl/'rtt' - 'return this'
java/'te' - ('throw new Exception();', 'throw new ${1:Exception}($2);')
java/'tre' - 'throw new RuntimeException($1);'

vv = r'${1:String} ${2:${1/./\l$0/}}'
java/'vv' - ('variable', vv)
java/'vvn' - (':new: variable', vv + ' = new $1($3)')
java/'vvv' - (':value: variable', vv + ' = ${3:null}')

java/'pl' - 'System.out.println(${0:$SELECTION});'
java/'lgg' - ('logger', 'private static final Logger log = LoggerFactory.getLogger($FILENAME.class);')

java/spc/'List' - 'List<${1:String}>'
java/spc/'Set' - 'Set<${1:String}>'
java/spc/'Map' - ('Map<>', 'Map<${1:String}, ${2:String}>')

java/spc/'Optional' - 'Optional<${1:String}>'
java/slp/'opo' - 'Optional.of'
java/slp/'opn' - 'Optional.ofNullable'
java/'ope' - 'Optional.empty()'

java/slp/'rnn' - 'Objects.requireNonNull'

java/'over' - '@Override'
java/'sw' - ('@SuppressWarnings', '@SuppressWarnings("${1:unchecked}")')

java/'td' - ('TODO', '// TODO: ')

java/blk/'if' - 'if ($1)'
java/blk/'else' - 'else'
java/blk/'elif' - 'else if ($1)'
java/blk/'switch' - 'switch ($1)'
java/blk/'while' - 'while ($1)'

java/blk/'for' - ('for () {}', 'for ($1)')
java/blk/'fori' - (':i: for () {}', 'for (int ${1:i} = 0; $1 < ${2:imax}; ${3:$1++})')
java/blk/'form' - (':imax: for () {}', 'for (int ${1:i} = 0, $1max = ${2:count}; $1 < $1max; ${3:$1++})')
java/blk/'fore' - (':each: for () {}', 'for ($1 : $2)')
java/blk/'fort' - (':iterator: for () {}', 'for (Iterator<$1> ${2:itr} = ${3:list}.iterator(); $2.hasNext(); )')

java/blk/'try' - 'try'
java/blk/'tryr' - 'try ($1)'
java/blk/'catch' - 'catch (${1:Exception} e)'
java/blk/'finally' - 'finally'

java/blk/'syn' - 'synchronized (${1:this})'

java/blk/'class' - 'class ${1:$FILENAME}'
java/blk/'interface' - 'interface ${1:$FILENAME}'
java/blk/'enum' - 'enum ${1:$FILENAME}'

java/blk/'ctor' - ('constructor {}', '$FILENAME($1)')
java/blk/'ff' - ('method {}', '${1:void} ${2:run}($3)')
java/blk/'main' - ('main {}', 'public static void main(String[] args)')

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

java/'get' - ('getX() {}', getter)
java/'geto' - (':optional: getX() {}', getter.replace('public ${1:String}', 'public Optional<${1:String}>'))

java/'set' - ('setX() {}', setter)

java/'gs' - ('getX + setX', getter + setter)

java/ind/'jd' - ('javadoc', r'/**||${SELECTION/^\s*/ * /mg}$0|| */')

javadoc = java.subscope('comment.block.documentation.javadoc')

javadoc/'code' - ('@code', '{@code ${1:$SELECTION}}')
javadoc/'link' - ('@link', '{@link ${1:$SELECTION}}')
javadoc/spc/'par' - '@param'
javadoc/spc/'ret' - '@return'
