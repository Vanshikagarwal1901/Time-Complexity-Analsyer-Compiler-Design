import re

try:
    from .constants import KEYWORDS, OPERATORS, PUNCTUATORS
    from .token import Token
except ImportError:
    from constants import KEYWORDS, OPERATORS, PUNCTUATORS
    from token import Token


class Lexer:
    def __init__(self, source_code):
        self.code = source_code
        self.position = 0
        self.line = 1
        self.tokens = []

    def peek(self, offset=0):
        if self.position + offset < len(self.code):
            return self.code[self.position + offset]
        return None

    def advance(self):
        char = self.code[self.position]
        self.position += 1
        if char == "\n":
            self.line += 1
        return char

    def tokenize(self):
        while self.position < len(self.code):
            char = self.peek()

            if char.isspace():
                self.advance()
                continue

            if char == "/" and self.peek(1) == "/":
                while self.peek() and self.peek() != "\n":
                    self.advance()
                continue

            if char == "/" and self.peek(1) == "*":
                self.advance()
                self.advance()
                while self.peek() and not (self.peek() == "*" and self.peek(1) == "/"):
                    self.advance()
                self.advance()
                self.advance()
                continue

            if char == "#":
                value = ""
                while self.peek() and self.peek() != "\n":
                    value += self.advance()
                self.tokens.append(Token("PREPROCESSOR", value.strip(), self.line))
                continue

            if char == '"':
                value = self.advance()
                while self.peek() and self.peek() != '"':
                    if self.peek() == "\\":
                        value += self.advance()
                    value += self.advance()
                value += self.advance()
                self.tokens.append(Token("STRING_LITERAL", value, self.line))
                continue

            if char == "'":
                value = self.advance()
                while self.peek() and self.peek() != "'":
                    value += self.advance()
                value += self.advance()
                self.tokens.append(Token("CHAR_LITERAL", value, self.line))
                continue

            if char.isalpha() or char == "_":
                value = ""
                while self.peek() and (self.peek().isalnum() or self.peek() == "_"):
                    value += self.advance()

                if value in KEYWORDS:
                    self.tokens.append(Token("KEYWORD", value, self.line))
                else:
                    self.tokens.append(Token("IDENTIFIER", value, self.line))
                continue

            if char.isdigit():
                value = ""
                while self.peek() and (self.peek().isalnum() or self.peek() in ".xX"):
                    value += self.advance()

                if re.match(r"^0[xX][0-9a-fA-F]+$", value):
                    self.tokens.append(Token("INTEGER_LITERAL", value, self.line))
                elif re.match(r"^[0-9]+\.[0-9]*([eE][+-]?[0-9]+)?$", value):
                    self.tokens.append(Token("FLOAT_LITERAL", value, self.line))
                else:
                    self.tokens.append(Token("INTEGER_LITERAL", value, self.line))
                continue

            matched = False
            for op in OPERATORS:
                if self.code.startswith(op, self.position):
                    self.tokens.append(Token("OPERATOR", op, self.line))
                    self.position += len(op)
                    matched = True
                    break
            if matched:
                continue

            if char in PUNCTUATORS:
                self.tokens.append(Token("PUNCTUATOR", self.advance(), self.line))
                continue

            self.tokens.append(Token("UNKNOWN", self.advance(), self.line))

        return self.tokens
