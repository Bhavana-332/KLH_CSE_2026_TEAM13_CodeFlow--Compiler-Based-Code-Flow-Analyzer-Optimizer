"""
Abstract Syntax Tree (AST) node definitions.

Compiler Design concept: INTERMEDIATE REPRESENTATION
The parser builds a tree of these nodes. Every later stage (semantic
analysis, optimization, CFG generation) operates purely on this
structure rather than on the original text, which is the whole point
of having an IR.
"""

import itertools

_id_counter = itertools.count(1)


class Node:
    """Base class. Every node gets a unique id, useful for the AST viewer."""

    def __init__(self, line=0):
        self.id = f"n{next(_id_counter)}"
        self.line = line

    def to_dict(self):
        raise NotImplementedError


class Program(Node):
    def __init__(self, statements, line=0):
        super().__init__(line)
        self.statements = statements

    def to_dict(self):
        return {
            "id": self.id,
            "type": "Program",
            "children": [s.to_dict() for s in self.statements],
        }


class VarDecl(Node):
    def __init__(self, name, expr, line):
        super().__init__(line)
        self.name = name
        self.expr = expr

    def to_dict(self):
        return {
            "id": self.id,
            "type": "VarDecl",
            "label": f"int {self.name} =",
            "line": self.line,
            "children": [self.expr.to_dict()],
        }


class Assign(Node):
    def __init__(self, name, expr, line):
        super().__init__(line)
        self.name = name
        self.expr = expr

    def to_dict(self):
        return {
            "id": self.id,
            "type": "Assign",
            "label": f"{self.name} =",
            "line": self.line,
            "children": [self.expr.to_dict()],
        }


class Print(Node):
    def __init__(self, expr, line):
        super().__init__(line)
        self.expr = expr

    def to_dict(self):
        return {
            "id": self.id,
            "type": "Print",
            "label": "print",
            "line": self.line,
            "children": [self.expr.to_dict()],
        }


class If(Node):
    def __init__(self, cond, then_block, else_block, line):
        super().__init__(line)
        self.cond = cond
        self.then_block = then_block  # list[Node]
        self.else_block = else_block  # list[Node] or None

    def to_dict(self):
        children = [{"id": self.cond.id, "type": "Condition",
                      "children": [self.cond.to_dict()]}]
        children.append({
            "id": f"{self.id}-then", "type": "Then",
            "children": [s.to_dict() for s in self.then_block],
        })
        if self.else_block is not None:
            children.append({
                "id": f"{self.id}-else", "type": "Else",
                "children": [s.to_dict() for s in self.else_block],
            })
        return {"id": self.id, "type": "If", "label": "if", "line": self.line, "children": children}


class While(Node):
    def __init__(self, cond, body, line):
        super().__init__(line)
        self.cond = cond
        self.body = body  # list[Node]

    def to_dict(self):
        return {
            "id": self.id,
            "type": "While",
            "label": "while",
            "line": self.line,
            "children": [
                {"id": self.cond.id, "type": "Condition", "children": [self.cond.to_dict()]},
                {"id": f"{self.id}-body", "type": "Body",
                 "children": [s.to_dict() for s in self.body]},
            ],
        }


class BinOp(Node):
    def __init__(self, op, left, right, line=0):
        super().__init__(line)
        self.op = op
        self.left = left
        self.right = right

    def to_dict(self):
        return {
            "id": self.id,
            "type": "BinOp",
            "label": self.op,
            "children": [self.left.to_dict(), self.right.to_dict()],
        }


class Num(Node):
    def __init__(self, value, line=0):
        super().__init__(line)
        self.value = value

    def to_dict(self):
        return {"id": self.id, "type": "Num", "label": str(self.value), "children": []}


class Var(Node):
    def __init__(self, name, line=0):
        super().__init__(line)
        self.name = name

    def to_dict(self):
        return {"id": self.id, "type": "Var", "label": self.name, "children": []}


def expr_to_source(node):
    """Render an expression node back to a short source-like string, used
    for optimization-report messages and the code comparison panel."""
    if isinstance(node, Num):
        return str(node.value)
    if isinstance(node, Var):
        return node.name
    if isinstance(node, BinOp):
        return f"{expr_to_source(node.left)} {node.op} {expr_to_source(node.right)}"
    return "?"


def stmt_to_source(node, indent=0):
    pad = "    " * indent
    if isinstance(node, VarDecl):
        return f"{pad}int {node.name} = {expr_to_source(node.expr)};"
    if isinstance(node, Assign):
        return f"{pad}{node.name} = {expr_to_source(node.expr)};"
    if isinstance(node, Print):
        return f"{pad}print({expr_to_source(node.expr)});"
    if isinstance(node, If):
        lines = [f"{pad}if ({expr_to_source(node.cond)}) {{"]
        for s in node.then_block:
            lines.append(stmt_to_source(s, indent + 1))
        if node.else_block is not None:
            lines.append(f"{pad}}} else {{")
            for s in node.else_block:
                lines.append(stmt_to_source(s, indent + 1))
        lines.append(f"{pad}}}")
        return "\n".join(lines)
    if isinstance(node, While):
        lines = [f"{pad}while ({expr_to_source(node.cond)}) {{"]
        for s in node.body:
            lines.append(stmt_to_source(s, indent + 1))
        lines.append(f"{pad}}}")
        return "\n".join(lines)
    return f"{pad}?"


def program_to_source(statements):
    return "\n".join(stmt_to_source(s) for s in statements)
