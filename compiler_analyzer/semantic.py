from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from .models import Diagnostic, ExprNode, ExpressionRecord, Token


@dataclass
class Symbol:
    name: str
    data_type: str
    line: int
    declared_at: int
    used: bool = False


@dataclass
class FunctionDef:
    name: str
    return_type: str
    line: int
    body_open_idx: int


NUMERIC_TYPES = {"int", "float", "double", "long", "short", "unsigned", "signed"}
TYPE_KEYWORDS = {
    "int", "float", "double", "char", "bool", "long", "short", "unsigned", "signed", "void",
    "const", "static", "inline", "extern", "constexpr",
}


class SemanticAnalyzer:
    def analyze(self, tokens: List[Token], expressions: List[ExpressionRecord]) -> tuple[List[Diagnostic], List[Diagnostic]]:
        errors: List[Diagnostic] = []
        warnings: List[Diagnostic] = []

        symbols: Dict[str, List[Symbol]] = {}
        functions: Set[str] = {
            "printf", "scanf", "cout", "cin", "endl", "malloc", "free", "strlen", "memcpy", "main",
        }
        user_defined_functions: Dict[str, int] = {}
        function_defs: List[FunctionDef] = []
        empty_main_line: Optional[int] = None

        # Stack of scope-local declaration sets for duplicate checks only.
        scope_declared: List[Set[str]] = [set()]

        i = 0
        while i < len(tokens):
            t = tokens[i]

            if t.value == "{":
                scope_declared.append(set())
                i += 1
                continue

            if t.value == "}":
                if len(scope_declared) > 1:
                    scope_declared.pop()
                i += 1
                continue

            if t.value in TYPE_KEYWORDS:
                declared_type = t.value
                i += 1
                while i < len(tokens) and tokens[i].value in TYPE_KEYWORDS.union({"*", "&"}):
                    if tokens[i].value in {"*", "&"}:
                        declared_type += tokens[i].value
                    i += 1

                # Function declaration/definition starts here: type name (...)
                if i < len(tokens) and tokens[i].kind == "IDENTIFIER" and i + 1 < len(tokens) and tokens[i + 1].value == "(":
                    fn_tok = tokens[i]
                    fn_name = fn_tok.value
                    functions.add(fn_name)

                    params, end_idx = self._extract_function_params(tokens, i + 2)
                    for p in params:
                        symbols.setdefault(p.name, []).append(p)

                    if end_idx + 1 < len(tokens) and tokens[end_idx + 1].value == "{":
                        user_defined_functions[fn_name] = fn_tok.line
                        function_defs.append(FunctionDef(
                            name=fn_name,
                            return_type=declared_type,
                            line=fn_tok.line,
                            body_open_idx=end_idx + 1,
                        ))
                        if fn_name == "main" and self._is_empty_function_body(tokens, end_idx + 1):
                            empty_main_line = fn_tok.line
                        # Continue scanning from the opening brace so local declarations are analyzed.
                        i = end_idx + 1
                    else:
                        i = end_idx + 1
                        if i < len(tokens) and tokens[i].value == ";":
                            i += 1
                    continue

                expect_decl_name = True
                depth_paren = 0
                depth_bracket = 0
                depth_brace = 0

                while i < len(tokens) and tokens[i].value != ";":
                    tok = tokens[i]
                    if tok.value == "(":
                        depth_paren += 1
                    elif tok.value == ")":
                        depth_paren = max(0, depth_paren - 1)
                    elif tok.value == "[":
                        depth_bracket += 1
                    elif tok.value == "]":
                        depth_bracket = max(0, depth_bracket - 1)
                    elif tok.value == "{":
                        depth_brace += 1
                    elif tok.value == "}":
                        depth_brace = max(0, depth_brace - 1)

                    at_top_decl_level = depth_paren == 0 and depth_bracket == 0 and depth_brace == 0

                    if tok.kind == "IDENTIFIER" and expect_decl_name and at_top_decl_level:
                        name = tok.value

                        if name in scope_declared[-1]:
                            errors.append(Diagnostic(
                                phase="Semantic Analysis",
                                level="error",
                                message=f"Multiple declaration of variable '{name}'.",
                                line=tok.line,
                                column=tok.column,
                                suggestion=f"Rename one declaration of '{name}' or remove duplicate.",
                            ))
                        else:
                            scope_declared[-1].add(name)
                            symbols.setdefault(name, []).append(
                                Symbol(name=name, data_type=declared_type, line=tok.line, declared_at=tok.line)
                            )
                        expect_decl_name = False

                    if tok.value == "," and at_top_decl_level:
                        expect_decl_name = True

                    i += 1

                if i < len(tokens) and tokens[i].value == ";":
                    i += 1
                continue

            i += 1

        # AST-driven type propagation and usage checks.
        called_functions: Set[str] = set()
        for record in expressions:
            self._collect_called_functions(record.expr, called_functions)
            expr_type = self._infer_expr_type(record.expr, symbols, functions, errors, record.line)

            if record.context in {"assign", "decl_init"} and record.target:
                target = self._resolve_symbol_at_line(record.target, record.line, symbols)
                if target is None:
                    errors.append(Diagnostic(
                        phase="Semantic Analysis",
                        level="error",
                        message=f"Undeclared variable '{record.target}' used in assignment.",
                        line=record.line,
                        column=1,
                        suggestion=f"Declare '{record.target}' before assignment.",
                    ))
                else:
                    target.used = True
                    if expr_type and not self._can_assign(target.data_type, expr_type):
                        errors.append(Diagnostic(
                            phase="Semantic Analysis",
                            level="error",
                            message=f"Type mismatch: cannot assign '{expr_type}' to '{target.data_type}' variable '{record.target}'.",
                            line=record.line,
                            column=1,
                            suggestion="Use a compatible type or cast explicitly.",
                        ))

        self._validate_function_returns(tokens, function_defs, errors)

        for sym_list in symbols.values():
            for sym in sym_list:
                if not sym.used and sym.name not in {"i", "j", "k"}:
                    warnings.append(Diagnostic(
                        phase="Semantic Analysis",
                        level="warning",
                        message=f"Variable '{sym.name}' declared but never used.",
                        line=sym.line,
                        column=1,
                        suggestion=f"Remove '{sym.name}' if unnecessary, or use it in logic.",
                    ))

        # Educational compile-readiness checks.
        for fn_name, fn_line in user_defined_functions.items():
            if fn_name != "main" and fn_name not in called_functions:
                warnings.append(Diagnostic(
                    phase="Semantic Analysis",
                    level="warning",
                    message=f"Function '{fn_name}' is defined but never called.",
                    line=fn_line,
                    column=1,
                    suggestion=f"Call '{fn_name}' from main() or remove it if unused.",
                ))

        if empty_main_line is not None:
            warnings.append(Diagnostic(
                phase="Semantic Analysis",
                level="warning",
                message="main() is empty; program entry point has no executable logic.",
                line=empty_main_line,
                column=1,
                suggestion="Call your core function(s) from main(), or add program logic there.",
            ))

        errors = self._dedupe_diagnostics(errors)
        warnings = self._dedupe_diagnostics(warnings)

        return errors, warnings

    def _validate_function_returns(self, tokens: List[Token], defs: List[FunctionDef], errors: List[Diagnostic]) -> None:
        for fn in defs:
            close_idx = self._find_matching_brace(tokens, fn.body_open_idx)
            if close_idx <= fn.body_open_idx:
                continue

            is_void = self._normalized_base_type(fn.return_type) == "void"
            for i in range(fn.body_open_idx + 1, close_idx):
                if tokens[i].value != "return":
                    continue

                has_expr = i + 1 < len(tokens) and tokens[i + 1].value != ";"
                if is_void and has_expr:
                    errors.append(Diagnostic(
                        phase="Semantic Analysis",
                        level="error",
                        message=f"Void function '{fn.name}' should not return a value.",
                        line=tokens[i].line,
                        column=tokens[i].column,
                        suggestion="Use 'return;' in void functions, or change the function return type.",
                    ))

    def _normalized_base_type(self, data_type: str) -> str:
        base = data_type
        for qualifier in ("const", "static", "inline", "extern", "constexpr"):
            base = base.replace(qualifier, "")
        return base.replace("*", "").replace("&", "").strip()

    def _dedupe_diagnostics(self, diagnostics: List[Diagnostic]) -> List[Diagnostic]:
        seen: Set[Tuple[str, str, str, int, int]] = set()
        out: List[Diagnostic] = []
        for d in diagnostics:
            key = (d.phase, d.level, d.message, d.line, d.column)
            if key in seen:
                continue
            seen.add(key)
            out.append(d)
        return out

    def _is_empty_function_body(self, tokens: List[Token], open_brace_idx: int) -> bool:
        close_idx = self._find_matching_brace(tokens, open_brace_idx)
        if close_idx <= open_brace_idx:
            return False
        body_tokens = [t for t in tokens[open_brace_idx + 1 : close_idx] if t.value not in {"{" ,"}", ";"}]
        return len(body_tokens) == 0

    def _find_matching_brace(self, tokens: List[Token], open_idx: int) -> int:
        depth = 0
        for i in range(open_idx, len(tokens)):
            if tokens[i].value == "{":
                depth += 1
            elif tokens[i].value == "}":
                depth -= 1
                if depth == 0:
                    return i
        return open_idx

    def _collect_called_functions(self, node: Optional[ExprNode], called: Set[str]) -> None:
        if node is None:
            return
        if node.kind == "call":
            called.add(node.value)
            for arg in node.args:
                self._collect_called_functions(arg, called)
            return
        self._collect_called_functions(node.left, called)
        self._collect_called_functions(node.right, called)
        for arg in node.args:
            self._collect_called_functions(arg, called)

    def _extract_function_params(self, tokens: List[Token], start_idx: int) -> tuple[List[Symbol], int]:
        params: List[Symbol] = []
        i = start_idx
        depth = 1
        current_type = ""
        while i < len(tokens) and depth > 0:
            t = tokens[i]
            if t.value == "(":
                depth += 1
            elif t.value == ")":
                depth -= 1
                if depth == 0:
                    break
            elif depth == 1:
                if t.value in TYPE_KEYWORDS:
                    current_type = t.value
                elif t.value in {"*", "&"} and current_type:
                    current_type += t.value
                elif t.kind == "IDENTIFIER" and current_type:
                    params.append(Symbol(name=t.value, data_type=current_type, line=t.line, declared_at=t.line, used=False))
                    current_type = ""
            i += 1
        return params, i

    def _resolve_symbol_at_line(self, name: str, line: int, symbols: Dict[str, List[Symbol]]) -> Optional[Symbol]:
        candidates = symbols.get(name, [])
        if not candidates:
            return None
        visible = [sym for sym in candidates if sym.declared_at <= line]
        if not visible:
            return None
        return max(visible, key=lambda s: s.declared_at)

    def _infer_expr_type(
        self,
        node: Optional[ExprNode],
        symbols: Dict[str, List[Symbol]],
        functions: Set[str],
        errors: List[Diagnostic],
        line: int,
    ) -> Optional[str]:
        if node is None:
            return None

        if node.kind == "literal":
            v = node.value
            if v.startswith('"') and v.endswith('"'):
                return "char*"
            if v.startswith("'") and v.endswith("'"):
                return "char"
            if "." in v:
                return "double"
            if v.lstrip("-").isdigit():
                return "int"
            return None

        if node.kind == "identifier":
            sym = self._resolve_symbol_at_line(node.value, line, symbols)
            if sym is None:
                errors.append(Diagnostic(
                    phase="Semantic Analysis",
                    level="error",
                    message=f"Undeclared variable '{node.value}' used.",
                    line=line,
                    column=1,
                    suggestion=f"Declare '{node.value}' before using it.",
                ))
                return None
            sym.used = True
            return sym.data_type

        if node.kind == "call":
            if node.value not in functions:
                errors.append(Diagnostic(
                    phase="Semantic Analysis",
                    level="error",
                    message=f"Call to undeclared function '{node.value}'.",
                    line=line,
                    column=1,
                    suggestion=f"Declare or define function '{node.value}' before calling it.",
                ))
            for arg in node.args:
                self._infer_expr_type(arg, symbols, functions, errors, line)
            return "int"

        if node.kind == "index":
            base_t = self._infer_expr_type(node.left, symbols, functions, errors, line)
            _ = self._infer_expr_type(node.right, symbols, functions, errors, line)
            if base_t and base_t.endswith("*"):
                return base_t[:-1].strip() or "int"
            return base_t

        if node.kind == "unary":
            return self._infer_expr_type(node.left, symbols, functions, errors, line)

        if node.kind == "binary":
            lt = self._infer_expr_type(node.left, symbols, functions, errors, line)
            rt = self._infer_expr_type(node.right, symbols, functions, errors, line)
            if node.value in {"==", "!=", "<", "<=", ">", ">=", "&&", "||"}:
                return "bool"
            if lt == "double" or rt == "double":
                return "double"
            if lt in NUMERIC_TYPES and rt in NUMERIC_TYPES:
                return "int"
            return lt or rt

        return None

    def _can_assign(self, lhs_type: str, rhs_type: str) -> bool:
        lhs = lhs_type.replace("const", "").strip()
        if lhs == rhs_type:
            return True
        if lhs in NUMERIC_TYPES and rhs_type in NUMERIC_TYPES:
            return True
        if lhs == "char*" and rhs_type == "char*":
            return True
        return False
