"""
Control Flow Graph (CFG) / Flowchart builder
-----------------------------------------------
Walks a list of AST statements and builds a positioned graph of nodes
(start / end / process / decision) and edges, ready to be rendered as
an SVG flowchart. The SAME function is used for both the original and
the optimized AST, so the two flowcharts are always generated from the
real program structure -- never hard-coded.

Compiler Design concept: CONTROL FLOW GRAPH
Represents every possible execution path through the program: straight
line statements, if/else branching, and while looping (with an
explicit back-edge).
"""

import itertools

from .ast_nodes import VarDecl, Assign, Print, If, While, expr_to_source

NODE_W = 200
NODE_H = 56
V_SPACING = 110
MIN_BRANCH_OFFSET = 140

_counter = itertools.count(1)


def _new_id():
    return f"cfg{next(_counter)}"


def _stmt_label(stmt):
    if isinstance(stmt, VarDecl):
        return f"int {stmt.name} = {expr_to_source(stmt.expr)}"
    if isinstance(stmt, Assign):
        return f"{stmt.name} = {expr_to_source(stmt.expr)}"
    if isinstance(stmt, Print):
        return f"print({expr_to_source(stmt.expr)})"
    return "?"


class CFGBuilder:
    def __init__(self):
        self.nodes = []
        self.edges = []
        self.min_x = 0
        self.max_x = 0
        self.max_y = 0

    def build(self, statements):
        start_id = _new_id()
        self._add_node(start_id, "start", "START", 0, 0, 0)
        pending = [(start_id, None)]

        pending, y = self._build_block(statements, 0, V_SPACING, pending, offset=320)

        end_id = _new_id()
        self._add_node(end_id, "end", "END", 0, y, 0)
        for from_id, label in pending:
            self._add_edge(from_id, end_id, label)

        half_widest = 130  # half of DIAMOND_W (210) plus a small margin, rounded up
        margin = 60
        min_x_edge = self.min_x - half_widest - margin
        max_x_edge = self.max_x + half_widest + margin
        # Loop-back curves bow out to the right of the widest node, so make
        # sure there is always extra breathing room on the right side too.
        max_x_edge += 140
        width = max(max_x_edge - min_x_edge, 480)
        height = y + V_SPACING
        return {
            "nodes": self.nodes,
            "edges": self.edges,
            "bounds": {
                "minX": min_x_edge,
                "width": width,
                "height": height,
            },
        }

    # ------------------------------------------------------------------
    def _add_node(self, node_id, node_type, label, x, y, line):
        self.nodes.append({
            "id": node_id, "type": node_type, "label": label,
            "x": x, "y": y, "line": line,
        })
        self.min_x = min(self.min_x, x)
        self.max_x = max(self.max_x, x)
        self.max_y = max(self.max_y, y)

    def _add_edge(self, from_id, to_id, label):
        self.edges.append({"from": from_id, "to": to_id, "label": label})

    # ------------------------------------------------------------------
    def _build_block(self, statements, x, y, pending, offset):
        for stmt in statements:
            if isinstance(stmt, If):
                dec_id = _new_id()
                self._add_node(dec_id, "decision", expr_to_source(stmt.cond), x, y, stmt.line)
                for from_id, label in pending:
                    self._add_edge(from_id, dec_id, label)
                y += V_SPACING

                branch_offset = max(offset, MIN_BRANCH_OFFSET)
                then_x = x - branch_offset
                else_x = x + branch_offset
                next_offset = max(branch_offset * 0.62, MIN_BRANCH_OFFSET * 0.7)

                then_pending, then_y = self._build_block(
                    stmt.then_block, then_x, y, [(dec_id, "Yes")], next_offset
                )
                if stmt.else_block is not None:
                    else_pending, else_y = self._build_block(
                        stmt.else_block, else_x, y, [(dec_id, "No")], next_offset
                    )
                else:
                    else_pending, else_y = [(dec_id, "No")], y

                y = max(then_y, else_y)
                pending = then_pending + else_pending

            elif isinstance(stmt, While):
                dec_id = _new_id()
                self._add_node(dec_id, "decision", expr_to_source(stmt.cond), x, y, stmt.line)
                for from_id, label in pending:
                    self._add_edge(from_id, dec_id, label)
                y += V_SPACING

                body_offset = max(offset * 0.62, MIN_BRANCH_OFFSET * 0.7)
                body_pending, body_y = self._build_block(
                    stmt.body, x, y, [(dec_id, "Yes")], body_offset
                )
                for from_id, label in body_pending:
                    self._add_edge(from_id, dec_id, "loop back")
                y = body_y
                pending = [(dec_id, "No")]

            else:
                pid = _new_id()
                self._add_node(pid, "process", _stmt_label(stmt), x, y, stmt.line)
                for from_id, label in pending:
                    self._add_edge(from_id, pid, label)
                pending = [(pid, None)]
                y += V_SPACING

        return pending, y


def build_cfg(statements):
    return CFGBuilder().build(statements)
