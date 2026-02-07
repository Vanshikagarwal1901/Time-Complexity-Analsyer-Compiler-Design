from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Complexity:
    degree: int = 0
    log_power: int = 0
    unknown: bool = False

    def multiply(self, other: "Complexity") -> "Complexity":
        if self.unknown or other.unknown:
            return Complexity(unknown=True)
        return Complexity(self.degree + other.degree, self.log_power + other.log_power)

    def max_with(self, other: "Complexity") -> "Complexity":
        if self.unknown:
            return self
        if other.unknown:
            return other
        if self.degree != other.degree:
            return self if self.degree > other.degree else other
        if self.log_power != other.log_power:
            return self if self.log_power > other.log_power else other
        return self

    def __str__(self) -> str:
        if self.unknown:
            return "O(?)"
        if self.degree == 0 and self.log_power == 0:
            return "O(1)"
        parts = []
        if self.degree == 1:
            parts.append("n")
        elif self.degree > 1:
            parts.append(f"n^{self.degree}")
        if self.log_power == 1:
            parts.append("log n")
        elif self.log_power > 1:
            parts.append(f"(log n)^{self.log_power}")
        return "O(" + " ".join(parts) + ")"
