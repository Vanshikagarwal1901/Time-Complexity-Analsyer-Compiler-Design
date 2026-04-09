from __future__ import annotations

import argparse
from pathlib import Path

from compiler_analyzer import CompilerAnalyzer
from compiler_analyzer.reporter import ReportFormatter


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Educational C/C++ Compiler + Time Complexity Analyzer"
    )
    parser.add_argument("input", type=Path, help="Path to C/C++ source file")
    parser.add_argument(
        "--save",
        type=Path,
        default=None,
        help="Optional path to save full analysis report",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    if not args.input.exists():
        print(f"Input file not found: {args.input}")
        return 1

    source = args.input.read_text(encoding="utf-8")
    analyzer = CompilerAnalyzer()
    report = analyzer.analyze(source)

    text = ReportFormatter().format(report)
    print(text)

    if args.save:
        args.save.write_text(text, encoding="utf-8")
        print(f"\nSaved report to: {args.save}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
