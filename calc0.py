INTEGER = "INTEGER"
PLUS, MINUS, MUL, DIV, EOF = "PLUS", "MINUS", "MUL", "DIV", "EOF"
LPAREN, RPAREN = "LPAREN", "RPAREN"

class Token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return "Token({0}, {1})".format(self.type, repr(self.value))

    def __repr__(self):
        return self.__str__()


class Lexer(object):
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_token = None

    def skip_whitespace(self):
        while self.pos < len(self.text) and self.text[self.pos].isspace():
            self.pos += 1

    def integer(self):
        start = self.pos
        while self.pos < len(self.text) and self.text[self.pos].isdigit():
            self.pos += 1
        return int(self.text[start:self.pos])

    def error(self):
        raise Exception('Invalid character')

    def get_next_token(self):
        text = self.text
        self.skip_whitespace()
        if self.pos > len(text) - 1:
            return Token(EOF, None)

        current_char = text[self.pos]

        if current_char.isdigit():
            return Token(INTEGER, self.integer())
        if current_char == '+':
            self.pos += 1
            return Token(PLUS, '+')
        if current_char == '-':
            self.pos += 1
            return Token(MINUS, '-')
        if current_char == '*':
            self.pos += 1
            return Token(MUL, '*')
        if current_char == '/':
            self.pos += 1
            return Token(DIV, '/')
        if current_char == '(':
            self.pos += 1
            return Token(LPAREN, '(')
        if current_char == ')':
            self.pos += 1
            return Token(RPAREN, ')')
        self.error()


class AST(object):
    pass


class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right


class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class Parser(object):
    """
    expr: term((PLUS|MINUS)term)*
    term: factor((MUL|DIV)factor)*
    factor: INTEGER | LPAREN expr RPAREN
    """

    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception("Invalid syntax")

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def factor(self):
        token = self.current_token
        if token.type == INTEGER:
            self.eat(INTEGER)
            return Num(token)
        elif token.type == LPAREN:
            self.eat(LPAREN)
            node = self.expr()
            self.eat(RPAREN)
            return node

    def term(self):
        node = self.factor()
        while self.current_token.type in (MUL, DIV):
            op = self.current_token
            if op.type == MUL:
                self.eat(MUL)
            elif op.type == DIV:
                self.eat(DIV)
            node = BinOp(left=node, op=op, right=self.factor())
        return node

    def expr(self):
        node = self.term()
        while self.current_token.type in (PLUS, MINUS):
            op = self.current_token
            if op.type == PLUS:
                self.eat(PLUS)
            elif op.type == MINUS:
                self.eat(MINUS)
            node = BinOp(left=node, op=op, right=self.term())
        return node

    def parse(self):
        return self.expr()


if __name__ == "__main__":
    lexer = Lexer("2 * 7 + 3")
    parser = Parser(lexer)
    print parser.parse()
