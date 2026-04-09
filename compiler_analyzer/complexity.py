from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class ComplexityResult:
    complexity: str
    steps: List[str]


@dataclass
class LoopFactor:
    n_power: int = 0
    log_power: int = 0

    def mul(self, other: "LoopFactor") -> "LoopFactor":
        return LoopFactor(self.n_power + other.n_power, self.log_power + other.log_power)


class ComplexityAnalyzer:
    def analyze(self, source: str) -> ComplexityResult:
        steps: List[str] = []
        lines = source.splitlines()

        # First check for specialized algorithms (merge sort, quick sort, jump search)
        specialized = self._detect_special_algorithms(source)
        if specialized is not None:
            complexity, extra_steps = specialized
            steps.extend(extra_steps)
            steps.append(f"Final time complexity: {complexity}.")
            return ComplexityResult(complexity=complexity, steps=steps)

        recursion = self._detect_recursion(source)
        loop_factors, max_factor = self._analyze_loops(lines)

        for line_no, factor, reason in loop_factors:
            steps.append(f"Line {line_no}: {reason} -> contributes {self._format_factor(factor)}.")

        # Use recursion tree analysis if recursion detected
        if recursion["pattern"] is not None:
            complexity = self._apply_recursion_tree_analysis(recursion, steps)
            steps.append(f"Final time complexity: {complexity}.")
            return ComplexityResult(complexity=complexity, steps=steps)

        # Fallback to old behavior if no pattern detected
        if recursion["double"]:
            steps.append("Detected branching recursion (two or more self-calls per level).")
            steps.append("Each level branches into multiple subproblems.")
            steps.append("Final time complexity: O(2^n).")
            return ComplexityResult(complexity="O(2^n)", steps=steps)

        base = max_factor if max_factor else LoopFactor()
        if recursion["single"]:
            steps.append("Detected single recursion pattern: one recursive call per level.")
            base = base.mul(LoopFactor(n_power=1))

        complexity = self._format_factor(base)
        steps.append(f"Final time complexity: {complexity}.")
        return ComplexityResult(complexity=complexity, steps=steps)

    def _detect_special_algorithms(self, source: str) -> tuple[str, List[str]] | None:
        s = source

        # Jump Search: looks for sqrt or step-based jumping pattern
        if re.search(r"\bjumpSearch\s*\(", s):
            if re.search(r"\bsqrt\s*\(|step\s*=|step\s*\+=", s):
                return (
                    "O(√n)",
                    [
                        "Detected Jump Search pattern: block jumps with step-based iteration.",
                        "Jump phase performs about √n steps, followed by local linear scan up to √n.",
                        "Combined complexity is O(√n).",
                    ],
                )

        # Merge Sort: detects function pair with division by 2 indicating divide-and-conquer
        if re.search(r"\bmergeSort\s*\(", s) and re.search(r"\bmerge\s*\(", s):
            if re.search(r"/\s*2", s):  # Key indicator: dividing by 2 in recursion
                return (
                    "O(n log n)",
                    [
                        "Detected Merge Sort with divide-and-conquer pattern.",
                        "Two recursive calls on halved subarrays with linear merge operation.",
                        "Recurrence: T(n)=2T(n/2)+O(n) yields O(n log n) by Master Theorem.",
                    ],
                )

        # Quick Sort: detects partition-based recursion with offset patterns
        if re.search(r"\bquickSort\s*\(", s) and re.search(r"\bpartition\s*\(", s):
            # Look for typical quick sort patterns: recursive calls with pi-1 or pi+1
            if re.search(r"[\-\+]\s*1\s*[,\)]", s):  # pi-1 or pi+1 pattern
                return (
                    "O(n log n)",
                    [
                        "Detected Quick Sort with partition-based recursion.",
                        "Average case: balanced partitions yield T(n)=2T(n/2)+O(n).",
                        "Average-case complexity is O(n log n); worst-case is O(n²).",
                    ],
                )

        return None

    def _analyze_loops(self, lines: List[str]) -> tuple[List[Tuple[int, LoopFactor, str]], LoopFactor]:
        records: List[Tuple[int, LoopFactor, str]] = []
        stack: List[LoopFactor] = []
        scope_stack: List[str] = []

        max_factor = LoopFactor()
        pending_loop: LoopFactor | None = None

        for idx, raw in enumerate(lines, start=1):
            line = raw.strip()
            if not line:
                continue

            loop_factor, reason = self._classify_loop_line(line)
            if loop_factor is not None:
                current = loop_factor
                for parent in stack:
                    current = current.mul(parent)
                records.append((idx, current, reason))
                if self._dominates(current, max_factor):
                    max_factor = current
                pending_loop = loop_factor

            for ch in line:
                if ch == "{":
                    if pending_loop is not None:
                        stack.append(pending_loop)
                        scope_stack.append("loop")
                        pending_loop = None
                    else:
                        scope_stack.append("block")
                elif ch == "}":
                    if scope_stack:
                        kind = scope_stack.pop()
                        if kind == "loop" and stack:
                            stack.pop()

            if pending_loop is not None and line.endswith(";"):
                pending_loop = None

        return records, max_factor

    def _classify_loop_line(self, line: str) -> tuple[LoopFactor | None, str]:
        m_for = re.search(r"\bfor\s*\(([^;]*);([^;]*);([^)]*)\)", line)
        if m_for:
            init, cond, update = m_for.group(1).strip(), m_for.group(2).strip(), m_for.group(3).strip()
            
            # Check for multiplicative/divisive updates (logarithmic)
            if re.search(r"(\*=\s*2)|(\/=\s*2)|(>>=)|(<<=)", update):
                return LoopFactor(log_power=1), f"for-update '{update}' is multiplicative/divisive"
            
            # Check for constant-time loops (e.g., for(i=0; i<10; i++) or for(i=0; i<CONST; i++))
            if re.search(r"(\+\+)|(--)|(\+=\s*\d+)|(-=\s*\d+)", update):
                # Extract the bound from condition
                bound = self._extract_loop_bound(cond)
                if bound == "CONSTANT":
                    return LoopFactor(), f"for bound '{cond}' is constant (not dependent on n)"
                elif self._depends_on_outer(cond):
                    return LoopFactor(n_power=1), f"for bound '{cond}' depends on another index (triangular/mixed bound)"
                else:
                    # Check if bound is directly based on n (e.g., i < n, i < arr_size)
                    if self._bound_depends_on_n(cond):
                        return LoopFactor(n_power=1), f"for-update '{update}' is linear (bound: {cond})"
                    return LoopFactor(n_power=1), f"for-update '{update}' is linear"
            return LoopFactor(n_power=1), "for-loop treated as linear by default"

        m_while = re.search(r"\bwhile\s*\(([^)]*)\)", line)
        if m_while:
            cond = m_while.group(1).strip()
            if re.search(r"(high\s*<=\s*low)|(low\s*<=\s*high)|(high\s*=\s*mid)|(low\s*=\s*mid)", line):
                return LoopFactor(log_power=1), "while condition/update matches binary-search pattern"
            if re.search(r"(/\s*2)|(>>\s*1)", cond):
                return LoopFactor(log_power=1), f"while condition '{cond}' shrinks search space"
            return LoopFactor(n_power=1), "while-loop treated as linear"

        return None, ""

    def _depends_on_outer(self, cond: str) -> bool:
        # Heuristic for mixed bounds like j < i, j <= i + k.
        return bool(re.search(r"[a-zA-Z_]\w*\s*[<>]=?\s*[a-zA-Z_]\w*", cond))

    def _extract_loop_bound(self, cond: str) -> str:
        """Extract whether loop bound is constant, based on n, or variable."""
        # Check if bound is a literal decimal number (constant time)
        if re.search(r"<\s*\d+\s*($|[\&\|,)])", cond) or re.search(r"<=\s*\d+\s*($|[\&\|,)])", cond):
            return "CONSTANT"
        
        # Check for all-caps identifiers (conventionally constants like MAX, SIZE)
        if re.search(r"<\s*[A-Z_][A-Z0-9_]*\s*($|[\&\|,)])", cond) or re.search(r"<=\s*[A-Z_][A-Z0-9_]*\s*($|[\&\|,)])", cond):
            return "CONSTANT"
        
        return "VARIABLE"

    def _bound_depends_on_n(self, cond: str) -> bool:
        """Check if loop bound mentions n, size, or length (typical data size variables)."""
        return bool(re.search(r"\b(n|size|length|arr_size|len|count)\b", cond, re.IGNORECASE))

    def _apply_recursion_tree_analysis(self, rec_info: dict, steps: List[str]) -> str:
        """Apply recursion tree methodology to compute complexity.
        
        Considers:
        1. Reduction pattern (how problem size decreases each level)
        2. Branching factor (how many subproblems per level)
        3. Work per level (operations at each recursion level)
        4. Total levels (recursion depth)
        """
        pattern = rec_info["pattern"]
        calls = rec_info["calls_per_level"]
        work = rec_info["work"]
        
        # Scenario 1: Linear reduction (n → n-1) + single call
        if pattern == "linear" and calls == 1:
            steps.append(f"Recursion pattern: T(n) = T(n-1) + O({work})")
            steps.append(f"Depth: Linear (n levels, each reducing by 1)")
            steps.append(f"Work per level: {work}")
            if work == "linear":
                steps.append("Total work = n levels × O(n) per level = O(n²)")
                return "O(n²)"
            else:
                steps.append("Total work = n levels × O(1) per level = O(n)")
                return "O(n)"
        
        # Scenario 2: Logarithmic reduction (n → n/2) + single call
        if pattern == "logarithmic" and calls == 1:
            steps.append(f"Recursion pattern: T(n) = T(n/2) + O({work})")
            steps.append(f"Depth: Logarithmic (~log n levels, each halving)")
            steps.append(f"Work per level: {work}")
            if work == "linear":
                steps.append("Total work = log(n) levels × O(n) per level = O(n log n)")
                return "O(n log n)"
            else:
                steps.append("Total work = log(n) levels × O(1) per level = O(log n)")
                return "O(log n)"
        
        # Scenario 3: Linear reduction + multiple calls (branching)
        if pattern == "linear" and calls >= 2:
            steps.append(f"Recursion pattern: T(n) = {calls}*T(n-1) + O({work})")
            steps.append(f"Depth: Linear (n levels, each reducing by 1)")
            steps.append(f"Branching factor: {calls} subproblems per level")
            steps.append(f"Recursion tree has {calls}^n nodes at depth n")
            steps.append(f"Total work = O({calls}^n)")
            return f"O({calls}^n)"
        
        # Scenario 4: Logarithmic reduction + multiple calls
        if pattern == "logarithmic" and calls >= 2:
            steps.append(f"Recursion pattern: T(n) = {calls}*T(n/2) + O({work})")
            steps.append(f"Depth: Logarithmic (~log n levels)")
            steps.append(f"Branching factor: {calls} subproblems per level")
            if calls == 2:
                steps.append("Each level has 2× nodes from previous level")
                steps.append("Total nodes grow exponentially initially, then narrow at base")
                if work == "linear":
                    steps.append("Total work = O(n log n) (linear work dominates)")
                    return "O(n log n)"
                else:
                    steps.append("Total work = O(n) (combines levels efficiently)")
                    return "O(n)"
            else:
                steps.append(f"Each level has {calls}× nodes from previous level")
                steps.append(f"Total work = O(n^log₂({calls}))")
                return f"O(n^{calls//2})" if calls > 2 else "O(n)"
        
        # Default fallback
        if calls >= 2:
            return "O(2^n)"
        return "O(n)"

    def _detect_recursion(self, source: str) -> dict:
        """Analyze recursion using recursion tree methodology: pattern, depth, and work.
        
        Returns:
            dict with keys:
            - pattern: 'linear' (n-1), 'logarithmic' (n/2), 'constant' (n-c), 'branching', or None
            - depth: estimated recursion depth
            - calls_per_level: number of recursive calls per level
            - work: estimated work per level ('linear', 'constant', 'n_power', etc.)
        """
        fn_pattern = re.compile(r"(?:int|float|double|char|void|bool|long|short)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")
        function_names = fn_pattern.findall(source)
        
        result = {
            "pattern": None,
            "depth": None,
            "calls_per_level": 0,
            "work": "constant",
            "single": False,
            "double": False,
        }
        
        lines = source.splitlines()
        
        for fn in set(function_names):
            if fn == "main":
                continue
            
            # Find function body
            start = None
            for i, raw in enumerate(lines):
                if re.search(rf"\b{re.escape(fn)}\s*\(", raw):
                    start = i
                    break
            if start is None:
                continue
            
            body_lines: List[str] = []
            depth = 0
            entered = False
            for raw in lines[start:]:
                if "{" in raw:
                    entered = True
                if entered:
                    body_lines.append(raw)
                    depth += raw.count("{")
                    depth -= raw.count("}")
                    if depth <= 0:
                        break
            
            body = "\n".join(body_lines)
            
            # Count recursive calls, accounting for if/else control flow
            calls = self._count_actual_recursive_calls(body, fn)
            if calls <= 0:
                continue

            result["calls_per_level"] = max(result["calls_per_level"], calls)
            
            if calls == 1:
                result["single"] = True
            elif calls >= 2:
                result["double"] = True
            
            # Analyze reduction pattern (how n decreases in recursive calls)
            pattern = self._analyze_reduction_pattern(body, fn)
            if pattern is not None:
                result["pattern"] = pattern
            
            # Estimate recursion depth based on pattern
            if pattern == "linear":  # n-1, n-k
                result["depth"] = "O(n)"
            elif pattern == "logarithmic":  # n/2, n/10
                result["depth"] = "O(log n)"
            elif pattern == "constant":  # n-1
                result["depth"] = "O(n)"
            else:  # unknown pattern
                result["depth"] = "O(n)"
            
            # Analyze work done at each recursion level (loops, operations)
            if re.search(r"\bfor\b.*\bn\b", body):
                result["work"] = "linear"
            elif re.search(r"\bwhile\b.*\bn\b", body):
                result["work"] = "linear"
        
        return result
    
    def _analyze_reduction_pattern(self, body: str, fn_name: str) -> str:
        """Analyze how problem size reduces in recursive calls.
        
        Patterns (checked in priority order):
        - 'logarithmic': Division/binary reduction (n/2, n/10, modulo)
        - 'linear': Linear reduction (n-1, n-k, decrement)
        - None: Cannot determine pattern
        
        Priority matters: division/modulo take precedence to catch binary search, gcd correctly
        """
        # HIGH PRIORITY: Look for division/multiplication (logarithmic) - check FIRST
        # This catches mid = (left + right) / 2 patterns and modulo patterns
        if re.search(r"\(\s*\w+\s*\+\s*\w+\s*\)\s*/\s*2", body):  # (left + right) / 2
            return "logarithmic"
        if re.search(rf"\b{re.escape(fn_name)}\s*\([^)]*[/]\s*2", body):
            return "logarithmic"
        if re.search(rf"\b{re.escape(fn_name)}\s*\([^)]*>>\s*1", body):
            return "logarithmic"
        # Modulo is logarithmic (used in GCD, Euclidean algorithm)
        if re.search(r"%|mod", body, re.IGNORECASE):
            if re.search(rf"\b{re.escape(fn_name)}\s*\(", body):
                return "logarithmic"
        # Generic log indicators
        if re.search(r"log", body, re.IGNORECASE):
            if re.search(rf"\b{re.escape(fn_name)}\s*\(", body):
                return "logarithmic"
        
        # LOWER PRIORITY: Look for linear reduction patterns
        if re.search(rf"\b{re.escape(fn_name)}\s*\([^)]*-\s*1\s*[,)]", body):
            return "linear"
        if re.search(rf"\b{re.escape(fn_name)}\s*\([^)]*--", body):
            return "linear"
        if re.search(rf"\b{re.escape(fn_name)}\s*\([^)]*-\s*\d+", body):
            return "constant"
        
        return None
    
    def _count_actual_recursive_calls(self, body: str, fn_name: str) -> int:
        """Count recursive calls, accounting for if/else control flow.
        
        Logic:
        - Subtract 1 for the function definition line (appears in body)
        - Calls in sequences (arithmetic expressions): count all
        - Calls in if/else branches: count as 1 (only one branch executes)
        - Return the effective branching factor
        """
        # Count all calls to this function in its body
        call_matches = re.findall(rf"\b{re.escape(fn_name)}\s*\(", body)
        total_calls = max(0, len(call_matches) - 1)  # Subtract function definition occurrence
        
        # No self-call means not recursive.
        if total_calls == 0:
            return 0

        # Single self-call means linear recursion.
        if total_calls == 1:
            return 1
        
        # Check if all calls are in if/else/switch branches
        # Extract lines that have recursive calls
        lines_with_calls = []
        for i, line in enumerate(body.split('\n')):
            if re.search(rf"\b{re.escape(fn_name)}\s*\(", line):
                lines_with_calls.append((i, line))
        
        # If no calls found after stripping, defensive return
        if not lines_with_calls:
            return 1
        
        # Heuristic: if calls appear in arithmetic operations on same line, they're both executed
        # Example: fibonacci(n-1) + fibonacci(n-2) → 2 executed
        for linenum, line in lines_with_calls:
            # Remove comments
            line = re.sub(r'//.*$', '', line)
            calls_in_line = len(re.findall(rf"\b{re.escape(fn_name)}\s*\(", line))
            
            # Check for arithmetic operators between calls
            if calls_in_line >= 2:
                # Check if they're separated by +, -, *, / (they execute together)
                if re.search(r'[\+\-\*/]', line):
                    return calls_in_line
        
        # Check if we have if/else branches
        all_in_branches = True
        for linenum, line in lines_with_calls:
            if not re.search(r'if\s*\(|else|switch|case', line):
                # This call is not in a branch
                if linenum > 0:
                    prev_line = body.split('\n')[linenum - 1]
                    if not re.search(r'if\s*\(|else|switch|case', prev_line):
                        all_in_branches = False
                        break
        
        if all_in_branches and total_calls > 0:
            # Calls are in if/else, only one executes
            return 1
        
        # Multiple calls that all execute
        return total_calls

    def _format_factor(self, factor: LoopFactor) -> str:
        if factor.n_power == 0 and factor.log_power == 0:
            return "O(1)"
        n_part = ""
        if factor.n_power == 1:
            n_part = "n"
        elif factor.n_power > 1:
            n_part = f"n^{factor.n_power}"
        log_part = ""
        if factor.log_power == 1:
            log_part = "log n"
        elif factor.log_power > 1:
            log_part = f"(log n)^{factor.log_power}"

        if n_part and log_part:
            return f"O({n_part} {log_part})"
        if n_part:
            return f"O({n_part})"
        if log_part:
            return f"O({log_part})"
        return "O(1)"

    def _dominates(self, a: LoopFactor, b: LoopFactor) -> bool:
        # Lexicographic by n power first, then log power.
        return (a.n_power, a.log_power) > (b.n_power, b.log_power)
