from __future__ import annotations

import argparse
from pathlib import Path

from .analyzer import analyze_program
from .parsers import CParser, PythonParser
from .web.server import run_server


def main() -> None:
    parser = argparse.ArgumentParser(description="Time complexity analyzer")
    parser.add_argument("--file", type=str, help="Path to input file")
    parser.add_argument("--lang", type=str, default="auto", choices=["auto", "c", "cpp", "py"])
    parser.add_argument("--web", action="store_true", help="Run minimal web UI")
    args = parser.parse_args()

    if args.web:
        run_server()
        return

    if not args.file:
        raise SystemExit("--file is required unless --web is used")

    path = Path(args.file)
    code = path.read_text(encoding="utf-8")
    lang = args.lang
    if lang == "auto":
        if path.suffix in {".c", ".h"}:
            lang = "c"
        elif path.suffix in {".cpp", ".cc", ".hpp"}:
            lang = "cpp"
        else:
            lang = "py"

    if lang in {"c", "cpp"}:
        program = CParser().parse(code)
    else:
        program = PythonParser().parse(code)

    complexity = analyze_program(program)
    print(str(complexity))
