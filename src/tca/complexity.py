from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Complexity:
    degree_num: int = 0
    degree_den: int = 1
    log_power: int = 0
    unknown: bool = False

    def multiply(self, other: "Complexity") -> "Complexity":
        if self.unknown or other.unknown:
            return Complexity(unknown=True)
        num = self.degree_num * other.degree_den + other.degree_num * self.degree_den
        den = self.degree_den * other.degree_den
        num, den = _reduce_fraction(num, den)
        return Complexity(num, den, self.log_power + other.log_power)

    def max_with(self, other: "Complexity") -> "Complexity":
        if self.unknown:
            return self
        if other.unknown:
            return other
        cmp_degree = _compare_fraction(self.degree_num, self.degree_den, other.degree_num, other.degree_den)
        if cmp_degree != 0:
            return self if cmp_degree > 0 else other
        if self.log_power != other.log_power:
            return self if self.log_power > other.log_power else other
        return self

    def __str__(self) -> str:
        if self.unknown:
            return "O(?)"
        if self.degree_num == 0 and self.log_power == 0:
            return "O(1)"
        parts = []
        if self.degree_num != 0:
            parts.append(_format_n_power(self.degree_num, self.degree_den))
        if self.log_power == 1:
            parts.append("log n")
        elif self.log_power > 1:
            parts.append(f"(log n)^{self.log_power}")
        return "O(" + " ".join(parts) + ")"


def _reduce_fraction(num: int, den: int) -> tuple[int, int]:
    if den == 0:
        return num, den
    if num == 0:
        return 0, 1
    a, b = abs(num), abs(den)
    while b:
        a, b = b, a % b
    return num // a, den // a


def _compare_fraction(a_num: int, a_den: int, b_num: int, b_den: int) -> int:
    left = a_num * b_den
    right = b_num * a_den
    if left == right:
        return 0
    return 1 if left > right else -1


def _format_n_power(num: int, den: int) -> str:
    if den == 1:
        if num == 1:
            return "n"
        return f"n^{num}"
    if num == 1 and den == 2:
        return "sqrt n"
    return f"n^({num}/{den})"
