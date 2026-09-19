"""
Semantic Analyzer
-------------------
Walks the AST after parsing and checks rules that a context-free
grammar cannot express: variable declaration-before-use, duplicate
declarations, and undeclared-variable usage.

Compiler Design concept: SEMANTIC ANALYSIS
Syntax analysis only guarantees the program is *structurally* valid.
Semantic analysis guarantees it is *meaningfully* valid within the
scope rules of the language.
"""

from .ast_nodes import VarDecl, Assign, Print, If, While, BinOp, Var, Num
from .errors import SemanticError


class SemanticAnalyzer:
    def __init__(self, program):
        self.program = program
        self.declared = set()

    def analyze(self):
        self._visit_block(self.program.statements)
        return True

    def _visit_block(self, statements):
        for stmt in statements:
            self._visit_stmt(stmt)

    def _visit_stmt(self, stmt):
        if isinstance(stmt, VarDecl):
            if stmt.name in self.declared:
                raise SemanticError(
                    f"Variable '{stmt.name}' is already declared.", stmt.line
                )
            self._visit_expr(stmt.expr)
            self.declared.add(stmt.name)
        elif isinstance(stmt, Assign):
            if stmt.name not in self.declared:
                raise SemanticError(
                    f"Variable '{stmt.name}' used before declaration.", stmt.line
                )
            self._visit_expr(stmt.expr)
        elif isinstance(stmt, Print):
            self._visit_expr(stmt.expr)
        elif isinstance(stmt, If):
            self._visit_expr(stmt.cond)
            self._visit_block(stmt.then_block)
            if stmt.else_block is not None:
                self._visit_block(stmt.else_block)
        elif isinstance(stmt, While):
            self._visit_expr(stmt.cond)
            self._visit_block(stmt.body)
        else:
            raise SemanticError(f"Unknown statement type {type(stmt).__name__}", getattr(stmt, "line", 0))

    def _visit_expr(self, expr):
        if isinstance(expr, Num):
            return
        if isinstance(expr, Var):
            if expr.name not in self.declared:
                raise SemanticError(
                    f"Variable '{expr.name}' used before declaration.", expr.line
                )
            return
        if isinstance(expr, BinOp):
            self._visit_expr(expr.left)
            self._visit_expr(expr.right)
            return
        raise SemanticError(f"Unknown expression type {type(expr).__name__}", getattr(expr, "line", 0))
