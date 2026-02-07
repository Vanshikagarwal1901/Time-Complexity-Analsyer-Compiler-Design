# Model Design

## Model Type
Rule-based Static Analysis Model

## Model Inputs
- Abstract Syntax Tree (AST)
- Symbol table
- Semantic metadata

## Model Logic
- Loop pattern detection
- Loop nesting depth calculation
- Recursion pattern identification
- Mathematical combination of complexities

## Complexity Rules
| Structure | Inferred Complexity |
|---------|---------------------|
| Single loop | O(n) |
| Nested loops | O(n²), O(n³) |
| Logarithmic loop | O(log n) |
| Linear recursion | O(n) |
| Exponential recursion | O(2ⁿ) |

## Model Output
- Asymptotic time complexity (Big-O)

## Extensibility
- Can be extended with ML-based inference
- Can support additional language constructs