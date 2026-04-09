from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Token:
    kind: str
    value: str
    line: int
    column: int


@dataclass
class Diagnostic:
    phase: str
    level: str
    message: str
    line: int
    column: int
    suggestion: Optional[str] = None


@dataclass
class IRInstruction:
    op: str
    arg1: str = ""
    arg2: str = ""
    result: str = ""
    comment: str = ""


@dataclass
class ExprNode:
    kind: str
    value: str = ""
    left: Optional["ExprNode"] = None
    right: Optional["ExprNode"] = None
    args: List["ExprNode"] = field(default_factory=list)


@dataclass
class ExpressionRecord:
    context: str
    line: int
    target: Optional[str]
    expr: Optional[ExprNode]


@dataclass
class AnalysisReport:
    source: str
    tokens: List[Token] = field(default_factory=list)
    lexical_errors: List[Diagnostic] = field(default_factory=list)
    syntax_errors: List[Diagnostic] = field(default_factory=list)
    semantic_errors: List[Diagnostic] = field(default_factory=list)
    semantic_warnings: List[Diagnostic] = field(default_factory=list)
    ir: List[IRInstruction] = field(default_factory=list)
    optimized_ir: List[IRInstruction] = field(default_factory=list)
    optimizations_applied: List[str] = field(default_factory=list)
    target_code: List[str] = field(default_factory=list)
    parse_tree: str = ""
    complexity: str = "O(1)"
    complexity_steps: List[str] = field(default_factory=list)

    def has_errors(self) -> bool:
        return bool(self.lexical_errors or self.syntax_errors or self.semantic_errors)
