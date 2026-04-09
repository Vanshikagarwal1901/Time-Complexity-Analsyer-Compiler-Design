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


def _auto_fix_common_cases(source: str, syntax_diags, semantic_diags) -> str:
    lines = source.splitlines()

    # Fix missing semicolon after return when parser reports it.
    if any("Expected ';' after return" in d.message for d in syntax_diags):
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("return ") and not stripped.endswith(";"):
                lines[i] = line + ";"

    # Fix common type mismatch case: int var = "5"; -> int var = 5;
    for d in semantic_diags:
        m = re.search(r"cannot assign 'char\*' to 'int' variable '([A-Za-z_][A-Za-z0-9_]*)'", d.message)
        if not m:
            continue
        var = m.group(1)
        assign_re = re.compile(rf"(\bint\s+{re.escape(var)}\s*=\s*)\"([0-9]+)\"(\s*;)")
        for i, line in enumerate(lines):
            lines[i] = assign_re.sub(r"\g<1>\2\3", line)

    return "\n".join(lines)


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
                "codegen": format_codegen(report.target_code),
                "complexity_detail": "\n".join(report.complexity_steps),
                "guided_feedback": build_guided_feedback(source, report.syntax_errors, report.semantic_errors),
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
    host = "127.0.0.1"
    port = 8000
    server = ThreadingHTTPServer((host, port), AnalyzerHandler)
    print(f"Server running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
