"""
Syntax Analyzer (Parser)
--------------------------
A hand-written recursive-descent parser that turns the token stream
produced by the Lexer into an Abstract Syntax Tree (see ast_nodes.py).

Compiler Design concept: SYNTAX ANALYSIS
The parser encodes the grammar of the small CodeFlow language:

    program    -> statement*
    statement  -> varDecl | assign | ifStmt | whileStmt | printStmt
    varDecl    -> "int" IDENTIFIER "=" expr ";"
    assign     -> IDENTIFIER "=" expr ";"
    ifStmt     -> "if" "(" expr ")" block ("else" block)?
    whileStmt  -> "while" "(" expr ")" block
    printStmt  -> "print" "(" expr ")" ";"
    block      -> "{" statement* "}"
    expr       -> comparison
    comparison -> addition (("==" | "!=" | ">" | "<" | ">=" | "<=") addition)*
    addition   -> term (("+" | "-") term)*
    term       -> factor (("*" | "/") factor)*
    factor     -> NUMBER | IDENTIFIER | "(" expr ")"
"""

from .ast_nodes import Program, VarDecl, Assign, Print, If, While, BinOp, Num, Var
from .errors import ParserError

COMPARISON_OPS = {"EQ", "NE", "GT", "LT", "GE", "LE"}


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # -- token helpers -----------------------------------------------
    def _current(self):
        return self.tokens[self.pos]

    def _check(self, type_):
        return self._current().type == type_

    def _advance(self):
        tok = self.tokens[self.pos]
        if tok.type != "EOF":
            self.pos += 1
        return tok

    def _expect(self, type_, message):
        if not self._check(type_):
            tok = self._current()
            raise ParserError(f"{message} (found {tok.type!r})", tok.line)
        return self._advance()

    # -- entry point ---------------------------------------------------
    def parse(self):
        statements = []
        while not self._check("EOF"):
            statements.append(self._statement())
        return Program(statements)

    # -- statements ------------------------------------------------------
    def _statement(self):
        tok = self._current()
        if tok.type == "INT":
            return self._var_decl()
        if tok.type == "IDENTIFIER":
            return self._assign()
        if tok.type == "IF":
            return self._if_stmt()
        if tok.type == "WHILE":
            return self._while_stmt()
        if tok.type == "PRINT":
            return self._print_stmt()
        raise ParserError(f"Unexpected token {tok.type!r}", tok.line)

    def _var_decl(self):
        line = self._current().line
        self._advance()  # int
        name_tok = self._expect("IDENTIFIER", "Expected identifier after 'int'")
        self._expect("ASSIGN", "Expected '=' in variable declaration")
        expr = self._expr()
        self._expect("SEMI", "Expected ';' after declaration")
        return VarDecl(name_tok.value, expr, line)

    def _assign(self):
        name_tok = self._advance()
        line = name_tok.line
        self._expect("ASSIGN", f"Expected '=' after '{name_tok.value}'")
        expr = self._expr()
        self._expect("SEMI", "Expected ';' after assignment")
        return Assign(name_tok.value, expr, line)

    def _print_stmt(self):
        line = self._current().line
        self._advance()  # print
        self._expect("LPAREN", "Expected '(' after 'print'")
        expr = self._expr()
        self._expect("RPAREN", "Expected ')' after print expression")
        self._expect("SEMI", "Expected ';' after print statement")
        return Print(expr, line)

    def _if_stmt(self):
        line = self._current().line
        self._advance()  # if
        self._expect("LPAREN", "Expected '(' after 'if'")
        cond = self._expr()
        self._expect("RPAREN", "Expected ')' after condition")
        then_block = self._block()
        else_block = None
        if self._check("ELSE"):
            self._advance()
            else_block = self._block()
        return If(cond, then_block, else_block, line)

    def _while_stmt(self):
        line = self._current().line
        self._advance()  # while
        self._expect("LPAREN", "Expected '(' after 'while'")
        cond = self._expr()
        self._expect("RPAREN", "Expected ')' after condition")
        body = self._block()
        return While(cond, body, line)

    def _block(self):
        self._expect("LBRACE", "Expected '{' to start block")
        statements = []
        while not self._check("RBRACE"):
            if self._check("EOF"):
                raise ParserError("Unterminated block, expected '}'", self._current().line)
            statements.append(self._statement())
        self._expect("RBRACE", "Expected '}' to close block")
        return statements

    # -- expressions (precedence climbing) --------------------------------
    def _expr(self):
        return self._comparison()

    def _comparison(self):
        left = self._addition()
        while self._current().type in COMPARISON_OPS:
            op_tok = self._advance()
            right = self._addition()
            left = BinOp(op_tok.value, left, right, op_tok.line)
        return left

    def _addition(self):
        left = self._term()
        while self._current().type in ("PLUS", "MINUS"):
            op_tok = self._advance()
            right = self._term()
            left = BinOp(op_tok.value, left, right, op_tok.line)
        return left

    def _term(self):
        left = self._factor()
        while self._current().type in ("STAR", "SLASH"):
            op_tok = self._advance()
            right = self._factor()
            left = BinOp(op_tok.value, left, right, op_tok.line)
        return left

    def _factor(self):
        tok = self._current()
        if tok.type == "NUMBER":
            self._advance()
            value = float(tok.value) if "." in tok.value else int(tok.value)
            return Num(value, tok.line)
        if tok.type == "IDENTIFIER":
            self._advance()
            return Var(tok.value, tok.line)
        if tok.type == "LPAREN":
            self._advance()
            expr = self._expr()
            self._expect("RPAREN", "Expected ')' to close expression")
            return expr
        if tok.type in ("MINUS",):
            # unary minus, expressed as 0 - expr
            self._advance()
            operand = self._factor()
            return BinOp("-", Num(0, tok.line), operand, tok.line)
        raise ParserError(f"Expected expression, found {tok.type!r}", tok.line)
