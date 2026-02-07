# Time Complexity Analyzer (Compiler Design Project)

This project is a small, compiler-style time complexity analyzer for C/C++ and Python. It follows classic compiler phases:

1) Lexing and parsing (language-specific front-end)
2) AST construction (language-agnostic nodes)
3) Semantic analysis (loop-bound detection)
4) Complexity composition (Big-O for blocks and functions)

## Scope (current)

- Supports a focused subset of C/C++ and Python
- Detects loop nesting and common loop forms
- Outputs Big-O (e.g., O(1), O(n), O(n^2), O(n log n))

## Quick start

CLI:

```
python -m tca --file examples/python/nested_loops.py
python -m tca --file examples/c/for_loop.c
```

Minimal web UI:

```
python -m tca --web
```

Open http://localhost:8000

## Notes

This is intentionally a compiler-design style analyzer, not a full compiler. It is a teaching tool with explicit stages and a clear AST. The C/C++ and Python front-ends are small hand-rolled lexers/parsers for loop and block structures only.
