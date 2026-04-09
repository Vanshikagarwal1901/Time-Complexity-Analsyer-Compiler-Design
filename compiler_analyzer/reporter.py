from __future__ import annotations

from typing import Iterable

from .models import AnalysisReport, Diagnostic, IRInstruction, Token


class ReportFormatter:
    def format(self, report: AnalysisReport) -> str:
        sections = [
            self._lexical_section(report),
            self._syntax_section(report),
            self._semantic_section(report),
            self._ir_section(report),
            self._optimization_section(report),
            self._codegen_section(report),
            self._complexity_section(report),
        ]
        return "\n\n".join(sections)

    def _lexical_section(self, report: AnalysisReport) -> str:
        out = ["=== Lexical Analysis ==="]
        out.append("Tokens:")
        out.append("#   kind         value           line:col")
        for idx, t in enumerate(report.tokens[:120], start=1):
            out.append(f"{idx:3} {t.kind:12} {self._trim(t.value, 14):14} {t.line}:{t.column}")
        if len(report.tokens) > 120:
            out.append(f"... {len(report.tokens) - 120} more tokens")
        out.extend(self._diag_block(report.lexical_errors))
        return "\n".join(out)

    def _syntax_section(self, report: AnalysisReport) -> str:
        out = ["=== Syntax Analysis ==="]
        if not report.syntax_errors:
            out.append("No syntax errors detected.")
        out.extend(self._diag_block(report.syntax_errors))
        return "\n".join(out)

    def _semantic_section(self, report: AnalysisReport) -> str:
        out = ["=== Semantic Analysis ==="]
        if not report.semantic_errors and not report.semantic_warnings:
            out.append("No semantic issues detected.")
        out.extend(self._diag_block(report.semantic_errors))
        out.extend(self._diag_block(report.semantic_warnings))
        return "\n".join(out)

    def _ir_section(self, report: AnalysisReport) -> str:
        out = ["=== Intermediate Code (Three Address Code) ==="]
        for idx, ins in enumerate(report.ir, start=1):
            out.append(f"{idx:3}. {self._fmt_ir(ins)}")
        return "\n".join(out)

    def _optimization_section(self, report: AnalysisReport) -> str:
        out = ["=== Optimization ==="]
        out.append("Applied Optimizations:")
        for item in report.optimizations_applied:
            out.append(f"- {item}")
        out.append("\nBefore Optimization:")
        for ins in report.ir:
            out.append(f"  {self._fmt_ir(ins)}")
        out.append("After Optimization:")
        for ins in report.optimized_ir:
            out.append(f"  {self._fmt_ir(ins)}")
        return "\n".join(out)

    def _codegen_section(self, report: AnalysisReport) -> str:
        out = ["=== Code Generation (Pseudo Assembly) ==="]
        out.extend(report.target_code or ["No target code generated."])
        return "\n".join(out)

    def _complexity_section(self, report: AnalysisReport) -> str:
        out = ["=== Time Complexity ==="]
        out.append(f"Final Complexity: {report.complexity}")
        out.append("Derivation Steps:")
        for step in report.complexity_steps:
            out.append(f"- {step}")
        return "\n".join(out)

    def _diag_block(self, diagnostics: Iterable[Diagnostic]) -> list[str]:
        out: list[str] = []
        for d in diagnostics:
            out.append(f"[{d.level.upper()}] {d.phase} at {d.line}:{d.column} - {d.message}")
            if d.suggestion:
                out.append(f"  Suggestion: {d.suggestion}")
        return out

    def _fmt_ir(self, ins: IRInstruction) -> str:
        text = f"{ins.op} {ins.arg1} {ins.arg2} {ins.result}".strip()
        if ins.comment:
            text += f"    ; {ins.comment}"
        return " ".join(text.split())

    @staticmethod
    def _trim(value: str, width: int) -> str:
        return value if len(value) <= width else value[: width - 3] + "..."
