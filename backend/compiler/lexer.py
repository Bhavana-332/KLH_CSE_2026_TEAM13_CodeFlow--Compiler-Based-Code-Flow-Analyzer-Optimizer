"""
Lexical Analyzer (Lexer)
-------------------------
Converts raw source text into a flat stream of Token objects.

Compiler Design concept: LEXICAL ANALYSIS
This is the first phase of the pipeline. It groups characters of the
source program into the smallest meaningful units ("lexemes") and
classifies each one into a token type, discarding whitespace and
comments along the way.
"""

from .errors import LexerError

KEYWORDS = {
    "int": "INT",
    "if": "IF",
    "else": "ELSE",
    "while": "WHILE",
    "print": "PRINT",
}

# Multi-character operators must be checked before single-character ones.
SYMBOLS = [
    ("==", "EQ"),
    ("!=", "NE"),
    (">=", "GE"),
    ("<=", "LE"),
    ("+", "PLUS"),
    ("-", "MINUS"),
    ("*", "STAR"),
    ("/", "SLASH"),
    ("=", "ASSIGN"),
    (">", "GT"),
    ("<", "LT"),
    ("(", "LPAREN"),
    (")", "RPAREN"),
    ("{", "LBRACE"),
    ("}", "RBRACE"),
    (";", "SEMI"),
]


class Token:
    __slots__ = ("type", "value", "line", "col")

    def __init__(self, type_, value, line, col):
        self.type = type_
        self.value = value
        self.line = line
        self.col = col

    def to_dict(self):
        return {
            "type": self.type,
            "value": self.value,
            "line": self.line,
            "col": self.col,
        }

    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, line={self.line})"


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1
        self.length = len(source)

    def _peek(self, offset=0):
        idx = self.pos + offset
        if idx < self.length:
            return self.source[idx]
        return ""

    def _advance(self):
        ch = self.source[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def _skip_whitespace_and_comments(self):
        while self.pos < self.length:
            ch = self._peek()
            if ch in " \t\r\n":
                self._advance()
            elif ch == "/" and self._peek(1) == "/":
                while self.pos < self.length and self._peek() != "\n":
                    self._advance()
            elif ch == "/" and self._peek(1) == "*":
                self._advance()
                self._advance()
                while self.pos < self.length and not (
                    self._peek() == "*" and self._peek(1) == "/"
                ):
                    self._advance()
                if self.pos < self.length:
                    self._advance()
                    self._advance()
                else:
                    raise LexerError("Unterminated block comment", self.line)
            else:
                break

    def tokenize(self):
        tokens = []
        while True:
            self._skip_whitespace_and_comments()
            if self.pos >= self.length:
                tokens.append(Token("EOF", "", self.line, self.col))
                break

            ch = self._peek()
            start_line, start_col = self.line, self.col

            if ch.isdigit():
                num = ""
                while self.pos < self.length and self._peek().isdigit():
                    num += self._advance()
                if self._peek() == ".":
                    num += self._advance()
                    while self.pos < self.length and self._peek().isdigit():
                        num += self._advance()
                tokens.append(Token("NUMBER", num, start_line, start_col))
                continue

            if ch.isalpha() or ch == "_":
                ident = ""
                while self.pos < self.length and (
                    self._peek().isalnum() or self._peek() == "_"
                ):
                    ident += self._advance()
                token_type = KEYWORDS.get(ident, "IDENTIFIER")
                tokens.append(Token(token_type, ident, start_line, start_col))
                continue

            matched = False
            for symbol, token_type in SYMBOLS:
                if self.source.startswith(symbol, self.pos):
                    for _ in symbol:
                        self._advance()
                    tokens.append(Token(token_type, symbol, start_line, start_col))
                    matched = True
                    break
            if matched:
                continue

            raise LexerError(f"Unexpected character '{ch}'", start_line)

        return tokens
