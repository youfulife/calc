package main

import (
	"bufio"
	"bytes"
	"fmt"
	"strconv"
	"strings"
	"unicode"
)

var calcEbnf = `
            expr: term((PLUS|MINUS)term)*
            term: factor((MUL|DIV)factor)*
            factor: NUMBER|LP expr RP|(PLUS|MINUS)factor
            `

type item struct {
	typ itemType
	val string
}

type itemType int

const (
	itemError itemType = iota
	itemEOF

	itemNumber
	itemLp
	itemRp
	itemPlus
	itemMinus
	itemMul
	itemDiv
)

// for debug
var symbols = map[itemType]byte{
	itemLp:    '(',
	itemRp:    ')',
	itemPlus:  '+',
	itemMinus: '-',
	itemMul:   '*',
	itemDiv:   '/',
}

func (i item) String() string {
	switch i.typ {
	case itemEOF:
		return "EOF"
	case itemError:
		return i.val
	}
	if len(i.val) > 10 {
		return fmt.Sprintf("%.10q...", i.val)
	}
	return fmt.Sprintf("%q", i.val)
}

var eof = rune(0)

type lexer struct {
	name  string    // used only for error reports.
	items chan item //channel of scanned item.
	r     *bufio.Reader
}

func newLexer(name, input string) *lexer {
	return &lexer{
		name:  name,
		items: make(chan item, 2),
		r:     bufio.NewReader(strings.NewReader(input)),
	}
}

func (l *lexer) nextItem() item {
	return <-l.items
}

// read reads the next rune from the bufferred reader.
// Returns the rune(0) if an error occurs (or io.EOF is returned).
func (l *lexer) read() rune {
	ch, _, err := l.r.ReadRune()
	if err != nil {
		return eof
	}
	return ch
}

// unread places the previously read rune back on the reader.
func (l *lexer) unread() {
	_ = l.r.UnreadRune()
}

func isSpace(r rune) bool {
	return unicode.IsSpace(r)
}

func isDigit(r rune) bool {
	return unicode.IsDigit(r)
}

func isDot(r rune) bool {
	return r == '.'
}

func (l *lexer) skipSpace() {
	for {
		if ch := l.read(); !isSpace(ch) {
			break
		}
	}
	l.unread()
}

func (l *lexer) lexNumber() {
	var buf bytes.Buffer
	buf.WriteRune(l.read())
	for {
		if ch := l.read(); !isDigit(ch) {
			if isDot(ch) && isDigit(l.read()) {
				buf.WriteRune('.')
				l.unread()
				buf.WriteRune(l.read())
				for {
					if c := l.read(); isDigit(c) {
						buf.WriteRune(c)
					} else {
						break
					}
				}
			}
			break
		} else {
			buf.WriteRune(ch)
		}
	}
	l.unread()
	l.items <- item{itemNumber, buf.String()}
}

func (l *lexer) lex() {
	for {
		ch := l.read()
		if ch == eof {
			break
		}
		if isSpace(ch) {
			l.skipSpace()
		} else if isDigit(ch) {
			l.unread()
			l.lexNumber()
		} else {
			switch ch {
			case '+':
				l.items <- item{itemPlus, string(ch)}
			case '-':
				l.items <- item{itemMinus, string(ch)}
			case '*':
				l.items <- item{itemMul, string(ch)}
			case '/':
				l.items <- item{itemDiv, string(ch)}
			case '(':
				l.items <- item{itemLp, string(ch)}
			case ')':
				l.items <- item{itemRp, string(ch)}
			default:
				l.items <- item{itemError, fmt.Sprintf("Invalid character %q", ch)}
			}
		}
	}
	close(l.items)
}

type parser struct {
	l     *lexer
	token item
}

func newParser(l *lexer) *parser {
	return &parser{
		l:     l,
		token: l.nextItem(),
	}
}

func (p *parser) match(typ itemType) {
	// fmt.Println(p.token)
	if p.token.typ == typ {
		p.token = p.l.nextItem()
	} else {
		fmt.Printf("expecting %q but got %q", symbols[typ], p.token)
	}
}

func (p *parser) parse() *node {
	return p.expr()
}

func (p *parser) expr() *node {
	node := p.term()
	for p.token.typ == itemPlus || p.token.typ == itemMinus {
		token := p.token
		if p.token.typ == itemPlus {
			p.match(itemPlus)
		} else if p.token.typ == itemMinus {
			p.match(itemMinus)
		}
		node = newNode(token, node, p.term())
	}
	return node
}

func (p *parser) term() *node {
	node := p.factor()
	for p.token.typ == itemMul || p.token.typ == itemDiv {
		token := p.token
		if p.token.typ == itemMul {
			p.match(itemMul)
		} else if p.token.typ == itemDiv {
			p.match(itemDiv)
		}
		node = newNode(token, node, p.factor())
	}
	return node
}

func (p *parser) factor() *node {
	token := p.token
	if token.typ == itemNumber {
		p.match(itemNumber)
		return newNode(token, nil, nil)
	} else if token.typ == itemLp {
		p.match(itemLp)
		node := p.expr()
		p.match(itemRp)
		return node
	} else if token.typ == itemPlus || token.typ == itemMinus {
		if token.typ == itemPlus {
			p.match(itemPlus)
		} else if token.typ == itemMinus {
			p.match(itemMinus)
		}
		node := p.factor()
		return newNode(token, newNode(item{itemNumber, "0"}, nil, nil), node)
	}
	return nil
}

type node struct {
	tok   item
	left  *node
	right *node
}

func newNode(i item, l *node, r *node) *node {
	return &node{
		tok:   i,
		left:  l,
		right: r,
	}
}

func (n *node) walk() float64 {
	// fmt.Println(n.tok)
	switch n.tok.typ {
	case itemPlus:
		return n.left.walk() + n.right.walk()
	case itemMinus:
		return n.left.walk() - n.right.walk()
	case itemMul:
		return n.left.walk() * n.right.walk()
	case itemDiv:
		return n.left.walk() / n.right.walk()
	case itemNumber:
		f, _ := strconv.ParseFloat(n.tok.val, 64)
		return f
	default:
		fmt.Println("AST error")
	}
	return 0
}

type interpreter struct {
	p    *parser
	tree *node
}

func newInterpreter(p *parser) *interpreter {
	return &interpreter{
		p:    p,
		tree: p.parse(),
	}
}

func (i *interpreter) interpret() float64 {
	return i.tree.walk()
}

func main() {
	s := "-+-(--(---7+++1)) + 3 * (10 / (12 / (3 + 1) - 1)) / (2 + 3) - 5 - 3 + (8.5)"
	l := newLexer("test", s)
	go l.lex()
	p := newParser(l)
	i := newInterpreter(p)
	r := i.interpret()
	fmt.Println(r)
}
