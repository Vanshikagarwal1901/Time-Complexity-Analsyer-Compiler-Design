# Data Pipeline

## Overview
The data pipeline describes how input source code is transformed through different compiler phases to produce time complexity output.

## Pipeline Stages

### 1. Input Stage
- Mini-C source code provided as input file

### 2. Lexical Analysis
- Source code converted into tokens
- Invalid tokens rejected

### 3. Syntax Analysis
- Tokens parsed using grammar rules
- AST constructed

### 4. Semantic Analysis
- Symbol table generation
- Scope and type validation
- Loop and recursion validation

### 5. Complexity Analysis
- AST traversal
- Complexity rule application
- Final complexity estimation

## Output
- Error messages (if any)
- Time complexity in Big-O notation

## Pipeline Characteristics
- Linear, phase-based flow
- Fail-fast error handling
- Deterministic output