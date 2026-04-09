from __future__ import annotations

import argparse
from pathlib import Path

from .analyzer import analyze_program
from .parsers import CParser
from .semantic import analyze_semantics
from .web.server import run_server


def main() -> None:
    parser = argparse.ArgumentParser(description="Time complexity analyzer")
    parser.add_argument("--file", type=str, help="Path to input file")
    parser.add_argument("--web", action="store_true", help="Run minimal web UI")
    args = parser.parse_args()

    if args.web:
        run_server()
        return

    if not args.file:
        raise SystemExit("--file is required unless --web is used")

    path = Path(args.file)
    code = path.read_text(encoding="utf-8")
    program = CParser().parse(code)
    errors = analyze_semantics(program)
    if errors:
        for err in errors:
            print(f"Semantic error: {err}")
        raise SystemExit(1)

    complexity = analyze_program(program)
    print(str(complexity))
