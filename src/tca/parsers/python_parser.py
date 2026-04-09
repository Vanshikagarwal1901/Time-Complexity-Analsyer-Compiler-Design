from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional

from ..ast_nodes import Block, Function, Loop, Program


TOKEN_RE = re.compile(
    r"[A-Za-z_][A-Za-z0-9_]*|\d+|==|!=|<=|>=|\+=|-=|\*=|/=|\+|\-|\*|/|=|<|>|\(|\)|:|,"
)


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    line: int


class PythonLexer:
    def tokenize(self, code: str) -> List[Token]:
        tokens: List[Token] = []
        indent_stack = [0]
        lines = code.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        for line_no, raw in enumerate(lines, start=1):
            line = raw.split("#", 1)[0]
            if not line.strip():
                tokens.append(Token("NEWLINE", "\\n", line_no))
                continue
            indent = self._count_indent(line)
            if indent > indent_stack[-1]:
                indent_stack.append(indent)
                tokens.append(Token("INDENT", "", line_no))
            while indent < indent_stack[-1]:
                indent_stack.pop()
                tokens.append(Token("DEDENT", "", line_no))
            stripped = line.lstrip(" ")
            for match in TOKEN_RE.finditer(stripped):
                value = match.group(0)
                kind = self._classify(value)
                tokens.append(Token(kind, value, line_no))
            tokens.append(Token("NEWLINE", "\\n", line_no))
        while len(indent_stack) > 1:
            indent_stack.pop()
            tokens.append(Token("DEDENT", "", line_no))
        tokens.append(Token("EOF", "", line_no))
        return tokens

    def _count_indent(self, line: str) -> int:
        count = 0
        for ch in line:
            if ch == " ":
                count += 1
            elif ch == "\t":
                count += 4
            else:
                break
        return count

    def _classify(self, value: str) -> str:
        if value.isdigit():
            return "NUMBER"
        if value.isidentifier():
            return "NAME"
        return "OP"


class PythonParser:
    def __init__(self) -> None:
        self.tokens: List[Token] = []
        self.pos = 0

    def parse(self, code: str) -> Program:
        self.tokens = PythonLexer().tokenize(code)
        self.pos = 0
        body = self._parse_block()
        return Program(body=body)

    def _parse_block(self) -> Block:
        block = Block()
        while not self._peek("EOF") and not self._peek("DEDENT"):
            stmt = self._parse_statement()
            if stmt is not None:
                block.statements.append(stmt)
        if self._peek("DEDENT"):
            self._advance()
        return block

    def _parse_statement(self):
        if self._peek_name("def"):
            return self._parse_def()
        if self._peek_name("for"):
            return self._parse_for()
        if self._peek_name("while"):
            return self._parse_while()
        self._consume_until("NEWLINE")
        return None

    def _parse_def(self) -> Function:
        self._expect_name("def")
        name = self._expect_kind("NAME").value
        if self._peek_value("("):
            self._consume_until_value(")")
        self._expect_value(":")
        self._expect_kind("NEWLINE")
        self._expect_kind("INDENT")
        body = self._parse_block()
        return Function(name=name, body=body)

    def _parse_for(self) -> Loop:
        self._expect_name("for")
        self._expect_kind("NAME")
        self._expect_name("in")
        bound = "unknown"
        if self._peek_name("range"):
            self._advance()
            if self._peek_value("("):
                self._consume_until_value(")")
            bound = "linear"
        else:
            self._consume_until_value(":")
        self._expect_value(":")
        self._expect_kind("NEWLINE")
        self._expect_kind("INDENT")
        body = self._parse_block()
        return Loop(kind="for", bound=bound, body=body)

    def _parse_while(self) -> Loop:
        self._expect_name("while")
        cond_tokens = self._collect_until_value(":")
        self._expect_value(":")
        self._expect_kind("NEWLINE")
        self._expect_kind("INDENT")
        body_start = self.pos
        body = self._parse_block()
        body_tokens = self.tokens[body_start:self.pos]
        bound = self._infer_while_bound(cond_tokens, body_tokens)
        return Loop(kind="while", bound=bound, body=body)

    def _infer_while_bound(self, cond_tokens: List[Token], body_tokens: List[Token]) -> str:
        target = self._find_condition_var(cond_tokens)
        if not target:
            return "unknown"
        update = self._find_update_kind(body_tokens, target)
        if update in {"inc", "dec"}:
            return "linear"
        if update in {"mul", "div"}:
            return "log"
        return "unknown"

    def _find_condition_var(self, cond_tokens: List[Token]) -> Optional[str]:
        for tok in cond_tokens:
            if tok.kind == "NAME":
                return tok.value
        return None

    def _find_update_kind(self, tokens: List[Token], var_name: str) -> Optional[str]:
        values = [tok.value for tok in tokens]
        for i, tok in enumerate(values):
            if tok != var_name:
                continue
            if i + 1 < len(values) and values[i + 1] in {"+=", "-="}:
                return "inc" if values[i + 1] == "+=" else "dec"
            if i + 1 < len(values) and values[i + 1] in {"*=", "/="}:
                return "mul" if values[i + 1] == "*=" else "div"
            if i + 3 < len(values) and values[i + 1] == "=" and values[i + 2] == var_name:
                if values[i + 3] in {"+", "-"}:
                    return "inc" if values[i + 3] == "+" else "dec"
                if values[i + 3] in {"*", "/"}:
                    return "mul" if values[i + 3] == "*" else "div"
        return None

    def _peek(self, kind: str) -> bool:
        return self.tokens[self.pos].kind == kind

    def _peek_value(self, value: str) -> bool:
        return self.tokens[self.pos].value == value

    def _peek_name(self, value: str) -> bool:
        tok = self.tokens[self.pos]
        return tok.kind == "NAME" and tok.value == value

    def _advance(self) -> Token:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def _expect_kind(self, kind: str) -> Token:
        tok = self._advance()
        return tok if tok.kind == kind else tok

    def _expect_value(self, value: str) -> Token:
        tok = self._advance()
        return tok if tok.value == value else tok

    def _expect_name(self, value: str) -> Token:
        tok = self._advance()
        return tok if tok.kind == "NAME" and tok.value == value else tok

    def _consume_until(self, kind: str) -> None:
        while not self._peek(kind) and not self._peek("EOF"):
            self._advance()
        if self._peek(kind):
            self._advance()

    def _consume_until_value(self, value: str) -> None:
        while not self._peek_value(value) and not self._peek("EOF"):
            self._advance()
        if self._peek_value(value):
            self._advance()

    def _collect_until_value(self, value: str) -> List[Token]:
        buf: List[Token] = []
        while not self._peek_value(value) and not self._peek("EOF"):
            buf.append(self._advance())
        return buf
