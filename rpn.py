import unittest
from calc0 import Token, Lexer

INTEGER = "INTEGER"
PLUS, MINUS, MUL, DIV, EOF = "PLUS", "MINUS", "MUL", "DIV", "EOF"
LPAREN, RPAREN = "LPAREN", "RPAREN"


class Node(object):
    def __init__(self, token, left, right):
        self.token = token
        self.left = left
        self.right = right


class Parser(object):
    """
    expr: term((PLUS|MINUS)term)*
    term: factor((MUL|DIV)factor)*
    factor: INTEGER|LP expr RP
    """
    def __init__(self, lexer):
        self.lexer = lexer
        self.token = self.lexer.get_next_token()

    def error(self):
        raise Exception("parsing error")

    def eat(self, token_type):
        if self.token.type == token_type:
            self.token = self.lexer.get_next_token()
        else:
            print token_type
            print self.token
            self.error()

    def expr(self):
        node = self.term()
        while self.token.type in (PLUS, MINUS):
            op = self.token
            if op.type == PLUS:
                self.eat(PLUS)
            elif op.type == MINUS:
                self.eat(MINUS)
            node = Node(op, node, self.term())
        return node

    def term(self):
        node = self.factor()
        while self.token.type in (MUL, DIV):
            op = self.token
            if op.type == MUL:
                self.eat(MUL)
            elif op.type == DIV:
                self.eat(DIV)
            node = Node(op, node, self.factor())
        return node

    def factor(self):
        if self.token.type == INTEGER:
            node = Node(self.token, None, None)
            self.eat(INTEGER)
            return node
        elif self.token.type == LPAREN:
            self.eat(LPAREN)
            node = self.expr()
            self.eat(RPAREN)
            return node

    def parse(self):
        return self.expr()

def visit(tree):
    if tree.left:
        visit(tree.left)
    if tree.right:
        visit(tree.right)
    stack.append(tree.token.value)

stack = []
def infix2postfix(s):
    global stack
    lexer = Lexer(s)
    parser = Parser(lexer)
    tree = parser.parse()
    visit(tree)
    rpn = ' '.join(map(str, stack))
    stack = []
    return rpn

class Infix2PostfixTestCase(unittest.TestCase):

    def test_1(self):
        self.assertEqual(infix2postfix('2 + 3'), '2 3 +')

    def test_2(self):
        self.assertEqual(infix2postfix('2 + 3 * 5'), '2 3 5 * +')

    def test_3(self):
        self.assertEqual(
            infix2postfix('5 + ((1 + 2) * 4) - 3'),
            '5 1 2 + 4 * + 3 -',
        )

    def test_4(self):
        self.assertEqual(
            infix2postfix('(5 + 3) * 12 / 3'),
            '5 3 + 12 * 3 /',
        )

if __name__ == "__main__":
    unittest.main()
