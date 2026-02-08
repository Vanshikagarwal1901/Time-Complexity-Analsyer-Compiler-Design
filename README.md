# Static Time Complexity Analyzer for Mini-C

This project implements a static time complexity analyzer for a simplified subset of C/C++ (Mini-C). It follows compiler front-end phases: lexical analysis, syntax analysis, AST construction, semantic analysis, and complexity inference. The implementation is in Python, but the analyzed language is Mini-C.

## Compiler Pipeline

Mini-C Source Code
-> Lexical Analysis
-> Syntax Analysis
-> AST Construction
-> Semantic Analysis
-> Time Complexity Analysis
-> Big-O Output

## Supported Features

Included:
- Function definitions
- `for` and `while` loops
- Nested loops
- Integer variables
- Basic conditional expressions

Excluded:
- Arrays and data structures
- Pointers and memory operations
- Structures, unions, and macros
- Dynamic memory allocation
- Full ANSI C support

## Project Structure

project-root/
├── docs/
├── examples/
├── src/
│   └── tca/
│       ├── analyzer.py
│       ├── ast_nodes.py
│       ├── lexer/
│       ├── parsers/
│       ├── semantic.py
│       └── web/
└── README.md

## Scope

- Mini-C only (C/C++)
- Rule-based complexity inference (Big-O)
- Static analysis only (no execution)

## Quick start

CLI:

```
python -m tca --file examples/c/for_loop.c
```

Minimal web UI:

```
python -m tca --web
```

Open http://localhost:8000

## Notes

This is a teaching tool with a hand-rolled lexer and parser for a focused Mini-C subset. It is not a full compiler.
