from __future__ import annotations

from copy import deepcopy
import re
from typing import List

from .models import IRInstruction


class Optimizer:
    def optimize(self, ir: List[IRInstruction]) -> tuple[List[IRInstruction], List[str]]:
        optimized = deepcopy(ir)
        applied: List[str] = []

        optimized, changed = self._constant_folding(optimized)
        if changed:
            applied.extend(changed)

        optimized, changed = self._dead_code_elimination(optimized)
        if changed:
            applied.extend(changed)

        optimized, changed = self._common_subexpression_elimination(optimized)
        if changed:
            applied.extend(changed)

        if not applied:
            applied.append("No optimization rule was applicable.")

        return optimized, applied

    def _constant_folding(self, ir: List[IRInstruction]) -> tuple[List[IRInstruction], List[str]]:
        changes: List[str] = []
        for ins in ir:
            if ins.op in {"+", "-", "*", "/"} and self._is_number(ins.arg1) and self._is_number(ins.arg2):
                a = float(ins.arg1)
                b = float(ins.arg2)
                if ins.op == "+":
                    value = a + b
                elif ins.op == "-":
                    value = a - b
                elif ins.op == "*":
                    value = a * b
                else:
                    if b == 0:
                        continue
                    value = a / b
                folded = str(int(value)) if value.is_integer() else str(round(value, 6))
                old = f"{ins.result} = {ins.arg1} {ins.op} {ins.arg2}"
                ins.op = "="
                ins.arg1 = folded
                ins.arg2 = ""
                changes.append(f"Constant Folding: {old} -> {ins.result} = {folded}")
                continue

            if ins.op == "=":
                expr = ins.arg1.strip()
                binary = re.fullmatch(r"(-?\d+(?:\.\d+)?)\s*([+\-*/])\s*(-?\d+(?:\.\d+)?)", expr)
                if binary:
                    a = float(binary.group(1))
                    op = binary.group(2)
                    b = float(binary.group(3))
                    if op == "+":
                        value = a + b
                    elif op == "-":
                        value = a - b
                    elif op == "*":
                        value = a * b
                    else:
                        if b == 0:
                            continue
                        value = a / b
                    folded = str(int(value)) if value.is_integer() else str(round(value, 6))
                    ins.arg1 = folded
                    changes.append(f"Constant Folding: {ins.result} = {expr} -> {ins.result} = {folded}")
                    continue

                simplified = self._simplify_expr(expr)
                if simplified is not None and simplified != expr:
                    ins.arg1 = simplified
                    changes.append(f"Algebraic Simplification: {ins.result} = {expr} -> {ins.result} = {simplified}")
        return ir, changes

    def _dead_code_elimination(self, ir: List[IRInstruction]) -> tuple[List[IRInstruction], List[str]]:
        changes: List[str] = []
        used = set()
        for ins in ir:
            used.update(self._extract_identifiers(ins.arg1))
            used.update(self._extract_identifiers(ins.arg2))

        filtered: List[IRInstruction] = []
        for ins in ir:
            if ins.result.startswith("t") and ins.result not in used and ins.op not in {"RETURN", "IF_FALSE"}:
                changes.append(f"Dead Code Elimination: removed unused temp assignment '{ins.result}'.")
                continue
            if ins.op == "=" and self._is_identifier(ins.result) and ins.result not in used:
                changes.append(f"Dead Code Elimination: removed unused assignment to '{ins.result}'.")
                continue
            filtered.append(ins)

        return filtered, changes

    def _common_subexpression_elimination(self, ir: List[IRInstruction]) -> tuple[List[IRInstruction], List[str]]:
        changes: List[str] = []
        expr_to_temp = {}

        for ins in ir:
            if ins.op in {"+", "-", "*", "/"}:
                key = (ins.op, ins.arg1, ins.arg2)
                if key in expr_to_temp:
                    old_result = ins.result
                    old_expr = f"{ins.arg1} {ins.op} {ins.arg2}".strip()
                    ins.op = "="
                    ins.arg1 = expr_to_temp[key]
                    ins.arg2 = ""
                    changes.append(
                        f"Common Subexpression Elimination: reused {expr_to_temp[key]} for expression {old_expr} (was {old_result})."
                    )
                else:
                    expr_to_temp[key] = ins.result
            elif ins.op == "=" and self._is_binary_expression(ins.arg1):
                expr_key = ("=", self._normalize_expr(ins.arg1))
                if expr_key in expr_to_temp:
                    old_expr = ins.arg1
                    old_result = ins.result
                    ins.arg1 = expr_to_temp[expr_key]
                    changes.append(
                        f"Common Subexpression Elimination: reused {expr_to_temp[expr_key]} for expression {old_expr} (was {old_result})."
                    )
                else:
                    expr_to_temp[expr_key] = ins.result

        return ir, changes

    @staticmethod
    def _is_identifier(value: str) -> bool:
        return bool(re.fullmatch(r"[A-Za-z_]\w*", value or ""))

    @staticmethod
    def _extract_identifiers(value: str) -> set[str]:
        if not value:
            return set()
        return {token for token in re.findall(r"\b[A-Za-z_]\w*\b", value)}

    @staticmethod
    def _is_binary_expression(value: str) -> bool:
        if not value:
            return False
        return bool(re.search(r"\S\s*[+\-*/]\s*\S", value))

    @staticmethod
    def _normalize_expr(value: str) -> str:
        return " ".join((value or "").split())

    @staticmethod
    def _simplify_expr(expr: str) -> str | None:
        m = re.fullmatch(r"([A-Za-z_]\w*|-?\d+(?:\.\d+)?)\s*([+\-*/])\s*([A-Za-z_]\w*|-?\d+(?:\.\d+)?)", expr)
        if not m:
            return None

        left, op, right = m.group(1), m.group(2), m.group(3)
        if op == "+":
            if right == "0":
                return left
            if left == "0":
                return right
        if op == "-" and right == "0":
            return left
        if op == "*":
            if right == "1":
                return left
            if left == "1":
                return right
            if right == "0" or left == "0":
                return "0"
        if op == "/" and right == "1":
            return left
        return None

    @staticmethod
    def _is_number(value: str) -> bool:
        try:
            float(value)
            return True
        except ValueError:
            return False
