"""
Compiler Orchestrator
------------------------
Runs the full CodeFlow pipeline:

    source -> Lexer -> Parser -> SemanticAnalyzer -> Optimizer -> CFG -> SVG

and assembles a single JSON-serialisable result dict for the API layer.
Every stage is wrapped so that ANY compiler error (lexical, syntax or
semantic) is caught and turned into a clean, structured error response
instead of a stack trace or a crash.
"""

from .lexer import Lexer
from .parser import Parser
from .semantic import SemanticAnalyzer
from .optimizer import Optimizer
from .cfg import build_cfg
from .svg_render import render_svg
from .ast_nodes import If, While, Program, program_to_source
from .errors import CompilerError


def _count_statements(statements):
    count = 0
    for stmt in statements:
        count += 1
        if isinstance(stmt, If):
            count += _count_statements(stmt.then_block)
            if stmt.else_block is not None:
                count += _count_statements(stmt.else_block)
        elif isinstance(stmt, While):
            count += _count_statements(stmt.body)
    return count


def compile_source(source: str) -> dict:
    source_lines = source.splitlines()
    stages = {
        "lexical": "pending",
        "syntax": "pending",
        "semantic": "pending",
        "optimization": "pending",
        "flowchart": "pending",
    }

    try:
        # ---------------- Lexical Analysis ----------------
        tokens = Lexer(source).tokenize()
        stages["lexical"] = "done"

        # ---------------- Syntax Analysis ----------------
        program = Parser(tokens).parse()
        stages["syntax"] = "done"

        # ---------------- Semantic Analysis ----------------
        SemanticAnalyzer(program).analyze()
        stages["semantic"] = "done"

        # ---------------- Code Optimization ----------------
        optimized_statements, records = Optimizer(program).optimize()
        stages["optimization"] = "done"

        # ---------------- Control Flow Graphs ----------------
        original_cfg = build_cfg(program.statements)
        optimized_cfg = build_cfg(optimized_statements)
        flowchart_before = render_svg(original_cfg)
        flowchart_after = render_svg(optimized_cfg)
        stages["flowchart"] = "done"

        before_count = _count_statements(program.statements)
        after_count = _count_statements(optimized_statements)
        reduction = 0.0
        if before_count > 0:
            reduction = round((before_count - after_count) / before_count * 100, 1)

        optimized_program = Program(optimized_statements)

        return {
            "success": True,
            "stages": stages,
            "tokens": [t.to_dict() for t in tokens if t.type != "EOF"],
            "ast": program.to_dict(),
            "astOptimized": optimized_program.to_dict(),
            "optimizations": records,
            "originalCode": program_to_source(program.statements),
            "optimizedCode": program_to_source(optimized_statements),
            "flowchartBefore": flowchart_before,
            "flowchartAfter": flowchart_after,
            "stats": {
                "statementsBefore": before_count,
                "statementsAfter": after_count,
                "optimizationsApplied": len(records),
                "reductionPercent": reduction,
            },
            "error": None,
        }

    except CompilerError as exc:
        # Mark every stage from the failure point onward as failed.
        stage_order = ["lexical", "syntax", "semantic", "optimization", "flowchart"]
        failed_stage_key = {
            "Lexical Analysis": "lexical",
            "Syntax Analysis": "syntax",
            "Semantic Analysis": "semantic",
        }.get(exc.stage, "lexical")
        reached = False
        for key in stage_order:
            if key == failed_stage_key:
                stages[key] = "error"
                reached = True
            elif reached:
                stages[key] = "skipped"
        return {
            "success": False,
            "stages": stages,
            "error": exc.to_dict(source_lines),
        }
    except Exception as exc:  # pragma: no cover - absolute safety net
        return {
            "success": False,
            "stages": stages,
            "error": {
                "stage": "Compiler",
                "message": f"Unexpected internal error: {exc}",
                "line": 0,
                "sourceLine": "",
            },
        }
