from __future__ import annotations

from typing import List

from .codegen import CodeGenerator
from .complexity import ComplexityAnalyzer
from .ir import IRGenerator
from .lexer import Lexer
from .models import AnalysisReport, ExprNode, ExpressionRecord
from .optimizer import Optimizer
from .parser import Parser
from .reporter import ReportFormatter
from .semantic import SemanticAnalyzer


class CompilerAnalyzer:
    def __init__(self) -> None:
        self.lexer = Lexer()
        self.ir_generator = IRGenerator()
        self.optimizer = Optimizer()
        self.codegen = CodeGenerator()
        self.complexity = ComplexityAnalyzer()
        self.semantic = SemanticAnalyzer()

    def analyze(self, source: str) -> AnalysisReport:
        report = AnalysisReport(source=source)

        report.tokens, report.lexical_errors = self.lexer.tokenize(source)

        parser = Parser(report.tokens)
        parse_result = parser.parse()
        report.syntax_errors = parse_result.errors
        report.parse_tree = self._build_parse_tree(parse_result.expressions)

        report.semantic_errors, report.semantic_warnings = self.semantic.analyze(report.tokens, parse_result.expressions)

        report.ir = self.ir_generator.generate(report.tokens, parse_result.expressions)
        report.optimized_ir, report.optimizations_applied = self.optimizer.optimize(report.ir)
        report.target_code = self.codegen.generate(report.optimized_ir)

        complexity_result = self.complexity.analyze(source)
        report.complexity = complexity_result.complexity
        report.complexity_steps = complexity_result.steps

        return report

    def _build_parse_tree(self, expressions: List[ExpressionRecord]) -> str:
        if not expressions:
            return "No parse tree nodes available."

        lines: List[str] = []
        rendered_count = 0

        for idx, record in enumerate(expressions, start=1):
            if record.expr is None:
                continue
            rendered_count += 1
            target_suffix = f" -> {record.target}" if record.target else ""
            lines.append(f"[{idx}] {record.context} (line {record.line}){target_suffix}")
            self._render_expr_node(record.expr, prefix="", is_last=True, out=lines)
            lines.append("")

        if rendered_count == 0:
            return "No parse tree nodes available."

        return "\n".join(lines).strip()

    def _render_expr_node(self, node: ExprNode, prefix: str, is_last: bool, out: List[str]) -> None:
        connector = "└── " if is_last else "├── "
        out.append(f"{prefix}{connector}{self._node_label(node)}")
        child_prefix = prefix + ("    " if is_last else "│   ")

        children: List[ExprNode] = []
        if node.kind == "binary":
            if node.left is not None:
                children.append(node.left)
            if node.right is not None:
                children.append(node.right)
        elif node.kind == "unary":
            if node.left is not None:
                children.append(node.left)
        elif node.kind == "call":
            children.extend(node.args)
        elif node.kind == "index":
            if node.left is not None:
                children.append(node.left)
            if node.right is not None:
                children.append(node.right)

        for i, child in enumerate(children):
            self._render_expr_node(child, child_prefix, i == len(children) - 1, out)

    def _node_label(self, node: ExprNode) -> str:
        if node.kind == "binary":
            return f"BinaryOp({node.value})"
        if node.kind == "unary":
            return f"UnaryOp({node.value})"
        if node.kind == "identifier":
            return f"Identifier({node.value})"
        if node.kind == "literal":
            return f"Literal({node.value})"
        if node.kind == "call":
            return f"Call({node.value})"
        if node.kind == "index":
            return "Index([])"
        if node.kind == "unknown":
            return f"Unknown({node.value})"
        return node.kind

    def analyze_and_format(self, source: str) -> str:
        formatter = ReportFormatter()
        return formatter.format(self.analyze(source))
