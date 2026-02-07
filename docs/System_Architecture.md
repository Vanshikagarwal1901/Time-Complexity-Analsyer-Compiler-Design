# System Architecture

## Architectural Style
Modular Compiler Front-End Architecture

## High-Level Architecture

Source Code  
↓  
Lexical Analyzer  
↓  
Syntax Analyzer  
↓  
AST Generator  
↓  
Semantic Analyzer  
↓  
Complexity Analyzer  
↓  
Result Output  

## Modules Description

### 1. Lexical Analyzer
- Tokenizes source code
- Detects invalid characters

### 2. Syntax Analyzer
- Validates grammar rules
- Builds AST

### 3. AST Module
- Represents program structure
- Enables traversal

### 4. Semantic Analyzer
- Builds symbol tables
- Validates loop and recursion semantics

### 5. Complexity Analyzer
- Applies rule-based inference
- Produces Big-O complexity

## Design Principles
- Separation of concerns
- Loose coupling
- High cohesion
- Extensible modules

## Technology Stack
- Programming Language: C++ (recommended)
- Tools: Flex / Custom Parser