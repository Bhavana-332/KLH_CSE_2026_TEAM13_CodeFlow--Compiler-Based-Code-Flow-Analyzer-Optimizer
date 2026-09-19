"""
Custom exception types used across the compiler pipeline.
Every error carries a line number and a human-readable message so the
frontend can render a precise, non-crashing error panel.
"""


class CompilerError(Exception):
    """Base class for all compiler-stage errors."""

    stage = "Compiler"

    def __init__(self, message: str, line: int = 0):
        self.message = message
        self.line = line
        super().__init__(message)

    def to_dict(self, source_lines=None):
        source_line = ""
        if source_lines and 1 <= self.line <= len(source_lines):
            source_line = source_lines[self.line - 1]
        return {
            "stage": self.stage,
            "message": self.message,
            "line": self.line,
            "sourceLine": source_line,
        }


class LexerError(CompilerError):
    stage = "Lexical Analysis"


class ParserError(CompilerError):
    stage = "Syntax Analysis"


class SemanticError(CompilerError):
    stage = "Semantic Analysis"
