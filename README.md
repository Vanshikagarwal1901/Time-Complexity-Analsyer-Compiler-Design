# Time Complexity Analyzer (Compiler Design Project)

This project is a small, compiler-style time complexity analyzer for C/C++ and Python. It follows classic compiler phases:

1) Lexing and parsing (language-specific front-end)
2) AST construction (language-agnostic nodes)
3) Semantic analysis (loop-bound detection)
4) Complexity composition (Big-O for blocks and functions)
# Static Time Complexity Analyzer for Mini-C

## Overview

This project implements a static time complexity analyzer for a simplified subset of the C programming language, referred to as Mini-C. The system is designed using compiler design principles and follows a compiler front-end architecture. It performs lexical analysis, syntax analysis, semantic analysis, and Abstract Syntax Tree (AST) construction to estimate the asymptotic time complexity of input programs.

The analyzer operates entirely at compile time and does not execute the input code. Time complexity is inferred by analyzing control flow structures and semantic properties of the program.

---

## Problem Statement

Manual analysis of time complexity requires strong theoretical knowledge and is prone to errors, especially for programs with nested control structures or recursion. Existing tools often rely on runtime profiling or assume predefined algorithms. This project addresses the need for a static, compiler-based approach to time complexity estimation.

---

## Objectives

- Define a simplified C-like language (Mini-C)
- Implement lexical, syntactic, and semantic analysis phases
- Construct an Abstract Syntax Tree for structural representation
- Perform static analysis to infer time complexity
- Design the system using modular and extensible software practices

---

## System Design

The system is structured as a sequence of compiler front-end phases, where each phase transforms the input into a more structured and analyzable form.

Mini-C Source Code
↓
Lexical Analysis
↓
Syntax Analysis
↓
AST Construction
↓
Semantic Analysis
↓
Time Complexity Analysis
↓
Big-O Complexity Output


---

## Supported Language Features

### Included Features
- Function definitions
- for and while loops
- Nested loop structures
- Simple recursive functions
- Integer variables
- Basic conditional expressions

### Excluded Features
- Arrays and data structures
- Pointers and memory operations
- Structures, unions, and macros
- Dynamic memory allocation
- Full ANSI C language support

The language restrictions are intentional to maintain focus on compiler front-end concepts and static analysis.

---

## Analysis Approach

- Lexical analysis converts source code into tokens.
- Syntax analysis validates the program structure using grammar rules.
- Semantic analysis builds symbol tables, validates scopes, and ensures meaningful loop and recursion semantics.
- Time complexity analysis traverses the AST and applies rule-based inference to estimate asymptotic complexity.

---

## Example Output

Lexical Analysis: Passed
Syntax Analysis: Passed
Semantic Analysis: Passed

Detected:

Loop nesting depth: 2

Loop bound dependent on input size (n)

Estimated Time Complexity: O(n^2)


---

## Testing and Validation

The system is tested using:
- Programs with known theoretical time complexities
- Invalid syntax and semantic error cases
- Edge cases such as constant-bound loops
- Manual verification against expected results

---

## Project Structure

project-root/
│
├── docs/
│ ├── Project_Charter.md
│ ├── Requirement_Specification.md
│ ├── Data_Strategy.md
│ ├── Data_Pipeline.md
│ ├── Model_Design.md
│ └── System_Architecture.md
│
├── lexer/
├── parser/
├── ast/
├── semantic/
├── analyzer/
│
├── tests/
├── main.cpp
└── README.md


---

## Limitations

- Analysis is limited to the Mini-C language specification
- Only static analysis is supported; runtime behavior is not evaluated
- No handling of pointers, arrays, or dynamic memory
- Complexity inference is rule-based and not probabilistic

---

## Future Enhancements

- Extension of the language to support arrays and data structures
- Support for additional languages such as Python and C++
- Machine learning–based complexity inference
- Visualization of Abstract Syntax Trees
- Integration with development environments and editors

---

## Academic and Practical Relevance

This project demonstrates the application of compiler design concepts in static program analysis. It is suitable for compiler design coursework, academic research prototypes, and foundational static analysis tools.

---

## License

This project is intended for academic and educational use.

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
