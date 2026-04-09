# Project Charter

## Project Title
A Static Time Complexity Analyzer for Mini-C Using Compiler Design Techniques

## Project Overview
This project aims to design and implement a static time complexity analyzer for a subset of the C programming language (Mini-C). The system follows a compiler front-end architecture consisting of lexical analysis, syntax analysis, semantic analysis, and abstract syntax tree (AST) construction. Based on the analyzed program structure and semantic information, the system estimates the asymptotic time complexity of the input code.

## Objectives
- Design a Mini-C language specification
- Implement lexical, syntax, and semantic analysis
- Construct an Abstract Syntax Tree (AST)
- Perform static time complexity analysis
- Follow a modular, extensible, industry-standard architecture

## Scope
### In Scope
- Mini-C language
- Loop and recursion-based complexity analysis
- Static (compile-time) analysis

### Out of Scope
- Full ANSI C support
- Runtime profiling
- Pointer and memory analysis
- Code optimization and code generation

## Stakeholders
- Student Developer(s)
- Academic Evaluators
- Compiler Design Faculty

## Success Criteria
- Correct detection of lexical and syntax errors
- Accurate semantic validation
- Correct estimation of time complexity for supported constructs
- Modular and extensible system design

## Constraints
- Limited language subset
- Static analysis only
- Academic time constraints