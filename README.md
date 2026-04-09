# Compiler + Time Complexity Analyzer (C/C++)

An educational, modular project that simulates key compiler phases and derives Big-O time complexity with step-by-step reasoning.

## Features

- Lexical Analysis
  - Tokenization into keywords, identifiers, operators, constants, symbols
  - Lexical error detection (illegal characters, unterminated literals/comments)
- Syntax Analysis
  - Lightweight recursive-descent parser
  - Line/column syntax diagnostics with beginner-friendly suggestions
- Semantic Analysis
  - Undeclared variable checks
  - Duplicate declarations
  - Basic type mismatch checks
  - Unused variable warnings
- Intermediate Code Generation
  - Three Address Code style instructions
  - Function, assignment, loop, and return IR patterns
- Optimization
  - Constant folding
  - Dead code elimination
  - Common subexpression elimination
  - Before vs After view
- Code Generation
  - IR to pseudo assembly mapping
- Time Complexity (Core)
  - Loop pattern detection: i++, i--, i*=2, i/=2
  - Nested loop depth handling
  - Recursion detection (single and double recursion)
  - Final complexity + derivation steps

## Project Structure

- `main.py`: CLI entry point
- `compiler_analyzer/models.py`: Shared data models
- `compiler_analyzer/lexer.py`: Lexical analyzer
- `compiler_analyzer/parser.py`: Syntax analyzer
- `compiler_analyzer/semantic.py`: Semantic analyzer
- `compiler_analyzer/ir.py`: Intermediate code generator
- `compiler_analyzer/optimizer.py`: Optimization passes
- `compiler_analyzer/codegen.py`: Pseudo target code generator
- `compiler_analyzer/complexity.py`: Time complexity analyzer
- `compiler_analyzer/reporter.py`: Structured report formatter
- `compiler_analyzer/engine.py`: Pipeline orchestrator
- `samples/*.c`: Ready-to-run examples

## Run

```bash
python main.py samples/linear_search.c
python main.py samples/binary_search.c
python main.py samples/fibonacci.c
python main.py samples/semantic_error.c --save report.txt
```

## Output Sections

The report is printed with clear headings:

1. Lexical Analysis
2. Syntax Analysis
3. Semantic Analysis
4. Intermediate Code (TAC)
5. Optimization
6. Code Generation
7. Time Complexity

## Example Input

```c
int sumN(int n) {
    int s = 0;
    for (int i = 0; i < n; i++) {
        s = s + i;
    }
    return s;
}
```

## Example Output (excerpt)

```text
=== Time Complexity ===
Final Complexity: O(n)
Derivation Steps:
- Line 3: detected linear loop update 'i++' -> contributes O(n).
- Final time complexity: O(n).
```

## Notes on Accuracy

This tool is designed for academic clarity and phase-by-phase explanation. It uses safe, explainable heuristics instead of heavyweight compiler frameworks. For production-grade C/C++ conformance, full grammar + AST frameworks are needed, but this project intentionally stays lightweight and readable.
