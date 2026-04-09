# Data Strategy

## Data Sources
- User-provided Mini-C source code files
- Static code structures extracted during compilation phases

## Data Types
- Raw source code (text)
- Token streams
- Abstract Syntax Tree (AST) nodes
- Symbol tables
- Complexity metadata

## Data Usage
- Tokens used for syntax validation
- AST used for semantic analysis
- Semantic metadata used for complexity inference

## Data Storage
- In-memory data structures
- No persistent data storage required

## Data Validation
- Token-level validation during lexical analysis
- Grammar validation during parsing
- Semantic validation using symbol tables

## Data Security
- No external data storage
- No sensitive user data handled