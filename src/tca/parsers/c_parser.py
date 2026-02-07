from __future__ import annotations

import re
from typing import List, Optional, Tuple

from ..ast_nodes import Block, Loop, Program


TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|\d+|==|!=|<=|>=|\+\+|--|\+=|-=|\*=|/=|\+|\-|\*|/|=|<|>|\(|\)|\{|\}|;|,")


class CParser:
    def parse(self, code: str) -> Program:
        tokens = TOKEN_RE.findall(code)
        block, _ = self._parse_block(tokens, 0, stop_token=None)
        return Program(body=block)

    def _parse_block(self, tokens: List[str], i: int, stop_token: Optional[str]) -> Tuple[Block, int]:
        block = Block()
        while i < len(tokens):
            if stop_token and tokens[i] == stop_token:
                return block, i + 1
            tok = tokens[i]
            if tok == "for":
                loop, i = self._parse_for(tokens, i)
                block.statements.append(loop)
                continue
            if tok == "while":
                loop, i = self._parse_while(tokens, i)
                block.statements.append(loop)
                continue
            if tok == "{":
                _, i = self._parse_block(tokens, i + 1, stop_token="}")
                continue
            i = self._skip_statement(tokens, i)
        return block, i

    def _parse_for(self, tokens: List[str], i: int) -> Tuple[Loop, int]:
        i = i + 1
        i = self._expect(tokens, i, "(")
        header, i = self._collect_until(tokens, i, ")")
        init, cond, update = self._split_for_header(header)
        bound = self._infer_for_bound(cond, update)
        body, i = self._parse_loop_body(tokens, i)
        return Loop(kind="for", bound=bound, body=body), i

    def _parse_while(self, tokens: List[str], i: int) -> Tuple[Loop, int]:
        i = i + 1
        i = self._expect(tokens, i, "(")
        cond, i = self._collect_until(tokens, i, ")")
        body, i, body_tokens = self._parse_loop_body(tokens, i)
        bound = self._infer_while_bound(cond, body_tokens)
        return Loop(kind="while", bound=bound, body=body), i

    def _parse_loop_body(self, tokens: List[str], i: int) -> Tuple[Block, int, List[str]]:
        if i < len(tokens) and tokens[i] == "{":
            body_tokens, next_i = self._collect_braced_tokens(tokens, i)
            block, _ = self._parse_block(body_tokens, 0, stop_token=None)
            return block, next_i, body_tokens
        if i < len(tokens) and tokens[i] in {"for", "while"}:
            if tokens[i] == "for":
                loop, next_i = self._parse_for(tokens, i)
            else:
                loop, next_i = self._parse_while(tokens, i)
            return Block(statements=[loop]), next_i, tokens[i:next_i]
        body_tokens, next_i = self._collect_until(tokens, i, ";")
        return Block(), next_i, body_tokens

    def _infer_for_bound(self, cond: List[str], update: List[str]) -> str:
        if self._is_mul_update(update) or self._is_div_update(update):
            return "log"
        if self._mentions_variable(cond):
            return "linear"
        return "unknown"

    def _infer_while_bound(self, cond: List[str], body_tokens: List[str]) -> str:
        var = self._find_var_in_cond(cond)
        if not var:
            return "unknown"
        update = self._find_update_in_tokens(body_tokens, var)
        if update in {"inc", "dec"}:
            return "linear"
        if update in {"mul", "div"}:
            return "log"
        return "unknown"

    def _find_var_in_cond(self, cond: List[str]) -> Optional[str]:
        for tok in cond:
            if re.match(r"[A-Za-z_]", tok):
                return tok
        return None

    def _find_update_in_tokens(self, tokens: List[str], var: str) -> Optional[str]:
        for i, tok in enumerate(tokens):
            if tok == var and i + 1 < len(tokens):
                nxt = tokens[i + 1]
                if nxt in {"++", "--"}:
                    return "inc" if nxt == "++" else "dec"
                if nxt in {"+=", "-="}:
                    return "inc" if nxt == "+=" else "dec"
                if nxt in {"*=", "/="}:
                    return "mul" if nxt == "*=" else "div"
        return None

    def _mentions_variable(self, tokens: List[str]) -> bool:
        for tok in tokens:
            if re.match(r"[A-Za-z_]", tok):
                return True
        return False

    def _is_mul_update(self, tokens: List[str]) -> bool:
        return "*=" in tokens or self._contains_pattern(tokens, "*", "=")

    def _is_div_update(self, tokens: List[str]) -> bool:
        return "/=" in tokens or self._contains_pattern(tokens, "/", "=")

    def _contains_pattern(self, tokens: List[str], a: str, b: str) -> bool:
        for i in range(len(tokens) - 1):
            if tokens[i] == a and tokens[i + 1] == b:
                return True
        return False

    def _split_for_header(self, header: List[str]) -> Tuple[List[str], List[str], List[str]]:
        parts: List[List[str]] = [[], [], []]
        idx = 0
        for tok in header:
            if tok == ";" and idx < 2:
                idx += 1
                continue
            parts[idx].append(tok)
        return parts[0], parts[1], parts[2]

    def _collect_until(self, tokens: List[str], i: int, token: str) -> Tuple[List[str], int]:
        buf: List[str] = []
        while i < len(tokens) and tokens[i] != token:
            buf.append(tokens[i])
            i += 1
        return buf, i + 1

    def _collect_braced_tokens(self, tokens: List[str], i: int) -> Tuple[List[str], int]:
        depth = 0
        buf: List[str] = []
        while i < len(tokens):
            tok = tokens[i]
            if tok == "{":
                depth += 1
                if depth > 1:
                    buf.append(tok)
            elif tok == "}":
                depth -= 1
                if depth == 0:
                    return buf, i + 1
                buf.append(tok)
            else:
                buf.append(tok)
            i += 1
        return buf, i

    def _skip_statement(self, tokens: List[str], i: int) -> int:
        while i < len(tokens) and tokens[i] not in {";", "}"}:
            i += 1
        if i < len(tokens) and tokens[i] == ";":
            return i + 1
        return i

    def _expect(self, tokens: List[str], i: int, tok: str) -> int:
        if i >= len(tokens) or tokens[i] != tok:
            return i
        return i + 1
