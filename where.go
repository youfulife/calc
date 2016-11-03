package main

import (
	"fmt"
)

var boolEBNF = `
<expression>           ::= <term> { OR <term> }
<term>                 ::= <factor> { AND <factor> }
<factor>               ::= <predicate> | NOT <factor> | '(' <expression> ')'
<predicate>            ::= <comp_predicate> | <in_predicate> | <exists_predicate> | <match_predicate>

<comp_predicate>       ::= IDENT <comp_op> NUMBER
<comp_op>              ::= '>' | '<' | '=' | '>=' | '<=' | '!='

<in_predicate>         ::= IDENT [NOT] IN <list>
<list>                 ::= '[' <elements> ']'
<elements>             ::= <element> {',' <element>}
<element>              ::= NUMBER | IDENT

<exists_predicate>     ::= IDENT IS [NOT] NONE

<match_predicate>      ::= IDENT [NOT] MATCH <regexp>
<regexp>               ::= STRING
`

func main() {
	fmt.Println(boolEBNF)
}
