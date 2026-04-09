from __future__ import annotations

from typing import List

from .models import ExpressionRecord, IRInstruction, Token


class IRGenerator:
    def __init__(self) -> None:
        self.label_index = 0

    def _new_label(self, prefix: str = "L") -> str:
        self.label_index += 1
        return f"{prefix}{self.label_index}"

    def generate(self, tokens: List[Token], expressions: List[ExpressionRecord]) -> List[IRInstruction]:
        self.tokens = [t for t in tokens if t.kind != "PREPROCESSOR"]
        self.pos = 0
        self.ir: List[IRInstruction] = []
        self.expr_by_line = {e.line: e for e in expressions if e.expr is not None}

        while not self._at_end():
            if self._is_function_start():
                self._parse_function()
            else:
                self.pos += 1

        if not self.ir:
            self.ir.append(IRInstruction(op="NOP", comment="No intermediate representation generated."))
        return self.ir

    def _parse_function(self) -> None:
        fn = self.tokens[self.pos + 1].value
        self.ir.append(IRInstruction(op="FUNC_BEGIN", result=fn, comment=f"function {fn} entry"))

        # Move to function body start.
        while not self._at_end() and self._current().value != "{":
            self.pos += 1
        if self._current().value == "{":
            self.pos += 1
            self._parse_block()
        self.ir.append(IRInstruction(op="FUNC_END", comment="function exit"))

    def _parse_block(self) -> None:
        while not self._at_end() and self._current().value != "}":
            self._parse_statement()
        if self._current().value == "}":
            self.pos += 1

    def _parse_statement(self) -> None:
        t = self._current()
        if t.value == "if":
            self._parse_if()
            return
        if t.value == "while":
            self._parse_while()
            return
        if t.value == "for":
            self._parse_for()
            return
        if t.value == "return":
            self._parse_return()
            return
        if t.value == "{":
            self.pos += 1
            self._parse_block()
            return
        self._parse_linear_statement()

    def _parse_if(self) -> None:
        if_line = self._current().line
        else_label = self._new_label("IF_ELSE_")
        end_label = self._new_label("IF_END_")
        self.pos += 1
        cond = self._collect_paren_text()
        self.ir.append(IRInstruction(op="IF_FALSE", arg1=cond or f"cond@{if_line}", result=else_label, comment="if condition false jump"))
        self._parse_statement()
        self.ir.append(IRInstruction(op="GOTO", result=end_label, comment="if end jump"))
        self.ir.append(IRInstruction(op="LABEL", result=else_label, comment="else block"))
        if self._current().value == "else":
            self.pos += 1
            self._parse_statement()
        self.ir.append(IRInstruction(op="LABEL", result=end_label, comment="if merge"))

    def _parse_while(self) -> None:
        start = self._new_label("WHILE_BEGIN_")
        end = self._new_label("WHILE_END_")
        self.ir.append(IRInstruction(op="LABEL", result=start, comment="while condition"))
        self.pos += 1
        cond = self._collect_paren_text()
        self.ir.append(IRInstruction(op="IF_FALSE", arg1=cond or "cond", result=end, comment="while exit"))
        self._parse_statement()
        self.ir.append(IRInstruction(op="GOTO", result=start, comment="while back-edge"))
        self.ir.append(IRInstruction(op="LABEL", result=end, comment="while end"))

    def _parse_for(self) -> None:
        start = self._new_label("FOR_BEGIN_")
        update = self._new_label("FOR_UPDATE_")
        end = self._new_label("FOR_END_")

        self.pos += 1
        init_text, cond_text, update_text = self._collect_for_header()
        if init_text:
            self.ir.append(IRInstruction(op="EXPR", arg1=init_text, comment="for init"))
        self.ir.append(IRInstruction(op="LABEL", result=start, comment="for condition"))
        self.ir.append(IRInstruction(op="IF_FALSE", arg1=cond_text or "true", result=end, comment="for exit"))
        self._parse_statement()
        self.ir.append(IRInstruction(op="LABEL", result=update, comment="for update"))
        if update_text:
            self.ir.append(IRInstruction(op="EXPR", arg1=update_text, comment="for update expr"))
        self.ir.append(IRInstruction(op="GOTO", result=start, comment="for back-edge"))
        self.ir.append(IRInstruction(op="LABEL", result=end, comment="for end"))

    def _parse_return(self) -> None:
        line = self._current().line
        self.pos += 1
        parts: List[str] = []
        while not self._at_end() and self._current().value != ";":
            parts.append(self._current().value)
            self.pos += 1
        if not self._at_end() and self._current().value == ";":
            self.pos += 1
        value = " ".join(parts).strip() or "0"
        self.ir.append(IRInstruction(op="RETURN", arg1=value, comment=f"return@{line}"))

    def _parse_linear_statement(self) -> None:
        line = self._current().line
        parts: List[str] = []
        while not self._at_end() and self._current().value not in {";", "}", "{"}:
            parts.append(self._current().value)
            self.pos += 1
        if self._current().value == ";":
            self.pos += 1

        text = " ".join(parts).strip()
        if not text:
            return

        if "=" in text and "==" not in text:
            lhs, rhs = text.split("=", 1)
            lhs = lhs.strip().split()[-1]
            rhs = rhs.strip()
            if "(" in rhs and rhs.endswith(")"):
                fn = rhs[: rhs.index("(")].strip()
                self.ir.append(IRInstruction(op="CALL", arg1=fn, result=lhs, comment="call and assign"))
            else:
                self.ir.append(IRInstruction(op="=", arg1=rhs, result=lhs, comment=f"assign@{line}"))
            return

        if "(" in text and text.endswith(")"):
            fn = text[: text.index("(")].split()[-1]
            self.ir.append(IRInstruction(op="CALL", arg1=fn, comment=f"call@{line}"))
            return

        self.ir.append(IRInstruction(op="EXPR", arg1=text, comment=f"expr@{line}"))

    def _collect_paren_text(self) -> str:
        if self._current().value != "(":
            return ""
        self.pos += 1
        depth = 1
        parts: List[str] = []
        while not self._at_end() and depth > 0:
            t = self._current()
            if t.value == "(":
                depth += 1
                parts.append(t.value)
            elif t.value == ")":
                depth -= 1
                if depth > 0:
                    parts.append(t.value)
            else:
                parts.append(t.value)
            self.pos += 1
        return " ".join(parts).strip()

    def _collect_for_header(self) -> tuple[str, str, str]:
        if self._current().value != "(":
            return "", "", ""
        self.pos += 1
        sections: List[List[str]] = [[], [], []]
        sec = 0
        depth = 0
        while not self._at_end():
            t = self._current()
            if t.value == "(":
                depth += 1
                sections[sec].append(t.value)
            elif t.value == ")":
                if depth == 0:
                    self.pos += 1
                    break
                depth -= 1
                sections[sec].append(t.value)
            elif t.value == ";" and depth == 0:
                sec = min(2, sec + 1)
            else:
                sections[sec].append(t.value)
            self.pos += 1
        return (" ".join(sections[0]).strip(), " ".join(sections[1]).strip(), " ".join(sections[2]).strip())

    def _is_function_start(self) -> bool:
        if self.pos + 2 >= len(self.tokens):
            return False
        a, b, c = self.tokens[self.pos], self.tokens[self.pos + 1], self.tokens[self.pos + 2]
        return a.kind in {"TYPE", "KEYWORD"} and b.kind == "IDENTIFIER" and c.value == "("

    def _current(self) -> Token:
        if self.pos >= len(self.tokens):
            return Token("EOF", "EOF", self.tokens[-1].line if self.tokens else 1, 1)
        return self.tokens[self.pos]

    def _at_end(self) -> bool:
        return self.pos >= len(self.tokens)
