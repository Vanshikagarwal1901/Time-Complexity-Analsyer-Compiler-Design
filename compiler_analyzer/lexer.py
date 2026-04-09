from __future__ import annotations

from typing import List, Tuple

from .models import Diagnostic, Token


KEYWORDS = {
    "auto", "break", "case", "char", "const", "continue", "default", "do", "double",
    "else", "enum", "extern", "float", "for", "goto", "if", "inline", "int", "long",
    "register", "return", "short", "signed", "sizeof", "static", "struct", "switch",
    "typedef", "union", "unsigned", "void", "volatile", "while", "bool", "class",
    "namespace", "new", "delete", "public", "private", "protected", "template", "using",
    "true", "false", "nullptr", "try", "catch", "throw",
}

TYPES = {"int", "float", "double", "char", "void", "bool", "long", "short", "unsigned", "signed"}

MULTI_OPS = {
    "++", "--", "+=", "-=", "*=", "/=", "%=", "==", "!=", "<=", ">=", "&&", "||",
    "->", "::", "<<", ">>", "<<=", ">>=", "&=", "|=", "^=",
}

SINGLE_OPS = set("+-*/%=<>!&|^~?:")
SYMBOLS = set("(){}[];,.")


class Lexer:
    def tokenize(self, source: str) -> Tuple[List[Token], List[Diagnostic]]:
        tokens: List[Token] = []
        errors: List[Diagnostic] = []

        i = 0
        line = 1
        col = 1
        n = len(source)

        def peek(offset: int = 0) -> str:
            idx = i + offset
            return source[idx] if idx < n else ""

        while i < n:
            ch = source[i]

            if ch == "\n":
                i += 1
                line += 1
                col = 1
                continue

            if ch in " \t\r":
                i += 1
                col += 1
                continue

            if ch == "/" and peek(1) == "/":
                while i < n and source[i] != "\n":
                    i += 1
                    col += 1
                continue

            if ch == "/" and peek(1) == "*":
                i += 2
                col += 2
                closed = False
                while i < n:
                    if source[i] == "\n":
                        line += 1
                        col = 1
                        i += 1
                        continue
                    if source[i] == "*" and peek(1) == "/":
                        i += 2
                        col += 2
                        closed = True
                        break
                    i += 1
                    col += 1
                if not closed:
                    errors.append(Diagnostic(
                        phase="Lexical Analysis",
                        level="error",
                        message="Unterminated block comment.",
                        line=line,
                        column=col,
                        suggestion="Close comments with */.",
                    ))
                continue

            if ch == "#":
                start_line, start_col = line, col
                value = ""
                while i < n and source[i] != "\n":
                    value += source[i]
                    i += 1
                    col += 1
                tokens.append(Token("PREPROCESSOR", value.strip(), start_line, start_col))
                continue

            if ch == '"':
                start_line, start_col = line, col
                value = ch
                i += 1
                col += 1
                terminated = False
                while i < n:
                    c = source[i]
                    value += c
                    i += 1
                    col += 1
                    if c == "\\" and i < n:
                        value += source[i]
                        i += 1
                        col += 1
                        continue
                    if c == '"':
                        terminated = True
                        break
                    if c == "\n":
                        line += 1
                        col = 1
                if not terminated:
                    errors.append(Diagnostic(
                        phase="Lexical Analysis",
                        level="error",
                        message="Unterminated string literal.",
                        line=start_line,
                        column=start_col,
                        suggestion="Add closing double quote.",
                    ))
                tokens.append(Token("STRING", value, start_line, start_col))
                continue

            if ch == "'":
                start_line, start_col = line, col
                value = ch
                i += 1
                col += 1
                terminated = False
                while i < n:
                    c = source[i]
                    value += c
                    i += 1
                    col += 1
                    if c == "\\" and i < n:
                        value += source[i]
                        i += 1
                        col += 1
                        continue
                    if c == "'":
                        terminated = True
                        break
                if not terminated:
                    errors.append(Diagnostic(
                        phase="Lexical Analysis",
                        level="error",
                        message="Unterminated character literal.",
                        line=start_line,
                        column=start_col,
                        suggestion="Add closing single quote.",
                    ))
                tokens.append(Token("CHAR", value, start_line, start_col))
                continue

            if ch.isdigit() or (ch == "." and peek(1).isdigit()):
                start_col = col
                value = ch
                i += 1
                col += 1
                while i < n and (source[i].isalnum() or source[i] in "._"):
                    value += source[i]
                    i += 1
                    col += 1
                tokens.append(Token("NUMBER", value, line, start_col))
                continue

            if ch.isalpha() or ch == "_":
                start_col = col
                value = ch
                i += 1
                col += 1
                while i < n and (source[i].isalnum() or source[i] == "_"):
                    value += source[i]
                    i += 1
                    col += 1
                if value in TYPES:
                    kind = "TYPE"
                elif value in KEYWORDS:
                    kind = "KEYWORD"
                else:
                    kind = "IDENTIFIER"
                tokens.append(Token(kind, value, line, start_col))
                continue

            two = source[i : i + 2]
            three = source[i : i + 3]
            if three in MULTI_OPS:
                tokens.append(Token("OPERATOR", three, line, col))
                i += 3
                col += 3
                continue
            if two in MULTI_OPS:
                tokens.append(Token("OPERATOR", two, line, col))
                i += 2
                col += 2
                continue

            if ch in SINGLE_OPS:
                tokens.append(Token("OPERATOR", ch, line, col))
                i += 1
                col += 1
                continue

            if ch in SYMBOLS:
                tokens.append(Token("SYMBOL", ch, line, col))
                i += 1
                col += 1
                continue

            errors.append(Diagnostic(
                phase="Lexical Analysis",
                level="error",
                message=f"Illegal character: {ch}",
                line=line,
                column=col,
                suggestion="Remove the character or replace it with a valid C/C++ symbol.",
            ))
            tokens.append(Token("INVALID", ch, line, col))
            i += 1
            col += 1

        return tokens, errors
