# Software Requirement Specification (SRS)

## 1. Introduction
This document specifies the functional and non-functional requirements of the Static Time Complexity Analyzer.

## 2. Functional Requirements
- Accept Mini-C source code as input
- Perform lexical analysis and detect invalid tokens
- Perform syntax analysis based on defined grammar
- Generate an Abstract Syntax Tree (AST)
- Perform semantic analysis using symbol tables
- Detect loop nesting and recursion
- Estimate time complexity in Big-O notation

## 3. Non-Functional Requirements
- Modular architecture
- Readable and maintainable codebase
- Clear and descriptive error messages
- Extensible design for future language support

## 4. Assumptions
- Input code follows Mini-C specification
- Input size variables are symbolic (e.g., `n`)
- No dynamic memory allocation

## 5. Constraints
- Static analysis only
- No runtime execution of code