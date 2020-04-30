from snippets_lib import *

rs = Snippets("source.rust")

rs/'pl' - 'println!("{}", ${0:$SELECTION});'
rs/blk/'fn' - 'fn ${1:run} ($2)'
