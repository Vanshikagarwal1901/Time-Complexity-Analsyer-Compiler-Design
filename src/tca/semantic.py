from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Set

from .ast_nodes import Block, Function, Loop, Program, Statement


@dataclass
class SymbolTable:
    functions: Set[str] = field(default_factory=set)


def analyze_semantics(program: Program) -> List[str]:
    errors: List[str] = []
    table = SymbolTable()
    _check_block(program.body, table, errors)
    return errors


def _check_block(block: Block, table: SymbolTable, errors: List[str]) -> None:
    for stmt in block.statements:
        _check_statement(stmt, table, errors)


def _check_statement(stmt: Statement, table: SymbolTable, errors: List[str]) -> None:
    if isinstance(stmt, Function):
        if stmt.name in table.functions:
            errors.append(f"Duplicate function name: {stmt.name}")
        else:
            table.functions.add(stmt.name)
        _check_block(stmt.body, table, errors)
    elif isinstance(stmt, Loop):
        _check_block(stmt.body, table, errors)
