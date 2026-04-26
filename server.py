from __future__ import annotations

import json
import mimetypes
import re
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from compiler_analyzer import CompilerAnalyzer


ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = ROOT / "frontend"


def format_diagnostics(diags) -> str:
    if not diags:
        return "No issues detected."
    lines = []
    for d in diags:
        lines.append(f"[{d.level.upper()}] {d.phase} at {d.line}:{d.column} - {d.message}")
        if d.suggestion:
            lines.append(f"  Suggestion: {d.suggestion}")
    return "\n".join(lines)


def format_tokens(tokens, limit: int = 200) -> str:
    if not tokens:
        return "No tokens generated."
    out = ["#   kind         value           line:col"]
    for idx, t in enumerate(tokens[:limit], start=1):
        val = t.value if len(t.value) <= 14 else t.value[:11] + "..."
        out.append(f"{idx:3} {t.kind:12} {val:14} {t.line}:{t.column}")
    if len(tokens) > limit:
        out.append(f"... {len(tokens) - limit} more tokens")
    return "\n".join(out)


def format_ir(ir_lines) -> str:
    if not ir_lines:
        return "No IR generated."
    out = []
    for idx, ins in enumerate(ir_lines, start=1):
        text = f"{ins.op} {ins.arg1} {ins.arg2} {ins.result}".strip()
        text = " ".join(text.split())
        if ins.comment:
            text += f"    ; {ins.comment}"
        out.append(f"{idx:3}. {text}")
    return "\n".join(out)


def format_codegen(lines) -> str:
    return "\n".join(lines) if lines else "No target code generated."


def build_guided_feedback(source: str, syntax_diags, semantic_diags) -> str:
    issues: list[str] = []
    for d in syntax_diags:
        issues.append(f"- Syntax: {d.message} (line {d.line})")
    for d in semantic_diags:
        issues.append(f"- Semantic: {d.message} (line {d.line})")

    if not issues:
        return "No major issues detected."

    fixed = _auto_fix_common_cases(source, syntax_diags, semantic_diags)

    out = ["Detected Issues:"]
    out.extend(issues)
    if fixed and fixed != source:
        out.append("")
        out.append("Suggested Corrected Version:")
        out.append(fixed)
    return "\n".join(out)


def build_code_suggestion(source: str, syntax_diags, semantic_diags, optimizations, optimized_code: str) -> tuple[str, str]:
    fixed = _auto_fix_common_cases(source, syntax_diags, semantic_diags)
    has_issue = bool(syntax_diags or semantic_diags)
    has_optimization = any(item != "No optimization rule was applicable." for item in (optimizations or []))

    if has_issue and fixed != source:
        return fixed, "source-fix"

    if has_optimization:
        # Keep code suggestion focused on source-level syntax/semantic correction.
        # Optimization output remains available in Optimization and Code Generation panels.
        return "", "none"

    if has_issue:
        return source, "source-original"

    return "", "none"


def _auto_fix_common_cases(source: str, syntax_diags, semantic_diags) -> str:
    lines = source.splitlines()

    # Fix missing semicolon diagnostics (parser can report the error on the next line).
    for d in syntax_diags:
        if "Expected ';'" not in d.message:
            continue

        candidate_idxs = [max(0, int(d.line) - 1), max(0, int(d.line) - 2)]
        for line_idx in candidate_idxs:
            if line_idx >= len(lines):
                continue

            raw = lines[line_idx]
            stripped = raw.strip()
            if not _looks_like_statement_needing_semicolon(stripped):
                continue

            # Prefer return-line fixes when parser explicitly points to return statements.
            if "after return" in d.message and not stripped.startswith("return"):
                continue

            lines[line_idx] = raw.rstrip() + ";"
            break

    # Fix missing ')' based on parser diagnostics.
    for d in syntax_diags:
        if "Expected ')'" not in d.message:
            continue
        candidate_idxs = [max(0, int(d.line) - 1), max(0, int(d.line) - 2)]
        for line_idx in candidate_idxs:
            if line_idx >= len(lines):
                continue
            updated = _insert_missing_closer(lines[line_idx], "(", ")")
            if updated != lines[line_idx]:
                lines[line_idx] = updated
                break

    # Fix missing ']' based on parser diagnostics.
    for d in syntax_diags:
        if "Expected ']'" not in d.message:
            continue
        candidate_idxs = [max(0, int(d.line) - 1), max(0, int(d.line) - 2)]
        for line_idx in candidate_idxs:
            if line_idx >= len(lines):
                continue
            updated = _insert_missing_closer(lines[line_idx], "[", "]")
            if updated != lines[line_idx]:
                lines[line_idx] = updated
                break

    # Fix missing closing braces for block/initializer diagnostics.
    if any(("Missing closing '}' for block." in d.message or "Unclosed initializer list." in d.message) for d in syntax_diags):
        balance = source.count("{") - source.count("}")
        while balance > 0:
            lines.append("}")
            balance -= 1

    # Fix missing semicolon after local declarations when parser reports it.
    if any("Expected ';' after local declaration" in d.message for d in syntax_diags):
        for d in syntax_diags:
            if "Expected ';' after local declaration" not in d.message:
                continue
            # Parser often reports this on the following line, so try current then previous line.
            candidate_idxs = [max(0, int(d.line) - 1), max(0, int(d.line) - 2)]
            for line_idx in candidate_idxs:
                if line_idx >= len(lines):
                    continue
                raw = lines[line_idx]
                stripped = raw.strip()
                if not stripped:
                    continue
                # Avoid adding semicolons to block headers or already-complete statements.
                if stripped.endswith((";", "{", "}")):
                    continue
                if stripped.startswith(("if ", "if(", "for ", "for(", "while ", "while(", "switch ", "switch(")):
                    continue
                if _looks_like_local_declaration(stripped):
                    lines[line_idx] = raw.rstrip() + ";"
                    break

    # Fix common type mismatch case: int var = "5"; -> int var = 5;
    for d in semantic_diags:
        m = re.search(r"cannot assign 'char\*' to 'int' variable '([A-Za-z_][A-Za-z0-9_]*)'", d.message)
        if not m:
            continue
        var = m.group(1)
        assign_re = re.compile(rf"(\bint\s+{re.escape(var)}\s*=\s*)\"([0-9]+)\"(\s*;)")
        for i, line in enumerate(lines):
            lines[i] = assign_re.sub(r"\g<1>\2\3", line)

    # Semantic-guided undeclared variable fixes.
    undeclared_vars: set[str] = set()
    for d in semantic_diags:
        m = re.search(r"Undeclared variable '([A-Za-z_][A-Za-z0-9_]*)'", d.message)
        if m:
            undeclared_vars.add(m.group(1))

    for var in undeclared_vars:
        # Prefer for-loop initializer fix: for (i = 0; ...) -> for (int i = 0; ...)
        for_idx = _find_for_initializer_line(lines, var)
        if for_idx is not None:
            lines[for_idx] = _insert_int_in_for_initializer(lines[for_idx], var)
            continue

        # Fallback: plain assignment at start of statement -> declare variable in place.
        assign_idx = _find_plain_assignment_line(lines, var)
        if assign_idx is not None:
            lines[assign_idx] = _insert_int_in_assignment(lines[assign_idx], var)

    fixed = "\n".join(lines)
    # Safety guard: never return suggestions that modify code beyond explicit allowed fixes.
    if not _only_allowed_fixes_applied(source, fixed):
        return source
    return fixed


def _looks_like_local_declaration(stripped_line: str) -> bool:
    decl_prefix = re.compile(
        r"^(?:const\s+|static\s+|unsigned\s+|signed\s+|long\s+|short\s+)*"
        r"(?:int|float|double|char|bool|size_t|long|short)\b"
    )
    if not decl_prefix.search(stripped_line):
        return False
    # Common declaration patterns that should end with semicolon.
    return "=" in stripped_line or "[" in stripped_line or "," in stripped_line


def _looks_like_statement_needing_semicolon(stripped_line: str) -> bool:
    if not stripped_line:
        return False
    if stripped_line.endswith((";", "{", "}")):
        return False
    if stripped_line.startswith(("#", "//", "/*", "*")):
        return False
    if stripped_line.startswith(("if ", "if(", "for ", "for(", "while ", "while(", "switch ", "switch(", "else", "do")):
        return False

    # Avoid adding semicolons to likely function headers/signatures.
    function_header = re.compile(
        r"^(?:const\s+|static\s+|inline\s+|unsigned\s+|signed\s+|long\s+|short\s+)*"
        r"(?:void|int|float|double|char|bool|size_t|long|short)\s+[*&\sA-Za-z_][\w\s\*&]*\([^)]*\)$"
    )
    if function_header.search(stripped_line):
        return False

    # Typical fixable statement forms.
    return (
        stripped_line.startswith("return")
        or "=" in stripped_line
        or "(" in stripped_line
        or _looks_like_local_declaration(stripped_line)
    )


def _only_allowed_fixes_applied(original_source: str, fixed_source: str) -> bool:
    original_lines = original_source.splitlines()
    fixed_lines = fixed_source.splitlines()
    if len(fixed_lines) < len(original_lines):
        return False

    # Allow only trailing synthetic '}' lines when source has unclosed blocks.
    if len(fixed_lines) > len(original_lines):
        extra = fixed_lines[len(original_lines) :]
        if any(item.strip() != "}" for item in extra):
            return False
        fixed_lines = fixed_lines[: len(original_lines)]

    for before, after in zip(original_lines, fixed_lines):
        if before == after:
            continue
        if _is_semicolon_append_change(before, after):
            continue
        if _is_int_string_literal_unquote_change(before, after):
            continue
        if _is_for_initializer_declaration_fix(before, after):
            continue
        if _is_assignment_declaration_fix(before, after):
            continue
        if _is_single_closer_insertion_change(before, after):
            continue
        return False
    return True


def _is_semicolon_append_change(before: str, after: str) -> bool:
    return after.rstrip() == before.rstrip() + ";"


def _is_int_string_literal_unquote_change(before: str, after: str) -> bool:
    pattern = re.compile(r"(\bint\s+[A-Za-z_][A-Za-z0-9_]*\s*=\s*)\"([0-9]+)\"(\s*;)")
    expected = pattern.sub(r"\g<1>\2\3", before)
    return expected == after and expected != before


def _is_for_initializer_declaration_fix(before: str, after: str) -> bool:
    pattern = re.compile(r"(\bfor\s*\(\s*)([A-Za-z_][A-Za-z0-9_]*)(\s*=)")
    expected = pattern.sub(r"\g<1>int \g<2>\g<3>", before, count=1)
    return expected == after and expected != before


def _is_assignment_declaration_fix(before: str, after: str) -> bool:
    pattern = re.compile(r"^(\s*)([A-Za-z_][A-Za-z0-9_]*)(\s*=)")
    expected = pattern.sub(r"\g<1>int \g<2>\g<3>", before, count=1)
    return expected == after and expected != before


def _find_for_initializer_line(lines: list[str], var: str) -> int | None:
    pattern = re.compile(rf"\bfor\s*\(\s*{re.escape(var)}\s*=")
    for idx, line in enumerate(lines):
        if pattern.search(line):
            return idx
    return None


def _find_plain_assignment_line(lines: list[str], var: str) -> int | None:
    pattern = re.compile(rf"^\s*{re.escape(var)}\s*=")
    for idx, line in enumerate(lines):
        if pattern.search(line):
            return idx
    return None


def _insert_int_in_for_initializer(line: str, var: str) -> str:
    pattern = re.compile(rf"(\bfor\s*\(\s*){re.escape(var)}(\s*=)")
    return pattern.sub(rf"\g<1>int {var}\g<2>", line, count=1)


def _insert_int_in_assignment(line: str, var: str) -> str:
    pattern = re.compile(rf"^(\s*){re.escape(var)}(\s*=)")
    return pattern.sub(rf"\g<1>int {var}\g<2>", line, count=1)


def _insert_missing_closer(line: str, open_char: str, close_char: str) -> str:
    if line.count(open_char) <= line.count(close_char):
        return line

    insert_targets = []
    if close_char == ")":
        insert_targets = ["{", ";"]
    elif close_char == "]":
        insert_targets = ["=", ",", ";", ")"]

    for target in insert_targets:
        idx = line.find(target)
        if idx > 0:
            return line[:idx] + close_char + line[idx:]

    return line.rstrip() + close_char


def _is_single_closer_insertion_change(before: str, after: str) -> bool:
    allowed = {")", "]", "}"}
    if len(after) != len(before) + 1:
        return False

    i = 0
    j = 0
    inserted = ""
    while i < len(before) and j < len(after):
        if before[i] == after[j]:
            i += 1
            j += 1
            continue
        if inserted:
            return False
        inserted = after[j]
        j += 1

    if not inserted and j < len(after):
        inserted = after[j]
        j += 1

    return i == len(before) and j == len(after) and inserted in allowed


class AnalyzerHandler(BaseHTTPRequestHandler):
    analyzer = CompilerAnalyzer()

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/":
            path = "/index.html"

        file_path = (FRONTEND_DIR / path.lstrip("/")).resolve()
        if not str(file_path).startswith(str(FRONTEND_DIR)):
            self._send_json({"error": "Forbidden"}, HTTPStatus.FORBIDDEN)
            return

        if not file_path.exists() or not file_path.is_file():
            self._send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
            return

        mime, _ = mimetypes.guess_type(file_path.name)
        mime = mime or "application/octet-stream"
        content = file_path.read_bytes()

        self.send_response(HTTPStatus.OK)
        self._send_cors_headers()
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/analyze":
            self._send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length)
            payload = json.loads(raw.decode("utf-8")) if raw else {}
            source = str(payload.get("source", "")).strip()
            if not source:
                self._send_json({"error": "source is required"}, HTTPStatus.BAD_REQUEST)
                return

            report = self.analyzer.analyze(source)
            optimized_codegen = format_codegen(report.target_code)
            suggested_code, suggested_kind = build_code_suggestion(
                source,
                report.syntax_errors,
                report.semantic_errors,
                report.optimizations_applied,
                optimized_codegen,
            )

            data = {
                "tokens_count": len(report.tokens),
                "syntax_error_count": len(report.syntax_errors),
                "semantic_error_count": len(report.semantic_errors),
                "semantic_warning_count": len(report.semantic_warnings),
                "complexity": report.complexity,
                "lexical": format_tokens(report.tokens),
                "syntax": format_diagnostics(report.syntax_errors),
                "parse_tree": report.parse_tree or "No parse tree available.",
                "semantic": "\n".join([
                    format_diagnostics(report.semantic_errors),
                    format_diagnostics(report.semantic_warnings),
                ]).strip(),
                "ir": format_ir(report.ir),
                "optimization": "\n".join(report.optimizations_applied) if report.optimizations_applied else "No optimizations.",
                "codegen": optimized_codegen,
                "complexity_detail": "\n".join(report.complexity_steps),
                "guided_feedback": build_guided_feedback(source, report.syntax_errors, report.semantic_errors),
                "suggested_code": suggested_code,
                "suggested_code_kind": suggested_kind,
            }
            self._send_json(data, HTTPStatus.OK)
        except Exception as exc:  # pragma: no cover
            self._send_json({"error": f"analysis failed: {exc}"}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def log_message(self, fmt: str, *args) -> None:
        return

    def _send_json(self, data: dict, status: HTTPStatus) -> None:
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self._send_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")


def main() -> None:
    import os
    host = "0.0.0.0"
    port = int(os.environ.get("PORT", 8000))
    server = ThreadingHTTPServer((host, port), AnalyzerHandler)
    print(f"Server running at http://{host}:{port}")
    server.serve_forever()
    
if __name__ == "__main__":
    main()
