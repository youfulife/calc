INTEGER, EOF = 'INTEGER', 'EOF'
PLUS, MINUS, MUL, DIV = 'PLUS', 'MINUS', 'MUL', 'DIV'
LP, RP = 'LP', 'RP'


class Token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return "Token({type}, {value})".format(
            type=self.type,
            value=self.value
        )

    def __repr__(self):
        return self.__str__()


class Lexer(object):
    def __init__(self, text):
        self.text = text
        self.pos = 0

    def skip_whitespace(self):
        while self.pos < len(self.text) and self.text[self.pos].isspace():
            self.pos += 1

    def integer(self):
        start = self.pos
        while self.pos < len(self.text) and self.text[self.pos].isdigit():
            self.pos += 1
        return int(self.text[start:self.pos])

    def error(self):
        raise Exception("lexer error")

    def get_next_token(self):
        self.skip_whitespace()
        if self.pos >= len(self.text):
            return Token(EOF, 'EOF')
        if self.text[self.pos].isdigit():
            return Token(INTEGER, self.integer())
        if self.text[self.pos] == '+':
            self.pos += 1
            return Token(PLUS, 'PLUS')
        if self.text[self.pos] == '-':
            self.pos += 1
            return Token(MINUS, 'MINUS')
        if self.text[self.pos] == '*':
            self.pos += 1
            return Token(MUL, 'MUL')
        if self.text[self.pos] == '/':
            self.pos += 1
            return Token(DIV, 'DIV')
        if self.text[self.pos] == '(':
            self.pos += 1
            return Token(LP, 'LP')
        if self.text[self.pos] == ')':
            self.pos += 1
            return Token(RP, 'RP')
        return error()


class AST(object):
    pass


class BinOP(AST):
    def __init__(self, token, left, right):
        self.token = token
        self.op = token
        self.left = left
        self.right = right


class UnaryOP(AST):
    def __init__(self, token, expr):
        self.token = token
        self.op = token
        self.expr = expr


class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class Parser(object):
    """
    expr: term((PLUS|MINUS)term)*
    term: factor((MUL|DIV)factor)*
    factor: INTEGER|LP expr RP|(PLUS|MINUS)expr
    """
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = lexer.get_next_token()

    def error(self):
        raise Exception("parser error")

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
        elif token.type == LP:
            self.eat(LP)
            node = self.expr()
            self.eat(RP)
            return node
        elif token.type in (PLUS, MINUS):
            self.eat(token.type)
            return UnaryOP(token, self.expr())

    def term(self):
        node = self.factor()
        while self.current_token.type in (MUL, DIV):
            op = self.current_token
            self.eat(op.type)
            node = BinOP(op, node, self.factor())
        return node

    def expr(self):
        node = self.term()
        while self.current_token.type in (PLUS, MINUS):
            op = self.current_token
            self.eat(op.type)
            node = BinOP(op, node, self.term())
        return node

    def parse(self):
        return self.expr()


class Visitor(object):
    def __init__(self):
        pass

    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self):
        raise Exception("No visit_{} method".format(type(node).__name__))


class Interpreter(Visitor):
    def __init__(self, parser):
        self.parser = parser
        self.tree = self.parser.parse()

    def visit_BinOP(self, node):
        if node.op.type == PLUS:
            return self.visit(node.left) + self.visit(node.right)
        if node.op.type == MINUS:
            return self.visit(node.left) - self.visit(node.right)
        if node.op.type == MUL:
            return self.visit(node.left) * self.visit(node.right)
        if node.op.type == DIV:
            return self.visit(node.left) / self.visit(node.right)

    def visit_Num(self, node):
        return node.value

    def visit_UnaryOP(self, node):
        if node.op.type == PLUS:
            return +self.visit(node.expr)
        if node.op.type == MINUS:
            return -self.visit(node.expr)

    def interpret(self):
        return self.visit(self.tree)


if __name__ == '__main__':
    s = "-+-(--(---7+++1)) + 3 * (10 / (12 / (3 + 1) - 1)) / (2 + 3) - 5 - 3 + (8)"
    lexer = Lexer(s)
    parser = Parser(lexer)
    interpreter = Interpreter(parser)
    result = interpreter.interpret()
    print result
    print eval(s)
