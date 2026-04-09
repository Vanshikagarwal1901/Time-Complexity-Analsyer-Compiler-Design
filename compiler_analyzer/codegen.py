from __future__ import annotations

from typing import List

from .models import IRInstruction


class CodeGenerator:
    def generate(self, ir: List[IRInstruction]) -> List[str]:
        target: List[str] = []
        register_map = {}
        registers = ["R1", "R2", "R3", "R4", "R5", "R6"]

        def reg(name: str) -> str:
            if not name:
                return ""
            if name not in register_map:
                register_map[name] = registers[len(register_map) % len(registers)]
            return register_map[name]

        def operand(name: str) -> str:
            if not name:
                return ""
            if name.startswith('"') and name.endswith('"'):
                return name
            if name.replace(".", "", 1).lstrip("-").isdigit():
                return name
            return reg(name)

        for ins in ir:
            if ins.op == "FUNC_BEGIN":
                target.append(f"{ins.result}:")
                target.append("  PUSH BP")
                target.append("  MOV BP, SP")
            elif ins.op == "FUNC_END":
                target.append("  MOV SP, BP")
                target.append("  POP BP")
                target.append("  RET")
            elif ins.op == "LABEL":
                target.append(f"{ins.result}:")
            elif ins.op == "GOTO":
                target.append(f"  JMP {ins.result}")
            elif ins.op == "IF_FALSE":
                target.append("  CMP COND, 0")
                target.append(f"  JE {ins.result}")
            elif ins.op == "RETURN":
                target.append(f"  MOV R0, {operand(ins.arg1)}")
                target.append("  RET")
            elif ins.op == "=":
                target.append(f"  MOV {reg(ins.result)}, {operand(ins.arg1)}")
            elif ins.op in {"+", "-", "*", "/"}:
                op_map = {"+": "ADD", "-": "SUB", "*": "MUL", "/": "DIV"}
                r = reg(ins.result)
                target.append(f"  MOV {r}, {operand(ins.arg1)}")
                target.append(f"  {op_map[ins.op]} {r}, {operand(ins.arg2)}")
            elif ins.op == "CALL":
                target.append(f"  CALL {ins.arg1}")
                if ins.result:
                    target.append(f"  MOV {reg(ins.result)}, R0")
            else:
                target.append(f"  ; {ins.op} {ins.arg1} {ins.arg2} {ins.result}".strip())

        if not target:
            target.append("; No target code generated.")

        return target
