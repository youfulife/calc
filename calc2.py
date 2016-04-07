INTEGER, PLUS, MINUS, EOF = 'INTEGER', 'PLUS', 'MINUS', 'EOF'


class Token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return "Token({type}, {value})".format(type=self.type, value=self.value)

    def __repr__(self):
        return self.__str__()


class Interpreter(object):
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_token = None
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
            self.current_token = Token(EOF, None)
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
            self.error()
        return token

    def eat(self, token_type):
        if token_type == self.current_token.type:
            self.current_token = self.get_next_token()
        else:
            self.error()

    def expr(self):
        self.current_token = self.get_next_token()
        print self.current_token
        left = self.current_token
        self.eat(INTEGER)
        result = left.value
        while self.current_token.type is not EOF:
            op = self.current_token
            if op.type == PLUS:
                self.eat(PLUS)
            else:
                self.eat(MINUS)
            print op
            right = self.current_token
            print self.current_token
            self.eat(INTEGER)

            if op.type == PLUS:
                result += right.value
            else:
                result -= right.value
        print self.current_token
        return result

interpreter = Interpreter(' 40- 15 +1-13+ 2 ')
result = interpreter.expr()
print result