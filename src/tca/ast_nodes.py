from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class Node:
    pass


@dataclass
class Statement(Node):
    pass


@dataclass
class Block(Node):
    statements: List[Statement] = field(default_factory=list)


@dataclass
class Loop(Statement):
    kind: str
    bound: str  # "constant", "linear", "log", "unknown"
    body: Block


@dataclass
class Function(Statement):
    name: str
    body: Block


@dataclass
class Program(Node):
    body: Block
