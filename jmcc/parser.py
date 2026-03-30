"""JMCC Parser - Recursive descent parser for C11."""

from typing import List, Optional, Union
from .lexer import Token, TokenType
from .ast_nodes import *
from .errors import ParseError


class Parser:
    def __init__(self, tokens: List[Token], filename: str = "<stdin>"):
        self.tokens = tokens
        self.pos = 0
        self.filename = filename
        self.struct_defs: dict = {}  # name -> StructDef
        self.enum_defs: dict = {}   # name -> EnumDef
        self.enum_values: dict = {} # enumerator name -> int value
        self.typedefs: dict = {}    # typedef name -> TypeSpec
        self._in_func_args = False

    def error(self, msg, token=None):
        t = token or self.current()
        raise ParseError(msg, self.filename, t.line, t.col)

    def current(self) -> Token:
        return self.tokens[self.pos]

    def peek(self, offset=0) -> Token:
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]  # EOF

    def advance(self) -> Token:
        t = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return t

    def expect(self, tt: TokenType, msg: str = None) -> Token:
        t = self.current()
        if t.type != tt:
            expected = msg or tt.name
            self.error(f"expected {expected}, got '{t.value}' ({t.type.name})")
        return self.advance()

    def match(self, *types) -> Optional[Token]:
        if self.current().type in types:
            return self.advance()
        return None

    def at(self, *types) -> bool:
        return self.current().type in types

    # ---- Type parsing ----

    TYPE_SPECIFIERS = {
        TokenType.VOID, TokenType.CHAR, TokenType.SHORT, TokenType.INT,
        TokenType.LONG, TokenType.FLOAT, TokenType.DOUBLE, TokenType.SIGNED,
        TokenType.UNSIGNED, TokenType.BOOL, TokenType.STRUCT, TokenType.UNION,
        TokenType.ENUM, TokenType.CONST, TokenType.VOLATILE, TokenType.STATIC,
        TokenType.EXTERN, TokenType.INLINE, TokenType.REGISTER,
    }

    def is_type_start(self) -> bool:
        if self.current().type in self.TYPE_SPECIFIERS:
            return True
        # Typedef names are also type specifiers
        if self.current().type == TokenType.IDENTIFIER and self.current().value in self.typedefs:
            return True
        return False

    def parse_type_spec(self) -> TypeSpec:
        """Parse a type specifier (e.g., 'unsigned long int', 'struct Foo', 'enum Bar')."""
        is_unsigned = False
        is_signed = False
        is_const = False
        is_volatile = False
        is_static = False
        is_extern = False
        base_parts = []
        struct_def = None
        enum_def = None

        # Parse qualifiers and specifiers
        while True:
            t = self.current()
            if t.type == TokenType.UNSIGNED:
                is_unsigned = True
                self.advance()
            elif t.type == TokenType.SIGNED:
                is_signed = True
                self.advance()
            elif t.type == TokenType.CONST:
                is_const = True
                self.advance()
            elif t.type == TokenType.VOLATILE:
                is_volatile = True
                self.advance()
            elif t.type == TokenType.STATIC:
                is_static = True
                self.advance()
            elif t.type == TokenType.EXTERN:
                is_extern = True
                self.advance()
            elif t.type == TokenType.INLINE:
                self.advance()  # ignore for now
            elif t.type == TokenType.REGISTER:
                self.advance()  # ignore for now
            elif t.type in (TokenType.STRUCT, TokenType.UNION):
                is_union = t.type == TokenType.UNION
                self.advance()
                struct_def = self.parse_struct_spec(is_union)
                break
            elif t.type == TokenType.ENUM:
                self.advance()
                enum_def = self.parse_enum_spec()
                break
            elif t.type == TokenType.IDENTIFIER and t.value in self.typedefs and not base_parts:
                # Typedef name - resolve to underlying type (only if no base type yet)
                td = self.typedefs[t.value]
                self.advance()
                # Parse pointer levels on top of typedef
                pointer_depth = td.pointer_depth
                while self.match(TokenType.STAR):
                    pointer_depth += 1
                    while self.match(TokenType.CONST, TokenType.VOLATILE):
                        pass
                return TypeSpec(
                    base=td.base, pointer_depth=pointer_depth,
                    is_unsigned=td.is_unsigned, is_const=is_const,
                    is_volatile=is_volatile, is_static=is_static,
                    is_extern=is_extern, struct_def=td.struct_def,
                    enum_def=td.enum_def,
                )
            elif t.type in (TokenType.VOID, TokenType.CHAR, TokenType.SHORT,
                            TokenType.INT, TokenType.LONG, TokenType.FLOAT,
                            TokenType.DOUBLE, TokenType.BOOL):
                base_parts.append(t.value)
                self.advance()
            else:
                break

        if struct_def is not None:
            base = f"struct {struct_def.name}" if struct_def.name else "struct"
        elif enum_def is not None:
            base = f"enum {enum_def.name}" if enum_def.name else "enum"
        elif not base_parts:
            if is_unsigned or is_signed:
                base = "int"
            else:
                self.error("expected type specifier")
        elif base_parts == ["long", "long"]:
            base = "long long"
        elif "long" in base_parts and "double" in base_parts:
            base = "long double"
        elif len(base_parts) == 1:
            base = base_parts[0]
            if base == "_Bool":
                base = "int"
        else:
            if "long" in base_parts:
                base = "long"
            elif "short" in base_parts:
                base = "short"
            else:
                base = base_parts[-1]

        # Parse pointer levels
        pointer_depth = 0
        while self.match(TokenType.STAR):
            pointer_depth += 1
            # Skip const/volatile/restrict after *
            while self.match(TokenType.CONST, TokenType.VOLATILE, TokenType.RESTRICT):
                pass

        return TypeSpec(
            base=base,
            pointer_depth=pointer_depth,
            is_unsigned=is_unsigned,
            is_const=is_const,
            is_volatile=is_volatile,
            is_static=is_static,
            is_extern=is_extern,
            struct_def=struct_def,
            enum_def=enum_def,
        )

    def parse_struct_spec(self, is_union=False) -> StructDef:
        """Parse struct/union specifier: struct Name { members }"""
        name = None
        if self.at(TokenType.IDENTIFIER):
            name = self.advance().value

        members = []
        if self.match(TokenType.LBRACE):
            # Pre-register struct for self-referential types
            # Reuse existing EMPTY StructDef (forward-declared) to preserve references
            if name and name in self.struct_defs and not self.struct_defs[name].members:
                sdef = self.struct_defs[name]
                sdef.is_union = is_union
            else:
                sdef = StructDef(name=name, members=[], is_union=is_union)
                if name:
                    self.struct_defs[name] = sdef

            while not self.at(TokenType.RBRACE) and not self.at(TokenType.EOF):
                mem_type = self.parse_type_spec()
                mem_name = ""

                # Function pointer member: type (*name)(params);
                if self.at(TokenType.LPAREN) and self.peek(1).type == TokenType.STAR:
                    self.advance()  # (
                    self.advance()  # *
                    mem_name = self.expect(TokenType.IDENTIFIER, "member name").value
                    self.expect(TokenType.RPAREN, "')'")
                    # Skip param list
                    if self.match(TokenType.LPAREN):
                        depth = 1
                        while depth > 0 and not self.at(TokenType.EOF):
                            if self.match(TokenType.LPAREN): depth += 1
                            elif self.match(TokenType.RPAREN): depth -= 1
                            else: self.advance()
                    mem_type = TypeSpec(base="void", pointer_depth=1)
                elif self.at(TokenType.IDENTIFIER):
                    mem_name = self.advance().value

                # Array member
                if self.match(TokenType.LBRACKET):
                    if self.at(TokenType.RBRACKET):
                        mem_type.array_sizes = [None]
                    else:
                        mem_type.array_sizes = [self.parse_expr()]
                    self.expect(TokenType.RBRACKET, "']'")

                # Bit-field width: int x : 8;
                if self.match(TokenType.COLON):
                    self.parse_expr()  # skip width expression

                if mem_name:
                    members.append(StructMember(type_spec=mem_type, name=mem_name))
                elif not mem_name and mem_type.struct_def:
                    # Anonymous struct/union: keep as unnamed member
                    # member_offset/member_type resolve through it
                    members.append(StructMember(type_spec=mem_type, name=""))

                # Handle comma-separated members: int i, j, k;
                while self.match(TokenType.COMMA):
                    extra_ptrs = 0
                    while self.match(TokenType.STAR):
                        extra_ptrs += 1
                    ename = self.expect(TokenType.IDENTIFIER, "member name").value
                    ets = TypeSpec(base=mem_type.base, pointer_depth=mem_type.pointer_depth + extra_ptrs,
                                   is_unsigned=mem_type.is_unsigned, struct_def=mem_type.struct_def)
                    # Array
                    if self.match(TokenType.LBRACKET):
                        if self.at(TokenType.RBRACKET):
                            ets.array_sizes = [None]
                        else:
                            ets.array_sizes = [self.parse_expr()]
                        self.expect(TokenType.RBRACKET, "']'")
                    members.append(StructMember(type_spec=ets, name=ename))

                self.expect(TokenType.SEMICOLON, "';'")

            self.expect(TokenType.RBRACE, "'}'")
            sdef.members = members
            return sdef
        elif name and name in self.struct_defs:
            return self.struct_defs[name]
        elif name:
            # Forward-declared struct, create placeholder
            sdef = StructDef(name=name, members=[], is_union=is_union)
            self.struct_defs[name] = sdef
            return sdef
        else:
            self.error("expected struct name or '{'")

    def parse_enum_spec(self) -> EnumDef:
        """Parse enum specifier: enum Name { A, B = 5, C }"""
        name = None
        if self.at(TokenType.IDENTIFIER):
            name = self.advance().value

        members = []
        if self.match(TokenType.LBRACE):
            value = 0
            while not self.at(TokenType.RBRACE) and not self.at(TokenType.EOF):
                mem_name = self.expect(TokenType.IDENTIFIER, "enumerator name").value
                if self.match(TokenType.ASSIGN):
                    val_expr = self.parse_expr()
                    if isinstance(val_expr, IntLiteral):
                        value = val_expr.value
                    else:
                        self.error("enum value must be a constant integer")
                members.append(EnumMember(name=mem_name, value=value))
                self.enum_values[mem_name] = value
                value += 1
                if not self.match(TokenType.COMMA):
                    break

            self.expect(TokenType.RBRACE, "'}'")
            edef = EnumDef(name=name, members=members)
            if name:
                self.enum_defs[name] = edef
            return edef
        elif name and name in self.enum_defs:
            return self.enum_defs[name]
        elif name:
            # Forward reference to unknown enum — treat as int
            edef = EnumDef(name=name, members=[])
            self.enum_defs[name] = edef
            return edef
        else:
            self.error("expected enum name or '{'")

    # ---- Expression parsing (precedence climbing) ----

    def parse_expr(self) -> Expr:
        """Parse a full expression (comma operator level)."""
        return self.parse_assignment()

    def parse_assignment(self) -> Expr:
        left = self.parse_ternary()

        assign_ops = {
            TokenType.ASSIGN: "=",
            TokenType.PLUS_ASSIGN: "+=",
            TokenType.MINUS_ASSIGN: "-=",
            TokenType.STAR_ASSIGN: "*=",
            TokenType.SLASH_ASSIGN: "/=",
            TokenType.PERCENT_ASSIGN: "%=",
            TokenType.AMP_ASSIGN: "&=",
            TokenType.PIPE_ASSIGN: "|=",
            TokenType.CARET_ASSIGN: "^=",
            TokenType.LSHIFT_ASSIGN: "<<=",
            TokenType.RSHIFT_ASSIGN: ">>=",
        }

        if self.current().type in assign_ops:
            op = assign_ops[self.current().type]
            self.advance()
            right = self.parse_assignment()  # right-associative
            return Assignment(op=op, target=left, value=right, line=left.line, col=left.col)

        return left

    def parse_ternary(self) -> Expr:
        cond = self.parse_or()
        if self.match(TokenType.QUESTION):
            true_expr = self.parse_expr()
            self.expect(TokenType.COLON, "':'")
            false_expr = self.parse_ternary()
            return TernaryOp(condition=cond, true_expr=true_expr, false_expr=false_expr,
                             line=cond.line, col=cond.col)
        return cond

    def parse_or(self) -> Expr:
        left = self.parse_and()
        while self.match(TokenType.OR):
            right = self.parse_and()
            left = BinaryOp(op="||", left=left, right=right, line=left.line, col=left.col)
        return left

    def parse_and(self) -> Expr:
        left = self.parse_bitwise_or()
        while self.match(TokenType.AND):
            right = self.parse_bitwise_or()
            left = BinaryOp(op="&&", left=left, right=right, line=left.line, col=left.col)
        return left

    def parse_bitwise_or(self) -> Expr:
        left = self.parse_bitwise_xor()
        while self.match(TokenType.PIPE):
            right = self.parse_bitwise_xor()
            left = BinaryOp(op="|", left=left, right=right, line=left.line, col=left.col)
        return left

    def parse_bitwise_xor(self) -> Expr:
        left = self.parse_bitwise_and()
        while self.match(TokenType.CARET):
            right = self.parse_bitwise_and()
            left = BinaryOp(op="^", left=left, right=right, line=left.line, col=left.col)
        return left

    def parse_bitwise_and(self) -> Expr:
        left = self.parse_equality()
        while self.match(TokenType.AMP):
            right = self.parse_equality()
            left = BinaryOp(op="&", left=left, right=right, line=left.line, col=left.col)
        return left

    def parse_equality(self) -> Expr:
        left = self.parse_relational()
        while True:
            if self.match(TokenType.EQ):
                right = self.parse_relational()
                left = BinaryOp(op="==", left=left, right=right, line=left.line, col=left.col)
            elif self.match(TokenType.NE):
                right = self.parse_relational()
                left = BinaryOp(op="!=", left=left, right=right, line=left.line, col=left.col)
            else:
                break
        return left

    def parse_relational(self) -> Expr:
        left = self.parse_shift()
        while True:
            if self.match(TokenType.LT):
                right = self.parse_shift()
                left = BinaryOp(op="<", left=left, right=right, line=left.line, col=left.col)
            elif self.match(TokenType.GT):
                right = self.parse_shift()
                left = BinaryOp(op=">", left=left, right=right, line=left.line, col=left.col)
            elif self.match(TokenType.LE):
                right = self.parse_shift()
                left = BinaryOp(op="<=", left=left, right=right, line=left.line, col=left.col)
            elif self.match(TokenType.GE):
                right = self.parse_shift()
                left = BinaryOp(op=">=", left=left, right=right, line=left.line, col=left.col)
            else:
                break
        return left

    def parse_shift(self) -> Expr:
        left = self.parse_additive()
        while True:
            if self.match(TokenType.LSHIFT):
                right = self.parse_additive()
                left = BinaryOp(op="<<", left=left, right=right, line=left.line, col=left.col)
            elif self.match(TokenType.RSHIFT):
                right = self.parse_additive()
                left = BinaryOp(op=">>", left=left, right=right, line=left.line, col=left.col)
            else:
                break
        return left

    def parse_additive(self) -> Expr:
        left = self.parse_multiplicative()
        while True:
            if self.match(TokenType.PLUS):
                right = self.parse_multiplicative()
                left = BinaryOp(op="+", left=left, right=right, line=left.line, col=left.col)
            elif self.match(TokenType.MINUS):
                right = self.parse_multiplicative()
                left = BinaryOp(op="-", left=left, right=right, line=left.line, col=left.col)
            else:
                break
        return left

    def parse_multiplicative(self) -> Expr:
        left = self.parse_unary()
        while True:
            if self.match(TokenType.STAR):
                right = self.parse_unary()
                left = BinaryOp(op="*", left=left, right=right, line=left.line, col=left.col)
            elif self.match(TokenType.SLASH):
                right = self.parse_unary()
                left = BinaryOp(op="/", left=left, right=right, line=left.line, col=left.col)
            elif self.match(TokenType.PERCENT):
                right = self.parse_unary()
                left = BinaryOp(op="%", left=left, right=right, line=left.line, col=left.col)
            else:
                break
        return left

    def parse_unary(self) -> Expr:
        t = self.current()

        # Prefix ++/--
        if self.match(TokenType.INC):
            operand = self.parse_unary()
            return UnaryOp(op="++", operand=operand, prefix=True, line=t.line, col=t.col)
        if self.match(TokenType.DEC):
            operand = self.parse_unary()
            return UnaryOp(op="--", operand=operand, prefix=True, line=t.line, col=t.col)

        # Unary operators
        if self.match(TokenType.MINUS):
            operand = self.parse_unary()
            return UnaryOp(op="-", operand=operand, line=t.line, col=t.col)
        if self.match(TokenType.PLUS):
            return self.parse_unary()  # unary + is a no-op
        if self.match(TokenType.BANG):
            operand = self.parse_unary()
            return UnaryOp(op="!", operand=operand, line=t.line, col=t.col)
        if self.match(TokenType.TILDE):
            operand = self.parse_unary()
            return UnaryOp(op="~", operand=operand, line=t.line, col=t.col)
        if self.match(TokenType.AMP):
            operand = self.parse_unary()
            return UnaryOp(op="&", operand=operand, line=t.line, col=t.col)
        if self.match(TokenType.STAR):
            operand = self.parse_unary()
            return UnaryOp(op="*", operand=operand, line=t.line, col=t.col)

        # sizeof
        if self.at(TokenType.SIZEOF):
            return self.parse_sizeof()

        # Cast or compound literal: (type) expr  OR  (type){ init }
        if self.at(TokenType.LPAREN) and self.is_cast():
            self.advance()  # (
            target_type = self.parse_type_spec()
            self.expect(TokenType.RPAREN, "')'")
            # Compound literal: (type){ ... }
            if self.at(TokenType.LBRACE):
                init = self.parse_init_list()
                # For scalar compound literals, extract the value
                if isinstance(init, InitList) and init.items and not target_type.struct_def:
                    return init.items[0].value if init.items[0].value else IntLiteral(value=0, line=t.line, col=t.col)
                # For struct compound literals, return as InitList (codegen needs to handle)
                return init
            operand = self.parse_unary()
            return CastExpr(target_type=target_type, operand=operand, line=t.line, col=t.col)

        return self.parse_postfix()

    def is_cast(self) -> bool:
        """Look ahead to determine if (... is a cast or grouping."""
        # Save position
        saved = self.pos
        self.advance()  # skip (
        result = self.is_type_start()
        self.pos = saved
        return result

    def parse_sizeof(self) -> Expr:
        t = self.advance()  # sizeof
        if self.at(TokenType.LPAREN) and self.is_cast():
            self.advance()  # (
            type_spec = self.parse_type_spec()
            self.expect(TokenType.RPAREN, "')'")
            return SizeofExpr(operand=type_spec, is_type=True, line=t.line, col=t.col)
        else:
            operand = self.parse_unary()
            return SizeofExpr(operand=operand, is_type=False, line=t.line, col=t.col)

    def parse_postfix(self) -> Expr:
        expr = self.parse_primary()

        while True:
            if self.match(TokenType.LBRACKET):
                index = self.parse_expr()
                self.expect(TokenType.RBRACKET, "']'")
                expr = ArrayAccess(array=expr, index=index, line=expr.line, col=expr.col)
            elif self.match(TokenType.LPAREN):
                # Function call
                args = []
                if not self.at(TokenType.RPAREN):
                    args.append(self.parse_assignment())
                    while self.match(TokenType.COMMA):
                        args.append(self.parse_assignment())
                self.expect(TokenType.RPAREN, "')'")
                expr = FuncCall(name=expr, args=args, line=expr.line, col=expr.col)
            elif self.match(TokenType.DOT):
                member = self.expect(TokenType.IDENTIFIER, "member name").value
                expr = MemberAccess(obj=expr, member=member, arrow=False, line=expr.line, col=expr.col)
            elif self.match(TokenType.ARROW):
                member = self.expect(TokenType.IDENTIFIER, "member name").value
                expr = MemberAccess(obj=expr, member=member, arrow=True, line=expr.line, col=expr.col)
            elif self.match(TokenType.INC):
                expr = UnaryOp(op="++", operand=expr, prefix=False, line=expr.line, col=expr.col)
            elif self.match(TokenType.DEC):
                expr = UnaryOp(op="--", operand=expr, prefix=False, line=expr.line, col=expr.col)
            else:
                break

        return expr

    def parse_primary(self) -> Expr:
        t = self.current()

        if self.match(TokenType.INT_LITERAL):
            val_str = t.value.rstrip('uUlL')
            if val_str.startswith('0x') or val_str.startswith('0X'):
                val = int(val_str, 16)
            elif val_str.startswith('0') and len(val_str) > 1:
                val = int(val_str, 8)
            else:
                val = int(val_str)
            return IntLiteral(value=val, line=t.line, col=t.col)

        if self.match(TokenType.FLOAT_LITERAL):
            return FloatLiteral(value=float(t.value.rstrip('fFlL')), line=t.line, col=t.col)

        if self.match(TokenType.CHAR_LITERAL):
            return IntLiteral(value=ord(t.value), line=t.line, col=t.col)

        if self.match(TokenType.STRING_LITERAL):
            # Handle string concatenation
            value = t.value
            while self.at(TokenType.STRING_LITERAL):
                value += self.advance().value
            return StringLiteral(value=value, line=t.line, col=t.col)

        if self.match(TokenType.IDENTIFIER):
            # Check if this is an enum constant
            if t.value in self.enum_values:
                return IntLiteral(value=self.enum_values[t.value], line=t.line, col=t.col)
            return Identifier(name=t.value, line=t.line, col=t.col)

        if self.match(TokenType.LPAREN):
            expr = self.parse_expr()
            # Handle comma operator inside parentheses
            if self.at(TokenType.COMMA):
                exprs = [expr]
                while self.match(TokenType.COMMA):
                    exprs.append(self.parse_expr())
                expr = CommaExpr(exprs=exprs, line=exprs[0].line, col=exprs[0].col)
            self.expect(TokenType.RPAREN, "')'")
            return expr

        self.error(f"unexpected token '{t.value}'")

    # ---- Statement parsing ----

    def parse_stmt(self) -> Stmt:
        t = self.current()

        if self.at(TokenType.LBRACE):
            return self.parse_block()

        if self.at(TokenType.RETURN):
            return self.parse_return()

        if self.at(TokenType.IF):
            return self.parse_if()

        if self.at(TokenType.WHILE):
            return self.parse_while()

        if self.at(TokenType.DO):
            return self.parse_do_while()

        if self.at(TokenType.FOR):
            return self.parse_for()

        if self.at(TokenType.BREAK):
            self.advance()
            self.expect(TokenType.SEMICOLON, "';'")
            return BreakStmt(line=t.line, col=t.col)

        if self.at(TokenType.CONTINUE):
            self.advance()
            self.expect(TokenType.SEMICOLON, "';'")
            return ContinueStmt(line=t.line, col=t.col)

        if self.at(TokenType.GOTO):
            self.advance()
            label = self.expect(TokenType.IDENTIFIER, "label").value
            self.expect(TokenType.SEMICOLON, "';'")
            return GotoStmt(label=label, line=t.line, col=t.col)

        if self.at(TokenType.SWITCH):
            return self.parse_switch()

        if self.at(TokenType.CASE):
            return self.parse_case()

        if self.at(TokenType.DEFAULT):
            return self.parse_default()

        # Label: identifier followed by ':'
        if (self.at(TokenType.IDENTIFIER) and
                self.peek(1).type == TokenType.COLON):
            label = self.advance().value
            self.advance()  # :
            stmt = self.parse_stmt()
            return LabelStmt(label=label, stmt=stmt, line=t.line, col=t.col)

        # Empty statement
        if self.match(TokenType.SEMICOLON):
            return NullStmt(line=t.line, col=t.col)

        # Typedef in local scope
        if self.at(TokenType.TYPEDEF):
            td = self.parse_typedef()
            return NullStmt(line=t.line, col=t.col)

        # Struct/enum definition or variable declaration
        if self.at(TokenType.STRUCT, TokenType.UNION, TokenType.ENUM):
            type_spec = self.parse_type_spec()
            if self.match(TokenType.SEMICOLON):
                return NullStmt(line=t.line, col=t.col)
            # It's a variable declaration with struct/enum type
            return self.parse_var_decl_with_type(type_spec)

        # Variable declaration (including struct/enum types)
        if self.is_type_start():
            # Disambiguate typedef name used as variable vs type
            # If a typedef name is followed by . -> = ( [ ++ -- it's a variable use
            if (self.at(TokenType.IDENTIFIER) and self.current().value in self.typedefs and
                    self.peek(1).type in (TokenType.DOT, TokenType.ARROW, TokenType.ASSIGN,
                                          TokenType.LBRACKET, TokenType.INC, TokenType.DEC,
                                          TokenType.PLUS_ASSIGN, TokenType.MINUS_ASSIGN,
                                          TokenType.STAR_ASSIGN, TokenType.SLASH_ASSIGN)):
                pass  # fall through to expression statement
            else:
                return self.parse_var_decl()

        # Expression statement
        expr = self.parse_expr()
        self.expect(TokenType.SEMICOLON, "';'")
        return ExprStmt(expr=expr, line=t.line, col=t.col)

    def parse_block(self) -> Block:
        t = self.expect(TokenType.LBRACE, "'{'")
        stmts = []
        while not self.at(TokenType.RBRACE) and not self.at(TokenType.EOF):
            stmts.append(self.parse_stmt())
        self.expect(TokenType.RBRACE, "'}'")
        return Block(stmts=stmts, line=t.line, col=t.col)

    def parse_return(self) -> ReturnStmt:
        t = self.advance()  # return
        if self.match(TokenType.SEMICOLON):
            return ReturnStmt(value=None, line=t.line, col=t.col)
        value = self.parse_expr()
        self.expect(TokenType.SEMICOLON, "';'")
        return ReturnStmt(value=value, line=t.line, col=t.col)

    def parse_if(self) -> IfStmt:
        t = self.advance()  # if
        self.expect(TokenType.LPAREN, "'('")
        condition = self.parse_expr()
        self.expect(TokenType.RPAREN, "')'")
        then_body = self.parse_stmt()
        else_body = None
        if self.match(TokenType.ELSE):
            else_body = self.parse_stmt()
        return IfStmt(condition=condition, then_body=then_body, else_body=else_body,
                       line=t.line, col=t.col)

    def parse_while(self) -> WhileStmt:
        t = self.advance()  # while
        self.expect(TokenType.LPAREN, "'('")
        condition = self.parse_expr()
        self.expect(TokenType.RPAREN, "')'")
        body = self.parse_stmt()
        return WhileStmt(condition=condition, body=body, line=t.line, col=t.col)

    def parse_do_while(self) -> DoWhileStmt:
        t = self.advance()  # do
        body = self.parse_stmt()
        self.expect(TokenType.WHILE, "'while'")
        self.expect(TokenType.LPAREN, "'('")
        condition = self.parse_expr()
        self.expect(TokenType.RPAREN, "')'")
        self.expect(TokenType.SEMICOLON, "';'")
        return DoWhileStmt(condition=condition, body=body, line=t.line, col=t.col)

    def parse_for(self) -> ForStmt:
        t = self.advance()  # for
        self.expect(TokenType.LPAREN, "'('")

        # Init (may have comma expressions: i=0, j=0)
        if self.match(TokenType.SEMICOLON):
            init = None
        elif self.is_type_start():
            init = self.parse_var_decl()
        else:
            expr = self.parse_expr()
            if self.at(TokenType.COMMA):
                exprs = [expr]
                while self.match(TokenType.COMMA):
                    exprs.append(self.parse_expr())
                expr = CommaExpr(exprs=exprs, line=exprs[0].line, col=exprs[0].col)
            self.expect(TokenType.SEMICOLON, "';'")
            init = ExprStmt(expr=expr, line=expr.line, col=expr.col)

        # Condition
        if self.at(TokenType.SEMICOLON):
            condition = None
        else:
            condition = self.parse_expr()
        self.expect(TokenType.SEMICOLON, "';'")

        # Update (may have comma expressions: i++, j++)
        if self.at(TokenType.RPAREN):
            update = None
        else:
            update = self.parse_expr()
            if self.at(TokenType.COMMA):
                exprs = [update]
                while self.match(TokenType.COMMA):
                    exprs.append(self.parse_expr())
                update = CommaExpr(exprs=exprs, line=exprs[0].line, col=exprs[0].col)
        self.expect(TokenType.RPAREN, "')'")

        body = self.parse_stmt()
        return ForStmt(init=init, condition=condition, update=update, body=body,
                        line=t.line, col=t.col)

    def parse_switch(self) -> SwitchStmt:
        t = self.advance()  # switch
        self.expect(TokenType.LPAREN, "'('")
        expr = self.parse_expr()
        self.expect(TokenType.RPAREN, "')'")
        body = self.parse_stmt()
        return SwitchStmt(expr=expr, body=body, line=t.line, col=t.col)

    def parse_case(self) -> CaseStmt:
        t = self.advance()  # case
        value = self.parse_expr()
        self.expect(TokenType.COLON, "':'")
        # Parse following statements until next case/default/}
        stmts = []
        while not self.at(TokenType.CASE, TokenType.DEFAULT, TokenType.RBRACE, TokenType.EOF):
            stmts.append(self.parse_stmt())
        block = Block(stmts=stmts, line=t.line, col=t.col) if stmts else NullStmt(line=t.line, col=t.col)
        return CaseStmt(value=value, stmt=block, line=t.line, col=t.col)

    def parse_default(self) -> CaseStmt:
        t = self.advance()  # default
        self.expect(TokenType.COLON, "':'")
        stmts = []
        while not self.at(TokenType.CASE, TokenType.DEFAULT, TokenType.RBRACE, TokenType.EOF):
            stmts.append(self.parse_stmt())
        block = Block(stmts=stmts, line=t.line, col=t.col) if stmts else NullStmt(line=t.line, col=t.col)
        return CaseStmt(value=None, stmt=block, is_default=True, line=t.line, col=t.col)

    def parse_var_decl(self) -> Stmt:
        t = self.current()
        type_spec = self.parse_type_spec()
        return self.parse_var_decl_with_type(type_spec)

    def _parse_single_declarator(self, base_type) -> VarDecl:
        """Parse a single declarator (possibly with extra pointer levels)."""
        t = self.current()
        # Extra pointer levels for this specific declarator
        extra_ptrs = 0
        while self.match(TokenType.STAR):
            extra_ptrs += 1

        # Function pointer or pointer-to-array: (*name)(args) or (*name)[size]
        # Also handles const-qualified pointers: (* const name)
        if self.at(TokenType.LPAREN) and self.peek(1).type == TokenType.STAR:
            self.advance()  # (
            self.advance()  # *
            # Skip qualifiers between * and name
            while self.at(TokenType.CONST, TokenType.VOLATILE, TokenType.RESTRICT):
                self.advance()
            name = self.expect(TokenType.IDENTIFIER, "variable name").value
            self.expect(TokenType.RPAREN, "')'")

            if self.at(TokenType.LBRACKET):
                # Pointer to array: (*p)[4]
                # Treat as a regular pointer for codegen
                while self.match(TokenType.LBRACKET):
                    if not self.at(TokenType.RBRACKET):
                        self.parse_expr()  # skip size
                    self.expect(TokenType.RBRACKET, "']'")
                ts = TypeSpec(base=base_type.base, pointer_depth=base_type.pointer_depth + 1,
                              is_unsigned=base_type.is_unsigned)
            elif self.at(TokenType.LPAREN):
                # Function pointer: (*fp)(params)
                self.advance()  # (
                depth = 1
                while depth > 0 and not self.at(TokenType.EOF):
                    if self.match(TokenType.LPAREN): depth += 1
                    elif self.match(TokenType.RPAREN): depth -= 1
                    else: self.advance()
                ts = TypeSpec(base="void", pointer_depth=1)
            else:
                ts = TypeSpec(base=base_type.base, pointer_depth=base_type.pointer_depth + 1)
            init = None
            if self.match(TokenType.ASSIGN):
                init = self.parse_assignment()
            return VarDecl(type_spec=ts, name=name, init=init, line=t.line, col=t.col)

        name = self.expect(TokenType.IDENTIFIER, "variable name").value

        # Local function declaration: int f(char *);
        if self.at(TokenType.LPAREN):
            self.advance()  # (
            depth = 1
            while depth > 0 and not self.at(TokenType.EOF):
                if self.match(TokenType.LPAREN):
                    depth += 1
                elif self.match(TokenType.RPAREN):
                    depth -= 1
                else:
                    self.advance()
            # Return a no-op VarDecl
            return VarDecl(type_spec=TypeSpec(base="void"), name="__skip__", line=t.line, col=t.col)

        # Create type for this specific declarator
        import copy
        ts = TypeSpec(
            base=base_type.base,
            pointer_depth=base_type.pointer_depth + extra_ptrs,
            is_unsigned=base_type.is_unsigned,
            is_const=base_type.is_const,
            is_volatile=base_type.is_volatile,
            is_static=base_type.is_static,
            is_extern=base_type.is_extern,
            struct_def=base_type.struct_def,
            enum_def=base_type.enum_def,
        )

        # Array declaration
        array_sizes = []
        while self.match(TokenType.LBRACKET):
            if self.at(TokenType.RBRACKET):
                array_sizes.append(None)
            else:
                array_sizes.append(self.parse_expr())
            self.expect(TokenType.RBRACKET, "']'")
        if array_sizes:
            ts.array_sizes = array_sizes

        init = None
        if self.match(TokenType.ASSIGN):
            if self.at(TokenType.LBRACE):
                init = self.parse_init_list()
            else:
                init = self.parse_assignment()

        return VarDecl(type_spec=ts, name=name, init=init, line=t.line, col=t.col)

    def parse_var_decl_with_type(self, type_spec) -> Stmt:
        first = self._parse_single_declarator(type_spec)

        # Check for multiple declarators: int x, *p, **pp;
        # For subsequent declarators, use base type without pointer depth
        # (the * was consumed by parse_type_spec but belongs to first declarator)
        if self.match(TokenType.COMMA):
            base_for_comma = TypeSpec(
                base=type_spec.base, pointer_depth=0,
                is_unsigned=type_spec.is_unsigned, is_const=type_spec.is_const,
                is_volatile=type_spec.is_volatile, is_static=type_spec.is_static,
                is_extern=type_spec.is_extern, struct_def=type_spec.struct_def,
                enum_def=type_spec.enum_def,
            )
            decls = [first]
            while True:
                decls.append(self._parse_single_declarator(base_for_comma))
                if not self.match(TokenType.COMMA):
                    break
            self.expect(TokenType.SEMICOLON, "';'")
            return Block(stmts=decls, line=first.line, col=first.col)
        else:
            self.expect(TokenType.SEMICOLON, "';'")
            return first

    # ---- Top-level parsing ----

    def parse_program(self) -> Program:
        decls = []
        while not self.at(TokenType.EOF):
            decl = self.parse_top_level()
            if decl:
                if isinstance(decl, list):
                    decls.extend(decl)
                else:
                    decls.append(decl)
        return Program(declarations=decls)

    def parse_top_level(self) -> Union[FuncDecl, GlobalVarDecl, StructDecl, EnumDecl, TypedefDecl, None]:
        t = self.current()

        # Typedef
        if self.at(TokenType.TYPEDEF):
            return self.parse_typedef()

        # Struct/union/enum definition without variable (just `struct Foo { ... };`)
        if self.at(TokenType.STRUCT, TokenType.UNION, TokenType.ENUM):
            # Peek ahead to see if this is just a type definition
            saved = self.pos
            type_spec = self.parse_type_spec()

            # Just a struct/enum definition followed by ;
            if self.match(TokenType.SEMICOLON):
                if type_spec.struct_def:
                    return StructDecl(struct_def=type_spec.struct_def, line=t.line, col=t.col)
                elif type_spec.enum_def:
                    return EnumDecl(enum_def=type_spec.enum_def, line=t.line, col=t.col)

            # Otherwise it's a variable or function with struct/enum type
            if not self.at(TokenType.IDENTIFIER):
                self.error("expected identifier after type specifier")
            name = self.advance().value

            if self.at(TokenType.LPAREN):
                return self.parse_func_decl(type_spec, name, t)

            # Array global
            array_sizes = []
            while self.match(TokenType.LBRACKET):
                if self.at(TokenType.RBRACKET):
                    array_sizes.append(None)
                else:
                    array_sizes.append(self.parse_expr())
                self.expect(TokenType.RBRACKET, "']'")
            if array_sizes:
                type_spec.array_sizes = array_sizes

            init = None
            if self.match(TokenType.ASSIGN):
                if self.at(TokenType.LBRACE):
                    init = self.parse_init_list()
                else:
                    init = self.parse_expr()
            self.expect(TokenType.SEMICOLON, "';'")
            return GlobalVarDecl(type_spec=type_spec, name=name, init=init, line=t.line, col=t.col)

        if not self.is_type_start():
            self.error(f"expected declaration, got '{t.value}'")

        type_spec = self.parse_type_spec()

        # Global function pointer: int (*name)(params) = init;
        if self.at(TokenType.LPAREN) and self.peek(1).type == TokenType.STAR:
            self.advance()  # (
            self.advance()  # *
            name = self.expect(TokenType.IDENTIFIER, "variable name").value
            self.expect(TokenType.RPAREN, "')'")
            # Skip param list
            if self.match(TokenType.LPAREN):
                depth = 1
                while depth > 0 and not self.at(TokenType.EOF):
                    if self.match(TokenType.LPAREN): depth += 1
                    elif self.match(TokenType.RPAREN): depth -= 1
                    else: self.advance()
            # Treat as void* variable
            fptr_type = TypeSpec(base="void", pointer_depth=1)
            init = None
            if self.match(TokenType.ASSIGN):
                init = self.parse_expr()
            self.expect(TokenType.SEMICOLON, "';'")
            return GlobalVarDecl(type_spec=fptr_type, name=name, init=init, line=t.line, col=t.col)

        name = self.expect(TokenType.IDENTIFIER, "identifier").value

        # Function declaration/definition
        if self.at(TokenType.LPAREN):
            return self.parse_func_decl(type_spec, name, t)

        # Array global
        array_sizes = []
        while self.match(TokenType.LBRACKET):
            if self.at(TokenType.RBRACKET):
                array_sizes.append(None)
            else:
                array_sizes.append(self.parse_expr())
            self.expect(TokenType.RBRACKET, "']'")
        if array_sizes:
            type_spec.array_sizes = array_sizes

        # Global variable (with possible comma-separated additional declarations)
        init = None
        if self.match(TokenType.ASSIGN):
            if self.at(TokenType.LBRACE):
                init = self.parse_init_list()
            else:
                init = self.parse_expr()

        first = GlobalVarDecl(type_spec=type_spec, name=name, init=init, line=t.line, col=t.col)

        # Handle comma-separated global declarations: int a, b = 3, c;
        if self.match(TokenType.COMMA):
            extra = [first]
            while True:
                # Parse additional declarators
                extra_ptrs = 0
                while self.match(TokenType.STAR):
                    extra_ptrs += 1
                ename = self.expect(TokenType.IDENTIFIER, "identifier").value
                ets = TypeSpec(base=type_spec.base, pointer_depth=type_spec.pointer_depth + extra_ptrs,
                               is_unsigned=type_spec.is_unsigned, struct_def=type_spec.struct_def)
                # Array declarator
                if self.match(TokenType.LBRACKET):
                    arr_sizes = []
                    if self.at(TokenType.RBRACKET):
                        arr_sizes.append(None)
                    else:
                        arr_sizes.append(self.parse_expr())
                    self.expect(TokenType.RBRACKET, "']'")
                    ets.array_sizes = arr_sizes
                einit = None
                if self.match(TokenType.ASSIGN):
                    if self.at(TokenType.LBRACE):
                        einit = self.parse_init_list()
                    else:
                        einit = self.parse_expr()
                extra.append(GlobalVarDecl(type_spec=ets, name=ename, init=einit, line=t.line, col=t.col))
                if not self.match(TokenType.COMMA):
                    break
            self.expect(TokenType.SEMICOLON, "';'")
            return extra  # return list
        else:
            self.expect(TokenType.SEMICOLON, "';'")
            return first

    def parse_init_list(self) -> InitList:
        """Parse { expr, expr, ... } or { .field = expr, ... }"""
        t = self.expect(TokenType.LBRACE, "'{'")
        items = []

        while not self.at(TokenType.RBRACE) and not self.at(TokenType.EOF):
            designator = None
            designator_index = None

            # Designated initializer: .field = expr or [idx] = expr
            if self.at(TokenType.DOT):
                self.advance()
                designator = self.expect(TokenType.IDENTIFIER, "field name").value
                self.expect(TokenType.ASSIGN, "'='")
            elif self.at(TokenType.LBRACKET):
                self.advance()
                idx_expr = self.parse_expr()
                if isinstance(idx_expr, IntLiteral):
                    designator_index = idx_expr.value
                self.expect(TokenType.RBRACKET, "']'")
                self.expect(TokenType.ASSIGN, "'='")

            # Value (could be a nested init list)
            if self.at(TokenType.LBRACE):
                value = self.parse_init_list()
            else:
                value = self.parse_assignment()

            items.append(InitItem(designator=designator, designator_index=designator_index, value=value))

            if not self.match(TokenType.COMMA):
                break

        self.expect(TokenType.RBRACE, "'}'")
        return InitList(items=items, line=t.line, col=t.col)

    def parse_typedef(self) -> TypedefDecl:
        t = self.advance()  # typedef
        type_spec = self.parse_type_spec()

        # Function pointer typedef: typedef int (*name)(params);
        if self.at(TokenType.LPAREN) and self.peek(1).type == TokenType.STAR:
            self.advance()  # (
            self.advance()  # *
            name = self.expect(TokenType.IDENTIFIER, "typedef name").value
            self.expect(TokenType.RPAREN, "')'")
            # Skip param list
            if self.match(TokenType.LPAREN):
                depth = 1
                while depth > 0 and not self.at(TokenType.EOF):
                    if self.match(TokenType.LPAREN): depth += 1
                    elif self.match(TokenType.RPAREN): depth -= 1
                    else: self.advance()
            self.expect(TokenType.SEMICOLON, "';'")
            # Preserve the return type info — function pointer that returns type_spec
            fptr_type = TypeSpec(base=type_spec.base, pointer_depth=type_spec.pointer_depth + 1,
                                  struct_def=type_spec.struct_def, enum_def=type_spec.enum_def,
                                  is_unsigned=type_spec.is_unsigned)
            self.typedefs[name] = fptr_type
            return TypedefDecl(type_spec=fptr_type, name=name, line=t.line, col=t.col)

        name = self.expect(TokenType.IDENTIFIER, "typedef name").value
        # Handle typedef for arrays: typedef int arr_t[10];
        if self.match(TokenType.LBRACKET):
            if self.at(TokenType.RBRACKET):
                type_spec.array_sizes = [None]
            else:
                type_spec.array_sizes = [self.parse_expr()]
            self.expect(TokenType.RBRACKET, "']'")
        self.expect(TokenType.SEMICOLON, "';'")
        self.typedefs[name] = type_spec
        return TypedefDecl(type_spec=type_spec, name=name, line=t.line, col=t.col)

    def parse_func_decl(self, return_type: TypeSpec, name: str, start_token: Token) -> FuncDecl:
        self.expect(TokenType.LPAREN, "'('")
        params = []
        is_variadic = False

        if not self.at(TokenType.RPAREN):
            # Check for (void) - no params
            if self.at(TokenType.VOID) and self.peek(1).type == TokenType.RPAREN:
                self.advance()  # skip void
            else:
                params.append(self.parse_param())
                while self.match(TokenType.COMMA):
                    if self.match(TokenType.ELLIPSIS):
                        is_variadic = True
                        break
                    params.append(self.parse_param())

        self.expect(TokenType.RPAREN, "')'")

        # Function body or declaration
        if self.at(TokenType.LBRACE):
            body = self.parse_block()
        elif self.match(TokenType.COMMA) or self.match(TokenType.SEMICOLON):
            # Forward declaration (possibly comma-separated: int f(int), g(int), a;)
            body = None
            first = FuncDecl(return_type=return_type, name=name, params=params,
                             body=body, is_variadic=is_variadic,
                             line=start_token.line, col=start_token.col)
            # If we matched comma, parse remaining declarations
            if self.tokens[self.pos - 1].type == TokenType.COMMA:
                extra = [first]
                while True:
                    extra_ptrs = 0
                    while self.match(TokenType.STAR):
                        extra_ptrs += 1
                    ename = self.expect(TokenType.IDENTIFIER, "identifier").value
                    if self.at(TokenType.LPAREN):
                        ets = TypeSpec(base=return_type.base, pointer_depth=extra_ptrs)
                        # Parse func params inline
                        self.advance()  # (
                        fps = []
                        if not self.at(TokenType.RPAREN):
                            fps.append(self.parse_param())
                            while self.match(TokenType.COMMA):
                                fps.append(self.parse_param())
                        self.expect(TokenType.RPAREN, "')'")
                        extra.append(FuncDecl(return_type=ets, name=ename, params=fps,
                                              body=None, line=start_token.line, col=start_token.col))
                    else:
                        ets = TypeSpec(base=return_type.base, pointer_depth=extra_ptrs)
                        extra.append(GlobalVarDecl(type_spec=ets, name=ename,
                                                    line=start_token.line, col=start_token.col))
                    if not self.match(TokenType.COMMA):
                        break
                self.expect(TokenType.SEMICOLON, "';'")
                return extra
            return first
        else:
            self.expect(TokenType.SEMICOLON, "';'")
            body = None

        return FuncDecl(
            return_type=return_type, name=name, params=params,
            body=body, is_variadic=is_variadic,
            line=start_token.line, col=start_token.col,
        )

    def parse_param(self) -> Param:
        type_spec = self.parse_type_spec()
        name = ""
        # Parenthesized declarator: (*name), (* const name), (*name)(params)
        if self.at(TokenType.LPAREN) and self.peek(1).type == TokenType.STAR:
            self.advance()  # (
            self.advance()  # *
            while self.at(TokenType.CONST, TokenType.VOLATILE, TokenType.RESTRICT):
                self.advance()
            if self.at(TokenType.IDENTIFIER):
                name = self.advance().value
            self.expect(TokenType.RPAREN, "')'")
            type_spec.pointer_depth += 1
            # Skip function params if present: (*fp)(int, int)
            if self.match(TokenType.LPAREN):
                depth = 1
                while depth > 0 and not self.at(TokenType.EOF):
                    if self.match(TokenType.LPAREN): depth += 1
                    elif self.match(TokenType.RPAREN): depth -= 1
                    else: self.advance()
            return Param(type_spec=type_spec, name=name)
        if self.at(TokenType.IDENTIFIER):
            name = self.advance().value
        # Array parameter: int a[] or int a[100] or int a[const 5] — decays to pointer
        if self.match(TokenType.LBRACKET):
            # Skip qualifiers (const, static, volatile, restrict) inside brackets
            while self.at(TokenType.CONST, TokenType.VOLATILE, TokenType.STATIC, TokenType.RESTRICT):
                self.advance()
            # Handle * as VLA unspecified size
            if self.at(TokenType.STAR) and self.peek(1).type == TokenType.RBRACKET:
                self.advance()  # skip *
            elif not self.at(TokenType.RBRACKET):
                self.parse_expr()  # skip the size expression
            self.expect(TokenType.RBRACKET, "']'")
            type_spec.pointer_depth += 1  # arrays decay to pointers in params
        return Param(type_spec=type_spec, name=name)
