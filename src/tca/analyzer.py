from __future__ import annotations

from .ast_nodes import Block, Function, Loop, Program, Statement
from .complexity import Complexity


def analyze_program(program: Program) -> Complexity:
    return analyze_block(program.body)


def analyze_block(block: Block) -> Complexity:
    current = Complexity()
    for stmt in block.statements:
        current = current.max_with(analyze_statement(stmt))
    return current


def analyze_statement(stmt: Statement) -> Complexity:
    if isinstance(stmt, Loop):
        return loop_complexity(stmt)
    if isinstance(stmt, Function):
        return analyze_block(stmt.body)
    return Complexity()


def loop_complexity(loop: Loop) -> Complexity:
    bound = loop.bound
    if bound == "constant":
        base = Complexity()
    elif bound == "linear":
        base = Complexity(degree=1)
    elif bound == "log":
        base = Complexity(log_power=1)
    else:
        base = Complexity(unknown=True)
    body = analyze_block(loop.body)
    return base.multiply(body)
