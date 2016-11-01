package main

import (
	"bufio"
	"bytes"
	"fmt"
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
	fmt.Println(p.token)
	if p.token.typ == typ {
		p.token = p.l.nextItem()
	} else {
		fmt.Printf("expecting %q but got %q", symbols[typ], p.token)
	}
}

func (p *parser) parse() {
	p.expr()
}

func (p *parser) expr() {
	p.term()
	for p.token.typ == itemPlus || p.token.typ == itemMinus {
		if p.token.typ == itemPlus {
			p.match(itemPlus)
		} else if p.token.typ == itemMinus {
			p.match(itemMinus)
		}
		p.term()
	}
}

func (p *parser) term() {
	p.factor()
	for p.token.typ == itemMul || p.token.typ == itemDiv {
		if p.token.typ == itemMul {
			p.match(itemMul)
		} else if p.token.typ == itemDiv {
			p.match(itemDiv)
		}
		p.factor()
	}
}

func (p *parser) factor() {
	if p.token.typ == itemNumber {
		p.match(itemNumber)
	} else if p.token.typ == itemLp {
		p.match(itemLp)
		p.expr()
		p.match(itemRp)
	} else if p.token.typ == itemPlus || p.token.typ == itemMinus {
		if p.token.typ == itemPlus {
			p.match(itemPlus)
		} else if p.token.typ == itemMinus {
			p.match(itemMinus)
		}
		p.factor()
	}
}

func main() {
	s := "-+-(--(---7+++1)) + 3 * (10 / (12 / (3 + 1) - 1)) / (2 + 3) - 5 - 3 + (8)"
	l := newLexer("test", s)
	go l.lex()
	p := newParser(l)
	p.parse()
}
