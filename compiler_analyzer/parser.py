from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .models import Diagnostic, ExprNode, ExpressionRecord, Token


TYPE_STARTERS = {
    "int", "float", "double", "char", "void", "bool", "long", "short", "unsigned", "signed",
    "static", "const", "inline", "extern", "constexpr", "struct", "class",
}

STATEMENT_START_KEYWORDS = {"if", "for", "while", "do", "return", "break", "continue", "else", "switch", "case", "default"}


@dataclass
class ParseResult:
    errors: List[Diagnostic]
    expressions: List[ExpressionRecord] = field(default_factory=list)


class _ExprParser:
    PRECEDENCE = {
        "||": 1,
        "&&": 2,
        "==": 3,
        "!=": 3,
        "<": 4,
        "<=": 4,
        ">": 4,
        ">=": 4,
        "+": 5,
        "-": 5,
        "*": 6,
        "/": 6,
        "%": 6,
    }

    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.pos = 0

    def parse(self) -> Optional[ExprNode]:
        if not self.tokens:
            return None
        return self._parse_expr(0)

    def _parse_expr(self, min_prec: int) -> Optional[ExprNode]:
        left = self._parse_unary()
        if left is None:
            return None

        while self.pos < len(self.tokens):
            tok = self.tokens[self.pos]
            prec = self.PRECEDENCE.get(tok.value)
            if prec is None or prec < min_prec:
                break
            op = tok.value
            self.pos += 1
            right = self._parse_expr(prec + 1)
            if right is None:
                break
            left = ExprNode(kind="binary", value=op, left=left, right=right)
        return left

    def _parse_unary(self) -> Optional[ExprNode]:
        if self.pos >= len(self.tokens):
            return None
        tok = self.tokens[self.pos]
        if tok.value in {"+", "-", "!", "~", "++", "--"}:
            self.pos += 1
            node = self._parse_unary()
            return ExprNode(kind="unary", value=tok.value, left=node)
        return self._parse_primary()

    def _parse_primary(self) -> Optional[ExprNode]:
        if self.pos >= len(self.tokens):
            return None
        tok = self.tokens[self.pos]

        if tok.value == "(":
            self.pos += 1
            expr = self._parse_expr(0)
            if self.pos < len(self.tokens) and self.tokens[self.pos].value == ")":
                self.pos += 1
            return expr

        if tok.kind in {"NUMBER", "STRING", "CHAR"}:
            self.pos += 1
            return ExprNode(kind="literal", value=tok.value)

        if tok.kind == "IDENTIFIER":
            self.pos += 1
            node: ExprNode = ExprNode(kind="identifier", value=tok.value)
            while self.pos < len(self.tokens):
                if self.tokens[self.pos].value == "(":
                    self.pos += 1
                    args: List[ExprNode] = []
                    current: List[Token] = []
                    depth = 0
                    while self.pos < len(self.tokens):
                        t = self.tokens[self.pos]
                        if t.value == "(":
                            depth += 1
                            current.append(t)
                        elif t.value == ")":
                            if depth == 0:
                                if current:
                                    arg = _ExprParser(current).parse()
                                    if arg is not None:
                                        args.append(arg)
                                self.pos += 1
                                break
                            depth -= 1
                            current.append(t)
                        elif t.value == "," and depth == 0:
                            arg = _ExprParser(current).parse()
                            if arg is not None:
                                args.append(arg)
                            current = []
                        else:
                            current.append(t)
                        self.pos += 1
                    node = ExprNode(kind="call", value=node.value, args=args)
                    continue

                if self.tokens[self.pos].value == "[":
                    self.pos += 1
                    idx_tokens: List[Token] = []
                    depth = 0
                    while self.pos < len(self.tokens):
                        t = self.tokens[self.pos]
                        if t.value == "[":
                            depth += 1
                            idx_tokens.append(t)
                        elif t.value == "]":
                            if depth == 0:
                                self.pos += 1
                                break
                            depth -= 1
                            idx_tokens.append(t)
                        else:
                            idx_tokens.append(t)
                        self.pos += 1
                    idx_node = _ExprParser(idx_tokens).parse()
                    node = ExprNode(kind="index", value="[]", left=node, right=idx_node)
                    continue

                break
            return node

        if tok.value in {"[", "]", "{" , "}"}:
            self.pos += 1
            return None

        self.pos += 1
        return ExprNode(kind="unknown", value=tok.value)


class Parser:
    def __init__(self, tokens: List[Token]) -> None:
        self.raw_tokens = tokens
        self.tokens = [t for t in tokens if t.kind != "PREPROCESSOR"]
        self.pos = 0
        self.errors: List[Diagnostic] = []
        self.expressions: List[ExpressionRecord] = []
        self.defined_functions: set[str] = set()

    def parse(self) -> ParseResult:
        while not self._at_end():
            before = self.pos
            self._parse_top_level()
            if self.pos == before:
                t = self._current()
                self._error(t, f"Parser stalled near '{t.value}'.", "Remove or fix this token.")
                self._advance()
        self._post_syntax_checks()
        return ParseResult(errors=self.errors, expressions=self.expressions)

    def _parse_top_level(self) -> None:
        t = self._current()
        if t.value in {"struct", "class"}:
            self._parse_struct_or_class()
            return
        if self._is_type_start(t):
            self._parse_decl_or_function()
            return
        self._error(t, f"Unexpected token '{t.value}' at top level.", "Top level should contain declarations or function definitions.")
        self._advance()

    def _parse_struct_or_class(self) -> None:
        self._advance()
        if self._current().kind == "IDENTIFIER":
            self._advance()
        if not self._match("{"):
            t = self._current()
            self._error(t, "Expected '{' to start struct/class body.", "Add '{' after the name.")
            return
        self._parse_block_already_opened()
        self._consume(";", "Expected ';' after struct/class declaration.", "Add ';' after closing brace.")

    def _parse_decl_or_function(self) -> None:
        while self._is_type_start(self._current()):
            self._advance()

        while self._current().value in {"*", "&"}:
            self._advance()

        ident = self._current()
        if ident.kind != "IDENTIFIER":
            self._error(ident, "Expected identifier after type.", "Give a variable or function name.")
            self._sync({";", "{"})
            self._match(";")
            return
        func_or_var_name = ident.value
        self._advance()

        if self._match("("):
            self._parse_param_list()
            self._consume(")", "Expected ')' after parameter list.", "Close function parameters with ')'.")
            if self._match(";"):
                return
            if self._current().value == "{":
                self.defined_functions.add(func_or_var_name)
                self._parse_block()
                return
            t = self._current()
            self._error(t, "Expected '{' for function body.", "Start function body with '{'.")
            self._sync({"}"})
            self._match("}")
            return

        self._parse_declarator_tail("decl_init", ident.value)
        while self._match(","):
            while self._current().value in {"*", "&"}:
                self._advance()
            next_ident = None
            if self._current().kind == "IDENTIFIER":
                next_ident = self._current().value
                self._advance()
            else:
                self._error(self._current(), "Expected identifier in declaration list.", "Add a variable name after ','.")
            self._parse_declarator_tail("decl_init", next_ident)
        self._consume(";", "Expected ';' after declaration.", "End declaration with ';'.")

    def _parse_declarator_tail(self, context: str, target: Optional[str]) -> None:
        if self._match("["):
            if self._current().value != "]":
                self._parse_expression()
            self._consume("]", "Expected ']' for array declarator.", "Close array declarator with ']'.")
        if self._match("="):
            if self._current().value == "{":
                self._parse_brace_initializer()
            else:
                expr_tokens = self._collect_expr_tokens(stop_values={";", ",", "}"}.union(STATEMENT_START_KEYWORDS))
                expr = _ExprParser(expr_tokens).parse()
                self.expressions.append(ExpressionRecord(context=context, line=self._line_of_tokens(expr_tokens), target=target, expr=expr))

    def _parse_brace_initializer(self) -> None:
        if not self._match("{"):
            return
        depth = 1
        while not self._at_end() and depth > 0:
            t = self._current()
            if t.value == "{":
                depth += 1
            elif t.value == "}":
                depth -= 1
            self._advance()
        if depth != 0:
            self._error(self._current(), "Unclosed initializer list.", "Close initializer with '}'.")

    def _parse_param_list(self) -> None:
        if self._current().value == ")":
            return
        while not self._at_end() and self._current().value != ")":
            while self._is_type_start(self._current()) or self._current().value in {"*", "&"}:
                self._advance()
            if self._current().kind == "IDENTIFIER":
                self._advance()
            if self._match("["):
                if self._current().value != "]":
                    self._parse_expression()
                self._consume("]", "Expected ']'.", "Close parameter array type with ']'.")
            if not self._match(","):
                break

    def _parse_block(self) -> None:
        if not self._match("{"):
            self._error(self._current(), "Expected '{' to start block.", "Insert '{' before statements.")
            return
        self._parse_block_already_opened()

    def _parse_block_already_opened(self) -> None:
        while not self._at_end() and self._current().value != "}":
            before = self.pos
            self._parse_statement()
            if self.pos == before:
                t = self._current()
                self._error(t, f"Could not parse statement near '{t.value}'.", "Check statement syntax around this token.")
                self._advance()
        self._consume("}", "Missing closing '}' for block.", "Add '}' to close this block.")

    def _parse_statement(self) -> None:
        t = self._current()

        if t.value == "{":
            self._parse_block()
            return

        if t.value == "if":
            self._advance()
            self._consume("(", "Expected '(' after if.", "Write condition as if (condition).")
            cond_tokens = self._collect_expr_tokens(stop_values={")"})
            self.expressions.append(ExpressionRecord(context="condition", line=self._line_of_tokens(cond_tokens), target=None, expr=_ExprParser(cond_tokens).parse()))
            self._consume(")", "Expected ')' after if condition.", "Close condition with ')'.")
            self._parse_statement()
            if self._match("else"):
                self._parse_statement()
            return

        if t.value in {"for", "while"}:
            keyword = t.value
            self._advance()
            self._consume("(", f"Expected '(' after {keyword}.", f"Write loop header as {keyword} (...).")
            if keyword == "for":
                init_tokens = self._collect_expr_tokens(stop_values={";"})
                self.expressions.append(ExpressionRecord(context="for_init", line=self._line_of_tokens(init_tokens), target=None, expr=_ExprParser(init_tokens).parse()))
                self._consume(";", "Expected ';' in for header.", "for header needs init;condition;update.")

                cond_tokens = self._collect_expr_tokens(stop_values={";"})
                self.expressions.append(ExpressionRecord(context="for_cond", line=self._line_of_tokens(cond_tokens), target=None, expr=_ExprParser(cond_tokens).parse()))
                self._consume(";", "Expected second ';' in for header.", "for header needs two semicolons.")

                upd_tokens = self._collect_expr_tokens(stop_values={")"})
                self.expressions.append(ExpressionRecord(context="for_update", line=self._line_of_tokens(upd_tokens), target=None, expr=_ExprParser(upd_tokens).parse()))
            else:
                cond_tokens = self._collect_expr_tokens(stop_values={")"})
                self.expressions.append(ExpressionRecord(context="condition", line=self._line_of_tokens(cond_tokens), target=None, expr=_ExprParser(cond_tokens).parse()))
            self._consume(")", f"Expected ')' after {keyword} header.", "Close loop header with ')'.")
            self._parse_statement()
            return

        if t.value == "do":
            self._advance()
            self._parse_statement()
            self._consume("while", "Expected 'while' after do-body.", "Use do { ... } while (condition);")
            self._consume("(", "Expected '(' after while.", "Add while condition in parentheses.")
            cond_tokens = self._collect_expr_tokens(stop_values={")"})
            self.expressions.append(ExpressionRecord(context="condition", line=self._line_of_tokens(cond_tokens), target=None, expr=_ExprParser(cond_tokens).parse()))
            self._consume(")", "Expected ')' after condition.", "Close condition with ')'.")
            self._consume(";", "Expected ';' after do-while.", "End do-while with ';'.")
            return

        if t.value in {"return", "break", "continue"}:
            kw = t.value
            self._advance()
            if kw == "return" and self._current().value != ";":
                ret_tokens = self._collect_expr_tokens(stop_values={";", "}"}.union(STATEMENT_START_KEYWORDS))
                self.expressions.append(ExpressionRecord(context="return", line=self._line_of_tokens(ret_tokens), target=None, expr=_ExprParser(ret_tokens).parse()))
            self._consume(";", f"Expected ';' after {t.value}.", "End statement with ';'.")
            return

        if self._is_type_start(t):
            self._parse_local_decl()
            return

        self._parse_expression_statement()

    def _parse_local_decl(self) -> None:
        while self._is_type_start(self._current()):
            self._advance()
        while self._current().value in {"*", "&"}:
            self._advance()
        if self._current().kind != "IDENTIFIER":
            self._error(self._current(), "Expected variable name after type.", "Provide an identifier in declaration.")
            self._sync({";"})
            self._match(";")
            return
        ident = self._current().value
        self._advance()
        self._parse_declarator_tail("decl_init", ident)
        while self._match(","):
            while self._current().value in {"*", "&"}:
                self._advance()
            next_ident = None
            if self._current().kind == "IDENTIFIER":
                next_ident = self._current().value
                self._advance()
            else:
                self._error(self._current(), "Expected variable name after ','.", "Add a variable identifier.")
            self._parse_declarator_tail("decl_init", next_ident)
        self._consume(";", "Expected ';' after local declaration.", "End declaration with ';'.")

    def _parse_expression_statement(self) -> None:
        if self._match(";"):
            return
        start_pos = self.pos
        expr_tokens = self._collect_expr_tokens(stop_values={";", "}"}.union(STATEMENT_START_KEYWORDS))
        if not expr_tokens:
            self._error(self._current(), f"Invalid expression near '{self._current().value}'.", "Rewrite this expression.")
            self._advance()
            return

        context = "expr"
        target = None
        assign_idx = self._find_top_level_op(expr_tokens, "=")
        if assign_idx > 0 and expr_tokens[0].kind == "IDENTIFIER":
            context = "assign"
            target = expr_tokens[0].value
            rhs = expr_tokens[assign_idx + 1 :]
            expr = _ExprParser(rhs).parse()
            self.expressions.append(ExpressionRecord(context=context, line=expr_tokens[0].line, target=target, expr=expr))
        else:
            expr = _ExprParser(expr_tokens).parse()
            self.expressions.append(ExpressionRecord(context=context, line=expr_tokens[0].line, target=None, expr=expr))

        if self.pos == start_pos:
            self._advance()
        self._consume(";", "Expected ';' after expression.", "End statement with ';'.")

    def _parse_expression(self) -> None:
        _ = self._collect_expr_tokens(stop_values={";", ")", "]", "}", "{"})

    def _collect_expr_tokens(self, stop_values: set[str]) -> List[Token]:
        out: List[Token] = []
        depth_paren = 0
        depth_bracket = 0
        depth_brace = 0
        while not self._at_end():
            t = self._current()
            if depth_paren == 0 and depth_bracket == 0 and depth_brace == 0 and t.value in stop_values:
                break
            if t.value == "(":
                depth_paren += 1
            elif t.value == ")":
                depth_paren = max(0, depth_paren - 1)
            elif t.value == "[":
                depth_bracket += 1
            elif t.value == "]":
                depth_bracket = max(0, depth_bracket - 1)
            elif t.value == "{":
                depth_brace += 1
            elif t.value == "}":
                depth_brace = max(0, depth_brace - 1)
            out.append(t)
            self._advance()
        return out

    def _find_top_level_op(self, tokens: List[Token], op: str) -> int:
        depth_paren = 0
        depth_bracket = 0
        depth_brace = 0
        for i, t in enumerate(tokens):
            if t.value == "(":
                depth_paren += 1
            elif t.value == ")":
                depth_paren -= 1
            elif t.value == "[":
                depth_bracket += 1
            elif t.value == "]":
                depth_bracket -= 1
            elif t.value == "{":
                depth_brace += 1
            elif t.value == "}":
                depth_brace -= 1
            elif t.value == op and depth_paren == 0 and depth_bracket == 0 and depth_brace == 0:
                return i
        return -1

    def _line_of_tokens(self, tokens: List[Token]) -> int:
        return tokens[0].line if tokens else self._current().line

    def _is_type_start(self, token: Token) -> bool:
        return token.kind == "TYPE" or token.value in TYPE_STARTERS

    def _sync(self, stop_values: set[str]) -> None:
        while not self._at_end() and self._current().value not in stop_values:
            self._advance()

    def _consume(self, value: str, message: str, suggestion: str) -> None:
        if not self._match(value):
            self._error(self._current(), message, suggestion)

    def _match(self, value: str) -> bool:
        if self._current().value == value:
            self._advance()
            return True
        return False

    def _current(self) -> Token:
        if self.pos >= len(self.tokens):
            return Token("EOF", "EOF", self.tokens[-1].line if self.tokens else 1, 1)
        return self.tokens[self.pos]

    def _advance(self) -> Token:
        t = self._current()
        self.pos += 1
        return t

    def _at_end(self) -> bool:
        return self.pos >= len(self.tokens)

    def _error(self, token: Token, message: str, suggestion: str) -> None:
        self.errors.append(Diagnostic(
            phase="Syntax Analysis",
            level="error",
            message=message,
            line=token.line,
            column=token.column,
            suggestion=suggestion,
        ))

    def _post_syntax_checks(self) -> None:
        has_include = any(
            t.kind == "PREPROCESSOR" and t.value.strip().startswith("#include")
            for t in self.raw_tokens
        )
        if not has_include:
            self.errors.append(Diagnostic(
                phase="Syntax Analysis",
                level="error",
                message="Missing preprocessor include directive.",
                line=1,
                column=1,
                suggestion="Add an include line like #include <stdio.h> or required headers.",
            ))

        if "main" not in self.defined_functions:
            self.errors.append(Diagnostic(
                phase="Syntax Analysis",
                level="error",
                message="Missing entry point: main function is not defined.",
                line=1,
                column=1,
                suggestion="Define int main() { ... } as the program entry point.",
            ))
