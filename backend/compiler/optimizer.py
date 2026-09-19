"""
Code Optimizer
----------------
Performs source-to-source style optimizations directly on the AST and
returns a NEW, optimized AST plus a list of "optimization records"
describing exactly what changed and why, so the frontend can render a
readable optimization report.

Compiler Design concept: CODE OPTIMIZATION
Implements four classic, conservative optimizations:

1. Constant Folding          -> evaluate constant sub-expressions at compile time
2. Algebraic Simplification  -> x+0, x*1, x*0, x-0, x/1 identities
3. Constant Condition Opt.   -> inline the branch of an `if` whose condition
                                 is a compile-time constant; drop a `while`
                                 whose condition is constant-false
4. Dead Code Elimination     -> drop a variable assignment that is
                                 unconditionally overwritten before it is
                                 ever read (conservative: stops at any
                                 branch/loop boundary to avoid changing
                                 program behaviour)
"""

from .ast_nodes import (
    VarDecl, Assign, Print, If, While, BinOp, Num, Var,
    expr_to_source, stmt_to_source,
)

ARITH_OPS = {"+", "-", "*", "/"}
COMPARISON_FN = {
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    ">": lambda a, b: a > b,
    "<": lambda a, b: a < b,
    ">=": lambda a, b: a >= b,
    "<=": lambda a, b: a <= b,
}


class Optimizer:
    def __init__(self, program):
        self.program = program
        self.records = []

    def optimize(self):
        new_statements = self._optimize_block(self.program.statements)
        return new_statements, self.records

    # ------------------------------------------------------------------
    # Expression-level optimization
    # ------------------------------------------------------------------
    def _fold_expr(self, expr, line):
        if not isinstance(expr, BinOp):
            return expr

        left = self._fold_expr(expr.left, line)
        right = self._fold_expr(expr.right, line)
        op = expr.op

        # 1) Constant folding
        if isinstance(left, Num) and isinstance(right, Num):
            before = f"{expr_to_source(left)} {op} {expr_to_source(right)}"
            if op in ARITH_OPS:
                if op == "/" and right.value == 0:
                    # avoid divide-by-zero at compile time; leave for runtime
                    return BinOp(op, left, right, line)
                value = {
                    "+": left.value + right.value,
                    "-": left.value - right.value,
                    "*": left.value * right.value,
                    "/": left.value / right.value if isinstance(left.value, float) or isinstance(right.value, float) or left.value % right.value != 0 else left.value // right.value,
                }[op]
                if isinstance(value, float) and value.is_integer():
                    value = int(value)
                folded = Num(value, line)
                self.records.append({
                    "type": "Constant Folding",
                    "before": before,
                    "after": expr_to_source(folded),
                    "line": line,
                })
                return folded
            if op in COMPARISON_FN:
                result = 1 if COMPARISON_FN[op](left.value, right.value) else 0
                folded = Num(result, line)
                self.records.append({
                    "type": "Constant Folding",
                    "before": before,
                    "after": expr_to_source(folded),
                    "line": line,
                })
                return folded

        # 2) Algebraic simplification (only for arithmetic operators)
        if op in ARITH_OPS:
            simplified = self._algebraic_identity(op, left, right)
            if simplified is not None:
                before = f"{expr_to_source(left)} {op} {expr_to_source(right)}"
                self.records.append({
                    "type": "Algebraic Simplification",
                    "before": before,
                    "after": expr_to_source(simplified),
                    "line": line,
                })
                return simplified

        return BinOp(op, left, right, line)

    @staticmethod
    def _algebraic_identity(op, left, right):
        if op == "+":
            if isinstance(right, Num) and right.value == 0:
                return left
            if isinstance(left, Num) and left.value == 0:
                return right
        elif op == "-":
            if isinstance(right, Num) and right.value == 0:
                return left
        elif op == "*":
            if isinstance(right, Num) and right.value == 1:
                return left
            if isinstance(left, Num) and left.value == 1:
                return right
            if isinstance(right, Num) and right.value == 0:
                return Num(0)
            if isinstance(left, Num) and left.value == 0:
                return Num(0)
        elif op == "/":
            if isinstance(right, Num) and right.value == 1:
                return left
        return None

    # ------------------------------------------------------------------
    # Statement-level optimization
    # ------------------------------------------------------------------
    def _optimize_block(self, statements):
        result = []
        for stmt in statements:
            if isinstance(stmt, VarDecl):
                new_expr = self._fold_expr(stmt.expr, stmt.line)
                result.append(VarDecl(stmt.name, new_expr, stmt.line))

            elif isinstance(stmt, Assign):
                new_expr = self._fold_expr(stmt.expr, stmt.line)
                result.append(Assign(stmt.name, new_expr, stmt.line))

            elif isinstance(stmt, Print):
                new_expr = self._fold_expr(stmt.expr, stmt.line)
                result.append(Print(new_expr, stmt.line))

            elif isinstance(stmt, If):
                new_cond = self._fold_expr(stmt.cond, stmt.line)
                new_then = self._optimize_block(stmt.then_block)
                new_else = self._optimize_block(stmt.else_block) if stmt.else_block is not None else None

                if isinstance(new_cond, Num):
                    taken_branch = new_then if new_cond.value != 0 else (new_else or [])
                    branch_name = "then" if new_cond.value != 0 else "else"
                    self.records.append({
                        "type": "Constant Condition",
                        "before": f"if ({expr_to_source(stmt.cond)}) {{ ... }}",
                        "after": f"branch always takes '{branch_name}' \u2013 condition inlined, branching removed",
                        "line": stmt.line,
                    })
                    result.extend(taken_branch)
                else:
                    result.append(If(new_cond, new_then, new_else, stmt.line))

            elif isinstance(stmt, While):
                new_cond = self._fold_expr(stmt.cond, stmt.line)
                new_body = self._optimize_block(stmt.body)
                if isinstance(new_cond, Num) and new_cond.value == 0:
                    self.records.append({
                        "type": "Dead Code Elimination",
                        "before": f"while ({expr_to_source(stmt.cond)}) {{ ... }}",
                        "after": "removed \u2013 loop body never executes",
                        "line": stmt.line,
                    })
                else:
                    result.append(While(new_cond, new_body, stmt.line))
            else:
                result.append(stmt)

        return self._eliminate_dead_stores(result)

    # ------------------------------------------------------------------
    # Conservative dead-store elimination within one straight-line block
    # ------------------------------------------------------------------
    def _eliminate_dead_stores(self, statements):
        n = len(statements)
        to_remove = set()
        # If we remove a VarDecl, the statement that made it dead must be
        # promoted to a VarDecl in its place so the variable is still
        # declared in the optimized program.
        promote = {}

        for i in range(n):
            stmt = statements[i]
            if not isinstance(stmt, (VarDecl, Assign)):
                continue
            name = stmt.name
            for j in range(i + 1, n):
                nxt = statements[j]
                if isinstance(nxt, (If, While)):
                    # Cannot safely reason past a branch/loop boundary.
                    break
                if isinstance(nxt, Print):
                    if self._reads_var(nxt.expr, name):
                        break
                    continue
                if isinstance(nxt, (VarDecl, Assign)):
                    if self._reads_var(nxt.expr, name):
                        break
                    if isinstance(nxt, Assign) and nxt.name == name:
                        to_remove.add(i)
                        if isinstance(stmt, VarDecl):
                            promote[j] = name
                        break
                    if isinstance(nxt, VarDecl) and nxt.name == name:
                        break
                    continue

        if not to_remove:
            return statements

        for i in sorted(to_remove):
            stmt = statements[i]
            self.records.append({
                "type": "Dead Code Elimination",
                "before": stmt_to_source(stmt).strip(),
                "after": "removed \u2013 value overwritten before it is read",
                "line": stmt.line,
            })

        result = []
        for idx, s in enumerate(statements):
            if idx in to_remove:
                continue
            if idx in promote and isinstance(s, Assign):
                s = VarDecl(s.name, s.expr, s.line)
            result.append(s)
        return result

    @staticmethod
    def _reads_var(expr, name):
        if isinstance(expr, Var):
            return expr.name == name
        if isinstance(expr, BinOp):
            return Optimizer._reads_var(expr.left, name) or Optimizer._reads_var(expr.right, name)
        return False
