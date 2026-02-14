try:
    from .nodes import Node
except ImportError:
    from nodes import Node


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0
        self.type_keywords = {
            "void",
            "char",
            "short",
            "int",
            "long",
            "float",
            "double",
            "signed",
            "unsigned",
        }

    def current(self):
        if self.index < len(self.tokens):
            return self.tokens[self.index]
        return None

    def advance(self):
        token = self.current()
        if token is not None:
            self.index += 1
        return token

    def _token_type(self, token):
        if hasattr(token, "type"):
            return token.type
        return token[0]

    def _token_value(self, token):
        if hasattr(token, "value"):
            return token.value
        return token[1]

    def match(self, type_, value=None):
        token = self.current()
        if token is None:
            return None
        if self._token_type(token) != type_:
            return None
        if value is not None and self._token_value(token) != value:
            return None
        self.advance()
        return token

    def expect(self, type_, value=None):
        token = self.match(type_, value)
        if token is None:
            found = self.current()
            found_value = self._token_value(found) if found else None
            raise SyntaxError(f"Expected {type_} {value or ''} but found {found_value}")
        return token

    def parse(self):
        node = self.parse_program()
        if self.current() is not None:
            raise SyntaxError("Unexpected token after program")
        return node

    def parse_program(self):
        nodes = []
        while self.current() is not None:
            if self.match("PREPROCESSOR"):
                continue
            nodes.append(self.parse_function())
        return Node("PROGRAM", None, nodes)

    def parse_function(self):
        return_type = self.parse_type_spec()
        name_token = self.expect("IDENTIFIER")
        func_name = self._token_value(name_token)
        self.expect("PUNCTUATOR", "(")
        params = self.parse_parameter_list()
        self.expect("PUNCTUATOR", ")")
        body = self.parse_compound_statement()
        return Node("FUNCTION", func_name, [return_type, params, body])

    def parse_parameter_list(self):
        params = []
        token = self.current()
        if token is None:
            return Node("PARAMS", None, params)
        if self._token_type(token) == "PUNCTUATOR" and self._token_value(token) == ")":
            return Node("PARAMS", None, params)
        while True:
            type_node = self.parse_type_spec()
            declarator = self.parse_declarator()
            param = Node("PARAM", type_node.value, [declarator])
            params.append(param)
            if not self.match("PUNCTUATOR", ","):
                break
        return Node("PARAMS", None, params)

    def parse_type_spec(self):
        token = self.current()
        if token is None:
            raise SyntaxError("Expected type specifier")
        if self._token_type(token) == "KEYWORD" and self._token_value(token) in self.type_keywords:
            value = self._token_value(self.advance())
            return Node("TYPE", value)
        raise SyntaxError(f"Expected type specifier but found {self._token_value(token)}")

    def parse_compound_statement(self):
        self.expect("PUNCTUATOR", "{")
        statements = []
        while self.current() is not None and not self.match("PUNCTUATOR", "}"):
            statements.append(self.parse_statement())
        return Node("BLOCK", None, statements)

    def parse_statement(self):
        token = self.current()
        if token is None:
            raise SyntaxError("Unexpected end of input")

        if self._token_type(token) == "PUNCTUATOR" and self._token_value(token) == ";":
            self.advance()
            return Node("EMPTY", None)

        if self._token_type(token) == "PUNCTUATOR" and self._token_value(token) == "{":
            return self.parse_compound_statement()

        if self._token_type(token) == "KEYWORD" and self._token_value(token) == "return":
            return self.parse_return_statement()

        if self._token_type(token) == "KEYWORD" and self._token_value(token) == "if":
            return self.parse_if_statement()

        if self._token_type(token) == "KEYWORD" and self._token_value(token) == "while":
            return self.parse_while_statement()

        if self._token_type(token) == "KEYWORD" and self._token_value(token) == "for":
            return self.parse_for_statement()

        if self._token_type(token) == "KEYWORD" and self._token_value(token) in self.type_keywords:
            return self.parse_declaration()

        return self.parse_expression_statement()

    def parse_declaration(self):
        type_node = self.parse_type_spec()
        items = []
        while True:
            declarator = self.parse_declarator()
            init = None
            if self.match("OPERATOR", "="):
                init = self.parse_expression()
            if init is None:
                items.append(Node("DECL_ITEM", None, [declarator]))
            else:
                items.append(Node("DECL_ITEM", None, [declarator, init]))
            if not self.match("PUNCTUATOR", ","):
                break
        self.expect("PUNCTUATOR", ";")
        return Node("DECLARATION", type_node.value, items)

    def parse_declarator(self):
        pointer_depth = 0
        while self.match("OPERATOR", "*"):
            pointer_depth += 1
        name_token = self.expect("IDENTIFIER")
        node = Node("IDENTIFIER", self._token_value(name_token))
        if self.match("PUNCTUATOR", "["):
            size = None
            if not self.match("PUNCTUATOR", "]"):
                size = self.parse_expression()
                self.expect("PUNCTUATOR", "]")
            node = Node("ARRAY_DECL", None, [node] if size is None else [node, size])
        for _ in range(pointer_depth):
            node = Node("POINTER", None, [node])
        return node

    def parse_return_statement(self):
        self.expect("KEYWORD", "return")
        if self.match("PUNCTUATOR", ";"):
            return Node("RETURN", None)
        expr = self.parse_expression()
        self.expect("PUNCTUATOR", ";")
        return Node("RETURN", None, [expr])

    def parse_if_statement(self):
        self.expect("KEYWORD", "if")
        self.expect("PUNCTUATOR", "(")
        condition = self.parse_expression()
        self.expect("PUNCTUATOR", ")")
        then_stmt = self.parse_statement()
        else_stmt = None
        token = self.current()
        if token and self._token_type(token) == "KEYWORD" and self._token_value(token) == "else":
            self.advance()
            else_stmt = self.parse_statement()
        children = [condition, then_stmt] if else_stmt is None else [condition, then_stmt, else_stmt]
        return Node("IF", None, children)

    def parse_while_statement(self):
        self.expect("KEYWORD", "while")
        self.expect("PUNCTUATOR", "(")
        condition = self.parse_expression()
        self.expect("PUNCTUATOR", ")")
        body = self.parse_statement()
        return Node("WHILE", None, [condition, body])

    def parse_for_statement(self):
        self.expect("KEYWORD", "for")
        self.expect("PUNCTUATOR", "(")
        init = None
        if self._token_type(self.current()) == "KEYWORD" and self._token_value(self.current()) in self.type_keywords:
            init = self.parse_declaration()
        elif not self.match("PUNCTUATOR", ";"):
            init_expr = self.parse_expression()
            self.expect("PUNCTUATOR", ";")
            init = Node("EXPR_STMT", None, [init_expr])

        if init is None:
            pass

        condition = None
        if not self.match("PUNCTUATOR", ";"):
            condition = self.parse_expression()
            self.expect("PUNCTUATOR", ";")

        update = None
        if not self.match("PUNCTUATOR", ")"):
            update = self.parse_expression()
            self.expect("PUNCTUATOR", ")")

        body = self.parse_statement()
        children = [node for node in [init, condition, update, body] if node is not None]
        return Node("FOR", None, children)

    def parse_expression_statement(self):
        expr = self.parse_expression()
        self.expect("PUNCTUATOR", ";")
        return Node("EXPR_STMT", None, [expr])

    def parse_expression(self):
        return self.parse_assignment()

    def parse_assignment(self):
        left = self.parse_logical_or()
        if self.match("OPERATOR", "="):
            if not self.is_assignable(left):
                raise SyntaxError("Left side of assignment must be an identifier")
            right = self.parse_assignment()
            return Node("ASSIGN", "=", [left, right])
        return left

    def is_assignable(self, node):
        if node.kind == "IDENTIFIER":
            return True
        if node.kind == "INDEX":
            return True
        if node.kind == "UNARY_OP" and node.value == "*":
            return True
        return False

    def parse_logical_or(self):
        node = self.parse_logical_and()
        while True:
            token = self.current()
            if token and self._token_type(token) == "OPERATOR" and self._token_value(token) == "||":
                op = self._token_value(self.advance())
                right = self.parse_logical_and()
                node = Node("BINARY_OP", op, [node, right])
            else:
                break
        return node

    def parse_logical_and(self):
        node = self.parse_equality()
        while True:
            token = self.current()
            if token and self._token_type(token) == "OPERATOR" and self._token_value(token) == "&&":
                op = self._token_value(self.advance())
                right = self.parse_equality()
                node = Node("BINARY_OP", op, [node, right])
            else:
                break
        return node

    def parse_equality(self):
        node = self.parse_relational()
        while True:
            token = self.current()
            if token and self._token_type(token) == "OPERATOR" and self._token_value(token) in {"==", "!="}:
                op = self._token_value(self.advance())
                right = self.parse_relational()
                node = Node("BINARY_OP", op, [node, right])
            else:
                break
        return node

    def parse_relational(self):
        node = self.parse_additive()
        while True:
            token = self.current()
            if token and self._token_type(token) == "OPERATOR" and self._token_value(token) in {"<", "<=", ">", ">="}:
                op = self._token_value(self.advance())
                right = self.parse_additive()
                node = Node("BINARY_OP", op, [node, right])
            else:
                break
        return node

    def parse_additive(self):
        node = self.parse_term()
        while True:
            token = self.current()
            if token and self._token_type(token) == "OPERATOR" and self._token_value(token) in {"+", "-"}:
                op = self._token_value(self.advance())
                right = self.parse_term()
                node = Node("BINARY_OP", op, [node, right])
            else:
                break
        return node

    def parse_term(self):
        node = self.parse_factor()
        while True:
            token = self.current()
            if token and self._token_type(token) == "OPERATOR" and self._token_value(token) in {"*", "/", "%"}:
                op = self._token_value(self.advance())
                right = self.parse_factor()
                node = Node("BINARY_OP", op, [node, right])
            else:
                break
        return node

    def parse_factor(self):
        return self.parse_unary()

    def parse_unary(self):
        token = self.current()
        if token is None:
            raise SyntaxError("Unexpected end of input")

        if self._token_type(token) == "OPERATOR" and self._token_value(token) in {"+", "-", "!", "~", "++", "--", "*", "&"}:
            op = self._token_value(self.advance())
            right = self.parse_unary()
            return Node("UNARY_OP", op, [right])

        return self.parse_postfix()

    def parse_postfix(self):
        node = self.parse_primary()
        while True:
            token = self.current()
            if token and self._token_type(token) == "PUNCTUATOR" and self._token_value(token) == "(":
                self.advance()
                args = self.parse_argument_list()
                self.expect("PUNCTUATOR", ")")
                node = Node("CALL", None, [node, args])
                continue

            if token and self._token_type(token) == "PUNCTUATOR" and self._token_value(token) == "[":
                self.advance()
                index_expr = self.parse_expression()
                self.expect("PUNCTUATOR", "]")
                node = Node("INDEX", None, [node, index_expr])
                continue

            if token and self._token_type(token) == "OPERATOR" and self._token_value(token) in {"++", "--"}:
                op = self._token_value(self.advance())
                node = Node("POSTFIX_OP", op, [node])
                continue

            break
        return node

    def parse_argument_list(self):
        args = []
        token = self.current()
        if token and self._token_type(token) == "PUNCTUATOR" and self._token_value(token) == ")":
            return Node("ARGS", None, args)
        while True:
            args.append(self.parse_expression())
            if not self.match("PUNCTUATOR", ","):
                break
        return Node("ARGS", None, args)

    def parse_primary(self):
        token = self.current()
        if token is None:
            raise SyntaxError("Unexpected end of input")

        if self.match("PUNCTUATOR", "("):
            expr = self.parse_expression()
            self.expect("PUNCTUATOR", ")")
            return Node("GROUP", None, [expr])

        if self._token_type(token) == "IDENTIFIER":
            value = self._token_value(self.advance())
            return Node("IDENTIFIER", value)

        if self._token_type(token) in {
            "INTEGER_LITERAL",
            "FLOAT_LITERAL",
            "CHAR_LITERAL",
            "STRING_LITERAL",
        }:
            value = self._token_value(self.advance())
            return Node("LITERAL", value)

        raise SyntaxError(f"Unexpected token {self._token_value(token)}")
