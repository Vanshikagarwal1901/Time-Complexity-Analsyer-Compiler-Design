from __future__ import annotations

import re
from typing import List


TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|\d+|==|!=|<=|>=|\+\+|--|\+=|-=|\*=|/=|\+|\-|\*|/|=|<|>|\(|\)|\{|\}|;|,")


class CLexer:
    def tokenize(self, code: str) -> List[str]:
        return TOKEN_RE.findall(code)
