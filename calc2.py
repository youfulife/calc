INTEGER, PLUS, MINUS, MUL, DIV, EOF = 'INTEGER', 'PLUS', 'MINUS', 'MUL', 'DIV', 'EOF'


class Token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return "Token({type}, {value})".format(type=self.type, value=self.value)

    def __repr__(self):
        return self.__str__()


class Lexer(object):
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def error(self):
        print self.pos
        raise Exception('Error parsing input')

    def int_token(self):
        token_start = self.pos
        while self.current_char is not None and self.current_char.isdigit():
            self.advance()
        token = Token(INTEGER, int(self.text[token_start:self.pos]))
        return token

    def advance(self):
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def get_next_token(self):
        token = Token(EOF, None)
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            if self.current_char.isdigit():
                token = self.int_token()
                break
            if self.current_char == '+':
                token = Token(PLUS, '+')
                self.advance()
                break
            if self.current_char == '-':
                token = Token(MINUS, '-')
                self.advance()
                break
            if self.current_char == '*':
                token = Token(MUL, '*')
                self.advance()
                break
            if self.current_char == '/':
                token = Token(DIV, '/')
                self.advance()
                break
            self.error()
        return token


class Interpreter(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception("Invalid syntax")

    def eat(self, type):
        if type == self.current_token.type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def factor(self):
        token = self.current_token
        self.eat(INTEGER)
        return token.value

    def term(self):
        result = self.factor()
        while self.current_token.type in (MUL, DIV):
            if self.current_token.type == MUL:
                self.eat(MUL)
                result *= self.factor()
            elif self.current_token.type == DIV:
                self.eat(DIV)
                result /= self.factor()
        return result

    def expr(self):
        result = self.term()
        while self.current_token.type in (PLUS, MINUS):
            if self.current_token.type == PLUS:
                self.eat(PLUS)
                result += self.term()
            elif self.current_token.type == MINUS:
                self.eat(MINUS)
                result -= self.term()

        return result


lexer = Lexer('3+1*5*2/2')
interpreter = Interpreter(lexer)
result = interpreter.expr()
print result