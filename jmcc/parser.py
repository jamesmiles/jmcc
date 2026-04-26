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
        # Pre-define built-in GCC/Clang type names that are always available
        self.typedefs["__builtin_va_list"] = TypeSpec(base="char", pointer_depth=1)
        self.typedefs["__gnuc_va_list"] = TypeSpec(base="char", pointer_depth=1)
        self.declared_vars: set = set()  # variable names that shadow enum constants
        self.local_scope: set = set()   # param/variable names that shadow typedef names
        self._in_func_args = False
        self._hoisted_funcs: list = []      # (FuncDecl, enclosing_func_name) staged for lifting
        self._current_func_name: str = ""   # name of top-level function being parsed

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
        TokenType.EXTERN, TokenType.INLINE, TokenType.REGISTER, TokenType.ATOMIC,
        TokenType.NORETURN,
        TokenType.AUTO, TokenType.THREAD_LOCAL,
    }

    def _skip_asm_label(self):
        """Skip __asm__("label") on declarations (linker name aliases)."""
        while (self.at(TokenType.IDENTIFIER) and
               self.current().value in ("__asm__", "asm", "__asm")):
            self.advance()  # __asm__
            if self.match(TokenType.LPAREN):
                depth = 1
                while depth > 0 and not self.at(TokenType.EOF):
                    if self.match(TokenType.LPAREN):
                        depth += 1
                    elif self.match(TokenType.RPAREN):
                        depth -= 1
                    else:
                        self.advance()

    def skip_attribute(self):
        """Skip GCC __attribute__((...)) annotations.
        Returns a set of recognized attribute names (e.g., {'packed'})."""
        attrs = set()
        while (self.at(TokenType.IDENTIFIER) and
               self.current().value in ("__attribute__", "__attribute")):
            self.advance()  # __attribute__
            if self.match(TokenType.LPAREN):
                depth = 1
                while depth > 0 and not self.at(TokenType.EOF):
                    if self.at(TokenType.IDENTIFIER):
                        name = self.current().value
                        if name in ("packed", "__packed__"):
                            attrs.add("packed")
                    if self.match(TokenType.LPAREN):
                        depth += 1
                    elif self.match(TokenType.RPAREN):
                        depth -= 1
                    else:
                        self.advance()
        return attrs

    def is_type_start(self) -> bool:
        if self.current().type in self.TYPE_SPECIFIERS:
            return True
        # Typedef names are also type specifiers, unless shadowed by a local variable
        if (self.current().type == TokenType.IDENTIFIER and
                self.current().value in self.typedefs and
                self.current().value not in self.local_scope):
            return True
        # __typeof__ / typeof are type specifiers
        if self.current().type == TokenType.IDENTIFIER and self.current().value in ("__typeof__", "__typeof", "typeof"):
            return True
        # __int128 / __uint128_t / __int128_t are type specifiers
        if self.current().type == TokenType.IDENTIFIER and self.current().value in (
                "__int128", "__uint128_t", "__int128_t", "__uint128"):
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
        has_storage_class = False  # any qualifier that implies implicit int
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
            elif t.type == TokenType.ATOMIC:
                self.advance()  # _Atomic qualifier: accept and ignore
            elif t.type == TokenType.STATIC:
                is_static = True
                has_storage_class = True
                self.advance()
            elif t.type == TokenType.EXTERN:
                is_extern = True
                has_storage_class = True
                self.advance()
            elif t.type == TokenType.INLINE:
                has_storage_class = True
                self.advance()
            elif t.type == TokenType.NORETURN:
                self.advance()
            elif t.type == TokenType.REGISTER:
                has_storage_class = True
                self.advance()
            elif t.type == TokenType.AUTO:
                # 'auto' storage class (no-op in C)
                has_storage_class = True
                self.advance()
            elif t.type == TokenType.THREAD_LOCAL:
                # __thread / _Thread_local: thread-local storage (no-op for jmcc)
                has_storage_class = True
                self.advance()
            elif t.type == TokenType.IDENTIFIER and t.value in ("_Nullable", "_Nonnull", "_Null_unspecified", "__nonnull", "__nullable"):
                self.advance()  # nullability qualifier: accept and ignore
            elif t.type == TokenType.IDENTIFIER and t.value in ("__attribute__", "__attribute"):
                self.skip_attribute()
                continue
            elif t.type == TokenType.IDENTIFIER and t.value in ("__typeof__", "__typeof", "typeof") and not base_parts:
                # __typeof__(expr) - deduce type from expression
                self.advance()  # consume __typeof__
                self.expect(TokenType.LPAREN, "'('")
                # Try to parse as a type first, then as expression
                saved = self.pos
                try:
                    if self.is_type_start():
                        ts = self.parse_type_spec()
                        self.expect(TokenType.RPAREN, "')'")
                        # Apply qualifiers parsed before __typeof__
                        pointer_depth = ts.pointer_depth
                        while self.match(TokenType.STAR):
                            pointer_depth += 1
                            while self.match(TokenType.CONST, TokenType.VOLATILE, TokenType.RESTRICT):
                                pass
                        return TypeSpec(
                            base=ts.base, pointer_depth=pointer_depth,
                            is_unsigned=ts.is_unsigned, is_const=is_const or ts.is_const,
                            is_volatile=is_volatile, is_static=is_static,
                            is_extern=is_extern, struct_def=ts.struct_def,
                            enum_def=ts.enum_def,
                        )
                except:
                    self.pos = saved
                # Parse as expression to deduce type
                expr = self.parse_expr()
                self.expect(TokenType.RPAREN, "')'")
                # Deduce type from expression
                if isinstance(expr, FloatLiteral):
                    base_type = "double"
                elif isinstance(expr, IntLiteral):
                    base_type = "int"
                elif isinstance(expr, CharLiteral):
                    base_type = "int"  # in C, char literals are int
                elif isinstance(expr, StringLiteral):
                    base_type = "char"
                    pointer_depth = 0
                    while self.match(TokenType.STAR):
                        pointer_depth += 1
                        while self.match(TokenType.CONST, TokenType.VOLATILE, TokenType.RESTRICT):
                            pass
                    return TypeSpec(base=base_type, pointer_depth=pointer_depth + 1,
                                   is_const=is_const, is_static=is_static, is_extern=is_extern)
                else:
                    base_type = "int"  # fallback
                pointer_depth = 0
                while self.match(TokenType.STAR):
                    pointer_depth += 1
                    while self.match(TokenType.CONST, TokenType.VOLATILE, TokenType.RESTRICT):
                        pass
                return TypeSpec(
                    base=base_type, pointer_depth=pointer_depth,
                    is_unsigned=is_unsigned, is_const=is_const,
                    is_volatile=is_volatile, is_static=is_static,
                    is_extern=is_extern,
                )
            elif t.type in (TokenType.STRUCT, TokenType.UNION):
                is_union = t.type == TokenType.UNION
                self.advance()
                struct_def = self.parse_struct_spec(is_union)
                break
            elif t.type == TokenType.ENUM:
                self.advance()
                enum_def = self.parse_enum_spec()
                break
            elif t.type == TokenType.IDENTIFIER and t.value in self.typedefs and not base_parts and not is_unsigned and not is_signed:
                # Typedef name - resolve to underlying type (only if no base type yet)
                td = self.typedefs[t.value]
                self.advance()
                # Parse pointer levels on top of typedef
                # Skip qualifiers before * (e.g., XColor const *)
                while self.match(TokenType.CONST, TokenType.VOLATILE, TokenType.RESTRICT):
                    pass
                pointer_depth = td.pointer_depth
                while self.match(TokenType.STAR):
                    pointer_depth += 1
                    while self.match(TokenType.CONST, TokenType.VOLATILE, TokenType.RESTRICT):
                        pass
                # Check for function pointer type after typedef: uid_t(*)(args)
                if self.at(TokenType.LPAREN) and self.peek(1).type == TokenType.STAR:
                    saved_fptr_td = self.pos
                    self.advance()  # (
                    star_count = 0
                    while self.match(TokenType.STAR):
                        star_count += 1
                    if self.at(TokenType.RPAREN):
                        self.advance()  # )
                        if self.match(TokenType.LPAREN):  # param list
                            depth = 1
                            while depth > 0 and not self.at(TokenType.EOF):
                                if self.match(TokenType.LPAREN): depth += 1
                                elif self.match(TokenType.RPAREN): depth -= 1
                                else: self.advance()
                        pointer_depth += star_count
                    else:
                        self.pos = saved_fptr_td  # not a match, restore
                # Function-type typedef with one star becomes a callable function pointer
                resolved_is_func_ptr = (
                    (td.is_func_ptr and pointer_depth == td.pointer_depth) or
                    (td.is_func_type and pointer_depth == 1)
                )
                resolved_fptr_depth = td.func_ptr_native_depth if td.is_func_ptr else (1 if (td.is_func_type and pointer_depth == 1) else 0)
                return TypeSpec(
                    base=td.base, pointer_depth=pointer_depth,
                    is_unsigned=td.is_unsigned, is_const=is_const,
                    is_volatile=is_volatile, is_static=is_static,
                    is_extern=is_extern, struct_def=td.struct_def,
                    enum_def=td.enum_def,
                    is_func_ptr=resolved_is_func_ptr,
                    func_ptr_native_depth=resolved_fptr_depth,
                    array_sizes=td.array_sizes,
                )
            elif t.type == TokenType.IDENTIFIER and t.value in ("__int128", "__uint128_t", "__int128_t", "__uint128"):
                base_parts.append("__int128")
                if t.value in ("__uint128_t", "__uint128"):
                    is_unsigned = True
                self.advance()
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
            if is_unsigned or is_signed or has_storage_class:
                base = "int"  # implicit int (C89 K&R style)
            else:
                self.error("expected type specifier")
        elif "__int128" in base_parts:
            base = "__int128"
        elif base_parts == ["long", "long"]:
            base = "long long"
        elif "long" in base_parts and "double" in base_parts:
            base = "long double"
        elif len(base_parts) == 1:
            base = base_parts[0]
            if base == "_Bool":
                base = "_Bool"  # keep as distinct type for truncation semantics
                is_unsigned = True
        else:
            if "long" in base_parts:
                base = "long"
            elif "short" in base_parts:
                base = "short"
            else:
                base = base_parts[-1]

        # Skip trailing qualifiers/attributes before pointer (e.g., enum E const *)
        while self.at(TokenType.CONST, TokenType.VOLATILE, TokenType.RESTRICT):
            self.advance()
        self.skip_attribute()  # int __attribute__((noinline)) *

        # Parse pointer levels
        pointer_depth = 0
        while self.match(TokenType.STAR):
            pointer_depth += 1
            # Skip const/volatile/restrict after *
            while self.match(TokenType.CONST, TokenType.VOLATILE, TokenType.RESTRICT):
                pass

        # Function pointer type in cast/sizeof: void (*)(void), int (*)(int, int), void*(*)(args)
        # Also handles int (__attribute__((x)) *)(void)
        # Only matches abstract fptr types (no name between * and ))
        if self.at(TokenType.LPAREN):
            saved_fptr = self.pos
            self.advance()  # (
            self.skip_attribute()
            if self.at(TokenType.STAR):
                star_count = 0
                while self.match(TokenType.STAR):
                    star_count += 1
                if self.at(TokenType.RPAREN):
                    self.advance()  # )
                    if self.at(TokenType.LBRACKET):
                        # Pointer to array: (*)[N]
                        arr_sizes = []
                        while self.match(TokenType.LBRACKET):
                            if not self.at(TokenType.RBRACKET):
                                arr_sizes.append(self.parse_expr())
                            else:
                                arr_sizes.append(None)
                            self.expect(TokenType.RBRACKET, "']'")
                        pointer_depth += star_count
                        return TypeSpec(
                            base=base, pointer_depth=pointer_depth,
                            is_unsigned=is_unsigned, is_const=is_const,
                            is_volatile=is_volatile, is_static=is_static,
                            is_extern=is_extern, struct_def=struct_def,
                            enum_def=enum_def, array_sizes=arr_sizes)
                    # Skip param list (function pointer)
                    elif self.match(TokenType.LPAREN):
                        depth = 1
                        while depth > 0 and not self.at(TokenType.EOF):
                            if self.match(TokenType.LPAREN): depth += 1
                            elif self.match(TokenType.RPAREN): depth -= 1
                            else: self.advance()
                    pointer_depth += star_count  # function pointer
                elif self.at(TokenType.LPAREN) and self.peek(1).type == TokenType.STAR:
                    # Potentially (*(*)(inner_params))(outer_params) — abstract nested fptr.
                    # Only match if there's no identifier inside (named declarators go to
                    # _parse_single_declarator instead).
                    scan = self.pos
                    depth = 0
                    has_ident = False
                    while scan < len(self.tokens):
                        tt = self.tokens[scan].type
                        if tt == TokenType.LPAREN: depth += 1
                        elif tt == TokenType.RPAREN:
                            depth -= 1
                            if depth < 0: break
                        elif tt == TokenType.IDENTIFIER and depth > 0:
                            has_ident = True
                            break
                        scan += 1
                    if has_ident:
                        self.pos = saved_fptr  # named declarator — leave for _parse_single_declarator
                    else:
                        # Abstract nested fptr: skip the whole inner group then outer params
                        depth = 1
                        while depth > 0 and not self.at(TokenType.EOF):
                            if self.match(TokenType.LPAREN): depth += 1
                            elif self.match(TokenType.RPAREN): depth -= 1
                            else: self.advance()
                        if self.match(TokenType.LPAREN):
                            depth = 1
                            while depth > 0 and not self.at(TokenType.EOF):
                                if self.match(TokenType.LPAREN): depth += 1
                                elif self.match(TokenType.RPAREN): depth -= 1
                                else: self.advance()
                        pointer_depth += star_count
                else:
                    self.pos = saved_fptr  # not a match, restore
            else:
                self.pos = saved_fptr  # not a match, restore

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
        attrs = self.skip_attribute() or set()  # union/struct __attribute__((packed)) Name {
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
                # Peek the first token to compute base-type inherent pointer depth
                # (for typedefs, typedef itself may contribute pointer_depth).
                # This is the pointer_depth that should be shared among ALL
                # declarators in a comma list; extra *s belong to individual declarators.
                base_inherent_pd = 0
                if self.at(TokenType.IDENTIFIER) and self.current().value in self.typedefs:
                    base_inherent_pd = self.typedefs[self.current().value].pointer_depth
                mem_type = self.parse_type_spec()
                mem_name = ""

                # Function pointer or pointer-to-array member: type (*name)(params) or type (*name)[N];
                if self.at(TokenType.LPAREN) and self.peek(1).type == TokenType.STAR:
                    self.advance()  # (
                    self.advance()  # *
                    # Skip const/volatile/restrict and nullability qualifiers after *
                    # e.g. long (*const name)(args) or int (* _Nullable name)(args)
                    while self.at(TokenType.CONST, TokenType.VOLATILE, TokenType.RESTRICT) or \
                          (self.at(TokenType.IDENTIFIER) and self.current().value in ('_Nullable', '_Nonnull', '_Null_unspecified')):
                        self.advance()
                    # Multiple stars: void (**name)(params) — pointer to function pointer
                    member_extra_stars = 0
                    while self.match(TokenType.STAR):
                        member_extra_stars += 1
                    # Function returning function pointer: void (*(*name)(args1))(args2)
                    # After `(*` we see another `(` instead of an identifier
                    if self.at(TokenType.LPAREN) and self.peek(1).type == TokenType.STAR:
                        self.advance()  # inner (
                        self.advance()  # inner *
                        mem_name = self.expect(TokenType.IDENTIFIER, "member name").value
                        self.expect(TokenType.RPAREN, "')'")  # close inner (*name)
                        # Skip inner param list (args1)
                        if self.match(TokenType.LPAREN):
                            depth = 1
                            while depth > 0 and not self.at(TokenType.EOF):
                                if self.match(TokenType.LPAREN): depth += 1
                                elif self.match(TokenType.RPAREN): depth -= 1
                                else: self.advance()
                        self.expect(TokenType.RPAREN, "')'")  # close outer (
                        # Skip outer param list (args2)
                        if self.match(TokenType.LPAREN):
                            depth = 1
                            while depth > 0 and not self.at(TokenType.EOF):
                                if self.match(TokenType.LPAREN): depth += 1
                                elif self.match(TokenType.RPAREN): depth -= 1
                                else: self.advance()
                        # Type: pointer to function returning function pointer
                        # Use pointer_depth=2 so calling it returns a pointer (depth=1)
                        mem_type = TypeSpec(base="void", pointer_depth=2)
                        # Bit-field width or end of declaration
                        bit_width = None
                        if self.match(TokenType.COLON):
                            bw_expr = self.parse_expr()
                            if isinstance(bw_expr, IntLiteral):
                                bit_width = bw_expr.value
                        members.append(StructMember(type_spec=mem_type, name=mem_name, bit_width=bit_width))
                        self.expect(TokenType.SEMICOLON, "';'")
                        continue
                    mem_name = self.expect(TokenType.IDENTIFIER, "member name").value
                    self.expect(TokenType.RPAREN, "')'")
                    if self.at(TokenType.LBRACKET):
                        # Pointer to array: type (*name)[N]
                        arr_sizes = []
                        while self.match(TokenType.LBRACKET):
                            if not self.at(TokenType.RBRACKET):
                                arr_sizes.append(self.parse_expr())
                            else:
                                arr_sizes.append(None)
                            self.expect(TokenType.RBRACKET, "']'")
                        mem_type = TypeSpec(base=mem_type.base, pointer_depth=mem_type.pointer_depth + 1 + member_extra_stars,
                                           is_unsigned=mem_type.is_unsigned,
                                           array_sizes=arr_sizes if arr_sizes else None)
                    else:
                        # Skip param list for function pointer
                        if self.match(TokenType.LPAREN):
                            depth = 1
                            while depth > 0 and not self.at(TokenType.EOF):
                                if self.match(TokenType.LPAREN): depth += 1
                                elif self.match(TokenType.RPAREN): depth -= 1
                                else: self.advance()
                        # Preserve return type base and pointer depth:
                        # void *(*fp)(args) needs pd=ret_pd+1 so calling it returns void* (pd=1)
                        mem_type = TypeSpec(base=mem_type.base,
                                            pointer_depth=mem_type.pointer_depth + 1 + member_extra_stars,
                                            is_unsigned=mem_type.is_unsigned,
                                            struct_def=mem_type.struct_def)
                elif self.at(TokenType.IDENTIFIER):
                    mem_name = self.advance().value

                # Array member (including multi-dimensional: short bbox[2][4])
                if self.at(TokenType.LBRACKET):
                    arr_sizes = []
                    while self.match(TokenType.LBRACKET):
                        if self.at(TokenType.RBRACKET):
                            arr_sizes.append(None)
                        else:
                            arr_sizes.append(self.parse_expr())
                        self.expect(TokenType.RBRACKET, "']'")
                    mem_type.array_sizes = arr_sizes
                    if mem_type.pointer_depth > 0:
                        mem_type.is_ptr_array = True

                # Bit-field width: int x : 8;  (use parse_assignment to avoid consuming comma)
                bit_width = None
                if self.match(TokenType.COLON):
                    bw_expr = self.parse_assignment()
                    if isinstance(bw_expr, IntLiteral):
                        bit_width = bw_expr.value

                if mem_name:
                    members.append(StructMember(type_spec=mem_type, name=mem_name, bit_width=bit_width))
                elif not mem_name and mem_type.struct_def:
                    # Anonymous struct/union: keep as unnamed member
                    # member_offset/member_type resolve through it
                    members.append(StructMember(type_spec=mem_type, name=""))

                # Skip __attribute__ after member name/array/bitfield
                self.skip_attribute()

                # Handle comma-separated members: int i, j, k; or int *p, a;
                # In C, `*` binds to the individual declarator. Subsequent
                # declarators start from the base pointer_depth (without the
                # extra *s parse_type_spec consumed for the first declarator).
                # But preserve typedef's inherent pointer depth.
                while self.match(TokenType.COMMA):
                    extra_ptrs = 0
                    while self.match(TokenType.STAR):
                        extra_ptrs += 1
                    ename = self.expect(TokenType.IDENTIFIER, "member name").value
                    ets = TypeSpec(base=mem_type.base, pointer_depth=base_inherent_pd + extra_ptrs,
                                   is_unsigned=mem_type.is_unsigned, struct_def=mem_type.struct_def,
                                   enum_def=mem_type.enum_def, is_const=mem_type.is_const)
                    # Array
                    if self.match(TokenType.LBRACKET):
                        if self.at(TokenType.RBRACKET):
                            ets.array_sizes = [None]
                        else:
                            ets.array_sizes = [self.parse_expr()]
                        self.expect(TokenType.RBRACKET, "']'")
                    # Bitfield width in comma-separated declarator: uint8_t a:4, b:4;
                    extra_bit_width = None
                    if self.match(TokenType.COLON):
                        bw = self.parse_expr()
                        if isinstance(bw, IntLiteral):
                            extra_bit_width = bw.value
                    self.skip_attribute()
                    members.append(StructMember(type_spec=ets, name=ename, bit_width=extra_bit_width))

                self.expect(TokenType.SEMICOLON, "';'")

            self.expect(TokenType.RBRACE, "'}'")
            sdef.members = members
            # Handle trailing __attribute__((packed)) after the struct body
            trailing_attrs = self.skip_attribute() or set()
            if "packed" in attrs or "packed" in trailing_attrs:
                sdef.is_packed = True
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
                    val_expr = self.parse_assignment()
                    cv = self._eval_const(val_expr)
                    if cv is not None:
                        value = cv
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

    def _eval_const(self, expr) -> Optional[int]:
        """Evaluate a constant expression at parse time (for enum values, etc.)."""
        if isinstance(expr, IntLiteral):
            return expr.value
        if isinstance(expr, CharLiteral):
            return ord(expr.value)
        if isinstance(expr, Identifier) and expr.name in self.enum_values:
            return self.enum_values[expr.name]
        if isinstance(expr, UnaryOp):
            v = self._eval_const(expr.operand)
            if v is None:
                return None
            if expr.op == "-": return -v
            if expr.op == "~": return ~v
            if expr.op == "!": return 0 if v else 1
        if isinstance(expr, BinaryOp):
            l = self._eval_const(expr.left)
            r = self._eval_const(expr.right)
            if l is None or r is None:
                return None
            ops = {
                "+": lambda a, b: a + b, "-": lambda a, b: a - b,
                "*": lambda a, b: a * b, "/": lambda a, b: a // b if b else 0,
                "%": lambda a, b: a % b if b else 0,
                "<<": lambda a, b: a << b, ">>": lambda a, b: a >> b,
                "&": lambda a, b: a & b, "|": lambda a, b: a | b,
                "^": lambda a, b: a ^ b,
            }
            if expr.op in ops:
                return ops[expr.op](l, r)
        if isinstance(expr, CastExpr):
            return self._eval_const(expr.operand)
        if isinstance(expr, SizeofExpr):
            if expr.is_type:
                ts = expr.operand
                size = ts.size_bytes()
                if ts.array_sizes:
                    for dim in ts.array_sizes:
                        cv = self._eval_const(dim) if dim else None
                        if cv is not None:
                            size *= cv
                return size
        return None

    # ---- Expression parsing (precedence climbing) ----

    def parse_expr(self) -> Expr:
        """Parse a full expression (comma operator level)."""
        left = self.parse_assignment()
        if self.at(TokenType.COMMA) and not self._in_func_args:
            exprs = [left]
            while self.match(TokenType.COMMA):
                exprs.append(self.parse_assignment())
            return CommaExpr(exprs=exprs, line=left.line, col=left.col)
        return left

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
        if self.match(TokenType.AND):
            # GCC &&label extension: address of label
            if self.at(TokenType.IDENTIFIER):
                label = self.advance().value
                return LabelAddrExpr(label=label, line=t.line, col=t.col)
            self.error("expected label name after '&&'", t.line, t.col)
        if self.match(TokenType.AMP):
            operand = self.parse_unary()
            return UnaryOp(op="&", operand=operand, line=t.line, col=t.col)
        if self.match(TokenType.STAR):
            operand = self.parse_unary()
            return UnaryOp(op="*", operand=operand, line=t.line, col=t.col)

        # sizeof / _Alignof
        if self.at(TokenType.SIZEOF):
            return self.parse_sizeof()
        if self.at(TokenType.ALIGNOF):
            return self.parse_alignof()

        # Cast or compound literal: (type) expr  OR  (type){ init }
        if self.at(TokenType.LPAREN) and self.is_cast():
            self.advance()  # (
            target_type = self.parse_type_spec()
            # Handle array type in cast: (int[]) or (int[N])
            while self.match(TokenType.LBRACKET):
                if not self.at(TokenType.RBRACKET):
                    dim = self.parse_expr()
                    if target_type.array_sizes is None:
                        target_type.array_sizes = [dim]
                    else:
                        target_type.array_sizes.append(dim)
                else:
                    if target_type.array_sizes is None:
                        target_type.array_sizes = [None]
                    else:
                        target_type.array_sizes.append(None)
                self.expect(TokenType.RBRACKET, "']'")
            self.expect(TokenType.RPAREN, "')'")
            # Compound literal: (type){ ... }
            if self.at(TokenType.LBRACE):
                init = self.parse_init_list()
                # For scalar compound literals (not struct/array), extract the value
                if isinstance(init, InitList) and init.items and not target_type.struct_def and not target_type.is_array():
                    return init.items[0].value if init.items[0].value else IntLiteral(value=0, line=t.line, col=t.col)
                # For scalar compound literals (not struct/array), extract the value
                if isinstance(init, InitList) and init.items and not target_type.struct_def and not target_type.is_array():
                    return init.items[0].value if init.items[0].value else IntLiteral(value=0, line=t.line, col=t.col)
                # For struct compound literals, return as CastExpr (preserves type info)
                return CastExpr(target_type=target_type, operand=init, line=t.line, col=t.col)
            operand = self.parse_unary()
            return CastExpr(target_type=target_type, operand=operand, line=t.line, col=t.col)

        return self.parse_postfix()

    def is_cast(self) -> bool:
        """Look ahead to determine if (... is a cast or grouping."""
        saved = self.pos
        self.advance()  # skip (
        # Skip __attribute__((...)) before type
        while (self.at(TokenType.IDENTIFIER) and
               self.current().value in ("__attribute__", "__attribute")):
            self.advance()
            if self.match(TokenType.LPAREN):
                depth = 1
                while depth > 0 and not self.at(TokenType.EOF):
                    if self.match(TokenType.LPAREN): depth += 1
                    elif self.match(TokenType.RPAREN): depth -= 1
                    else: self.advance()
        if not self.is_type_start():
            self.pos = saved
            return False
        # Consume the type to check that it's followed by ')' — ruling out (ident = ...)
        try:
            self.parse_type_spec()
        except Exception:
            self.pos = saved
            return False
        # Skip *, [], and pointer-to-function patterns after the type
        while self.at(TokenType.STAR, TokenType.CONST, TokenType.VOLATILE, TokenType.RESTRICT):
            self.advance()
        while self.match(TokenType.LBRACKET):
            while not self.at(TokenType.RBRACKET) and not self.at(TokenType.EOF):
                self.advance()
            if self.at(TokenType.RBRACKET):
                self.advance()
        result = self.at(TokenType.RPAREN)
        self.pos = saved
        return result

    def parse_sizeof(self) -> Expr:
        t = self.advance()  # sizeof
        if self.at(TokenType.LPAREN) and self.is_cast():
            self.advance()  # (
            type_spec = self.parse_type_spec()
            # Handle array-type sizeof: sizeof(char[N]) or sizeof(T[N])
            while self.match(TokenType.STAR):
                type_spec.pointer_depth += 1
            if self.match(TokenType.LBRACKET):
                dim_expr = None
                if not self.at(TokenType.RBRACKET):
                    dim_expr = self.parse_expr()
                self.expect(TokenType.RBRACKET, "']'")
                if type_spec.array_sizes is None:
                    type_spec.array_sizes = []
                type_spec.array_sizes.append(dim_expr if dim_expr is not None else None)
            self.expect(TokenType.RPAREN, "')'")
            return SizeofExpr(operand=type_spec, is_type=True, line=t.line, col=t.col)
        else:
            operand = self.parse_unary()
            return SizeofExpr(operand=operand, is_type=False, line=t.line, col=t.col)

    def parse_alignof(self) -> Expr:
        t = self.advance()  # _Alignof / __alignof__
        self.expect(TokenType.LPAREN, "'('")
        type_spec = self.parse_type_spec()
        self.expect(TokenType.RPAREN, "')'")
        return AlignofExpr(operand=type_spec, is_type=True, line=t.line, col=t.col)

    def parse_postfix(self) -> Expr:
        expr = self.parse_primary()

        while True:
            if self.match(TokenType.LBRACKET):
                index = self.parse_expr()
                self.expect(TokenType.RBRACKET, "']'")
                expr = ArrayAccess(array=expr, index=index, line=expr.line, col=expr.col)
            elif self.match(TokenType.LPAREN):
                # Check for __builtin_va_arg(ap, type)
                if isinstance(expr, Identifier) and expr.name == "__builtin_va_arg":
                    ap_expr = self.parse_assignment()
                    self.expect(TokenType.COMMA, "','")
                    target_type = self.parse_type_spec()
                    self.expect(TokenType.RPAREN, "')'")
                    expr = BuiltinVaArg(ap=ap_expr, target_type=target_type, line=expr.line, col=expr.col)
                elif isinstance(expr, Identifier) and expr.name == "__builtin_expect":
                    # __builtin_expect(expr, val) — branch hint, just return expr
                    result_expr = self.parse_assignment()
                    self.expect(TokenType.COMMA, "','")
                    self.parse_assignment()  # discard the hint value
                    self.expect(TokenType.RPAREN, "')'")
                    expr = result_expr
                elif isinstance(expr, Identifier) and expr.name == "__builtin_offsetof":
                    # __builtin_offsetof(type, member) — compile-time byte offset
                    target_type = self.parse_type_spec()
                    self.expect(TokenType.COMMA, "','")
                    member_path = [self.expect(TokenType.IDENTIFIER, "member name").value]
                    # Support nested: __builtin_offsetof(T, a.b.c)
                    while self.match(TokenType.DOT):
                        member_path.append(self.expect(TokenType.IDENTIFIER, "member name").value)
                    self.expect(TokenType.RPAREN, "')'")
                    # Compute offset
                    sdef = target_type.struct_def
                    offset = 0
                    for mn in member_path:
                        if sdef is None:
                            self.error(f"__builtin_offsetof: not a struct", expr.line, expr.col)
                        mo = sdef.member_offset(mn)
                        if mo is None:
                            self.error(f"__builtin_offsetof: no member '{mn}'", expr.line, expr.col)
                        offset += mo
                        mt = sdef.member_type(mn)
                        sdef = mt.struct_def if mt else None
                    expr = IntLiteral(value=offset, line=expr.line, col=expr.col)
                else:
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
            suffix = ''.join(c for c in t.value if c in 'uUlL').upper()
            val_str = t.value.rstrip('uUlL')
            if val_str.startswith('0x') or val_str.startswith('0X'):
                val = int(val_str, 16)
            elif val_str.startswith('0') and len(val_str) > 1:
                val = int(val_str, 8)
            else:
                val = int(val_str)
            return IntLiteral(value=val, suffix=suffix, line=t.line, col=t.col)

        if self.match(TokenType.FLOAT_LITERAL):
            raw = t.value
            is_single = raw[-1] in 'fF' if raw else False
            is_long_double = raw[-1] in 'lL' if raw else False
            return FloatLiteral(value=float(raw.rstrip('fFlL')), is_single=is_single,
                                is_long_double=is_long_double, line=t.line, col=t.col)

        if self.match(TokenType.CHAR_LITERAL):
            return IntLiteral(value=ord(t.value), line=t.line, col=t.col)

        if self.current().type in (TokenType.STRING_LITERAL, TokenType.WIDE_STRING_LITERAL):
            t = self.advance()
            wide = t.type == TokenType.WIDE_STRING_LITERAL
            value = t.value
            while self.current().type in (TokenType.STRING_LITERAL, TokenType.WIDE_STRING_LITERAL):
                nt = self.advance()
                if nt.type == TokenType.WIDE_STRING_LITERAL:
                    wide = True
                value += nt.value
            return StringLiteral(value=value, wide=wide, line=t.line, col=t.col)

        if self.match(TokenType.GENERIC):
            # _Generic(controlling-expr, type: expr, ..., default: expr)
            self.expect(TokenType.LPAREN, "'('")
            controlling = self.parse_assignment()
            assocs = []
            while self.match(TokenType.COMMA):
                if self.at(TokenType.DEFAULT):
                    self.advance()  # default
                    self.expect(TokenType.COLON, "':'")
                    assocs.append(GenericAssoc(type_spec=None, expr=self.parse_assignment()))
                else:
                    ts = self.parse_type_spec()
                    # Parse optional array dimensions (e.g. int[4])
                    if self.at(TokenType.LBRACKET):
                        array_sizes = []
                        while self.match(TokenType.LBRACKET):
                            if self.at(TokenType.RBRACKET):
                                array_sizes.append(None)
                            else:
                                array_sizes.append(self.parse_expr())
                            self.expect(TokenType.RBRACKET, "']'")
                        ts.array_sizes = array_sizes
                    self.expect(TokenType.COLON, "':'")
                    assocs.append(GenericAssoc(type_spec=ts, expr=self.parse_assignment()))
            self.expect(TokenType.RPAREN, "')'")
            return GenericSelection(controlling=controlling, associations=assocs,
                                    line=t.line, col=t.col)

        if self.match(TokenType.IDENTIFIER):
            # Check if this is an enum constant (not shadowed by a local variable)
            if t.value in self.enum_values and t.value not in self.declared_vars:
                return IntLiteral(value=self.enum_values[t.value], line=t.line, col=t.col)
            return Identifier(name=t.value, line=t.line, col=t.col)

        if self.match(TokenType.LPAREN):
            # GNU statement expression: ({ ... })
            if self.at(TokenType.LBRACE):
                block = self.parse_block()
                self.expect(TokenType.RPAREN, "')'")
                return StatementExpr(body=block, line=t.line, col=t.col)
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

        if self.at(TokenType.STATIC_ASSERT):
            self._skip_static_assert()
            return Block(stmts=[], line=t.line, col=t.col)

        # Skip __asm__ / asm / __asm statements
        if (self.at(TokenType.IDENTIFIER) and
                self.current().value in ("__asm__", "asm", "__asm")):
            self.advance()  # __asm__
            # Skip optional volatile qualifier
            if self.at(TokenType.VOLATILE) or (self.at(TokenType.IDENTIFIER) and
                    self.current().value in ("__volatile__", "volatile")):
                self.advance()
            if self.match(TokenType.LPAREN):
                depth = 1
                while depth > 0 and not self.at(TokenType.EOF):
                    if self.match(TokenType.LPAREN):
                        depth += 1
                    elif self.match(TokenType.RPAREN):
                        depth -= 1
                    else:
                        self.advance()
            self.match(TokenType.SEMICOLON)
            return Block(stmts=[], line=t.line, col=t.col)

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
            if self.match(TokenType.STAR):
                target = self.parse_expr()
                self.expect(TokenType.SEMICOLON, "';'")
                return IndirectGotoStmt(target=target, line=t.line, col=t.col)
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
        saved_scope = set(self.local_scope)
        stmts = []
        while not self.at(TokenType.RBRACE) and not self.at(TokenType.EOF):
            stmts.append(self.parse_stmt())
        self.expect(TokenType.RBRACE, "'}'")
        self.local_scope = saved_scope
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
        # Track inherent pointer depth from typedef BEFORE parse_type_spec consumes tokens.
        # For `typedef T *alias; alias x, y;`, both x and y should be T* (pd=1 inherent).
        # For `int *x, y;`, only x is T* — the `*` is a declarator star, not inherent.
        cur = self.current()
        inherent_pd = (self.typedefs[cur.value].pointer_depth
                       if cur.type == TokenType.IDENTIFIER and cur.value in self.typedefs
                       else 0)
        type_spec = self.parse_type_spec()
        return self.parse_var_decl_with_type(type_spec, inherent_pd=inherent_pd)

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
            extra_stars = 0
            while self.match(TokenType.STAR):
                extra_stars += 1
            # Skip qualifiers between * and name
            while self.at(TokenType.CONST, TokenType.VOLATILE, TokenType.RESTRICT):
                self.advance()

            # Nested complex declarator: (* (*p)(params))(ret_params)
            if self.at(TokenType.LPAREN):
                # Scan forward to find the identifier name inside nested parens
                # then skip everything.  Also count how many times depth returns to
                # zero inside the outer group (each such event is a closed subgroup
                # like `(*name)` or `(params)` at the top level of the outer group).
                saved = self.pos
                depth = 0
                name = ""
                inner_subgroups = 0  # counts closings at depth→0 inside outer group
                while self.pos < len(self.tokens) - 1:
                    tok = self.current()
                    if tok.type == TokenType.LPAREN:
                        depth += 1
                        self.advance()
                    elif tok.type == TokenType.RPAREN:
                        if depth == 0:
                            break
                        depth -= 1
                        self.advance()
                        if depth == 0:
                            inner_subgroups += 1
                    elif tok.type == TokenType.IDENTIFIER and not name:
                        name = tok.value
                        self.advance()
                    else:
                        self.advance()
                self.expect(TokenType.RPAREN, "')'")  # close outer (*...)
                # Skip trailing param list(s)
                while self.match(TokenType.LPAREN):
                    d = 1
                    while d > 0 and not self.at(TokenType.EOF):
                        if self.match(TokenType.LPAREN): d += 1
                        elif self.match(TokenType.RPAREN): d -= 1
                        else: self.advance()
                # If the inner scan had ≥2 subgroups, the declarator contained an
                # inner pointer group AND a param list, meaning the function returns
                # a function pointer — add one extra pointer level.
                extra_ret_ptr = 1 if inner_subgroups >= 2 else 0
                ts = TypeSpec(base=base_type.base,
                              pointer_depth=base_type.pointer_depth + extra_stars + extra_ret_ptr,
                              struct_def=base_type.struct_def,
                              is_func_ptr=(extra_ret_ptr == 1))
                init = None
                if self.match(TokenType.ASSIGN):
                    init = self.parse_assignment()
                return VarDecl(type_spec=ts, name=name or "__anon__", init=init, line=t.line, col=t.col)

            name = self.expect(TokenType.IDENTIFIER, "variable name").value

            # Handle function pointer array: (*name[4])(params)
            fptr_arr_sizes = []
            while self.match(TokenType.LBRACKET):
                if not self.at(TokenType.RBRACKET):
                    fptr_arr_sizes.append(self.parse_expr())
                else:
                    fptr_arr_sizes.append(None)
                self.expect(TokenType.RBRACKET, "']'")

            self.expect(TokenType.RPAREN, "')'")

            if self.at(TokenType.LBRACKET) and not fptr_arr_sizes:
                # Pointer to array: (*p)[4]
                # Store array size so element stride is computed correctly
                arr_sizes = []
                while self.match(TokenType.LBRACKET):
                    if not self.at(TokenType.RBRACKET):
                        arr_sizes.append(self.parse_expr())
                    else:
                        arr_sizes.append(None)
                    self.expect(TokenType.RBRACKET, "']'")
                ts = TypeSpec(base=base_type.base, pointer_depth=base_type.pointer_depth + extra_stars,
                              is_unsigned=base_type.is_unsigned,
                              array_sizes=arr_sizes if arr_sizes else None)
            elif self.at(TokenType.LPAREN):
                # Function pointer: (*fp)(params) or (*fp[4])(params)
                self.advance()  # (
                depth = 1
                fp_comma_count = 0
                fp_is_variadic = False
                fp_has_params = False
                while depth > 0 and not self.at(TokenType.EOF):
                    if self.match(TokenType.LPAREN):
                        depth += 1
                    elif self.match(TokenType.RPAREN):
                        depth -= 1
                    elif depth == 1 and self.match(TokenType.ELLIPSIS):
                        fp_is_variadic = True
                    elif depth == 1 and self.match(TokenType.COMMA):
                        fp_comma_count += 1
                    else:
                        tok = self.current()
                        if depth == 1 and tok.type == TokenType.IDENTIFIER:
                            fp_has_params = True
                        self.advance()
                # fixed_param_count for variadic: commas before ... separate fixed params
                # (last comma is between last fixed param and ...)
                fp_param_count = (fp_comma_count if fp_is_variadic
                                  else (fp_comma_count + 1 if fp_has_params else 0))
                ts = TypeSpec(base=base_type.base, pointer_depth=base_type.pointer_depth + extra_stars,
                              is_unsigned=base_type.is_unsigned,
                              struct_def=base_type.struct_def,
                              is_ptr_array=bool(fptr_arr_sizes),
                              array_sizes=fptr_arr_sizes if fptr_arr_sizes else None,
                              func_ptr_is_variadic=fp_is_variadic,
                              func_ptr_param_count=fp_param_count if fp_is_variadic else None)
            else:
                ts = TypeSpec(base=base_type.base, pointer_depth=base_type.pointer_depth + extra_stars)
            init = None
            if self.match(TokenType.ASSIGN):
                if self.at(TokenType.LBRACE):
                    init = self.parse_init_list()
                else:
                    init = self.parse_assignment()
            return VarDecl(type_spec=ts, name=name, init=init, line=t.line, col=t.col)

        # Handle parenthesized declarator: int (name) = 42; — strip outer parens.
        # Also supports int (name[]) = {...}; and int *(name) = &a;
        # Note: (*name) is handled above as function pointer
        parenthesized = False
        if self.at(TokenType.LPAREN) and self.peek(1).type == TokenType.IDENTIFIER:
            # Peek ahead: if after identifier we see RPAREN or LBRACKET, this is parenthesized
            if self.peek(2).type == TokenType.RPAREN or self.peek(2).type == TokenType.LBRACKET:
                self.advance()  # (
                parenthesized = True
        name = self.expect(TokenType.IDENTIFIER, "variable name").value

        # Local function declaration or definition: int f(char *); / int f(int n) { ... }
        if self.at(TokenType.LPAREN):
            # Lookahead past the closing ')' to see if '{' follows (definition vs declaration)
            scan, depth = self.pos + 1, 1
            while scan < len(self.tokens) and depth > 0:
                if self.tokens[scan].type == TokenType.LPAREN:
                    depth += 1
                elif self.tokens[scan].type == TokenType.RPAREN:
                    depth -= 1
                scan += 1
            if scan < len(self.tokens) and self.tokens[scan].type == TokenType.LBRACE:
                # Nested function definition — parse fully and stage for lifting
                func = self.parse_func_decl(base_type, name, t)
                self._hoisted_funcs.append((func, self._current_func_name))
                self.match(TokenType.SEMICOLON)  # trailing ';' is optional (GCC allows omitting it)
                return VarDecl(type_spec=TypeSpec(base="void"), name="__nested_skip__",
                               line=t.line, col=t.col)
            else:
                # Forward declaration — skip parameter list
                self.advance()  # (
                depth = 1
                while depth > 0 and not self.at(TokenType.EOF):
                    if self.match(TokenType.LPAREN):
                        depth += 1
                    elif self.match(TokenType.RPAREN):
                        depth -= 1
                    else:
                        self.advance()
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
            array_sizes=base_type.array_sizes,
            is_func_ptr=base_type.is_func_ptr,
            func_ptr_native_depth=base_type.func_ptr_native_depth,
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
            if ts.pointer_depth > 0:
                ts.is_ptr_array = True
            # If the base type (e.g. typedef) already has array dimensions,
            # append them after our outer dimensions.
            if ts.array_sizes:
                ts.array_sizes = array_sizes + list(ts.array_sizes)
            else:
                ts.array_sizes = array_sizes

        # Close parenthesized declarator: (name) or (name[])
        if parenthesized:
            self.expect(TokenType.RPAREN, "')'")

        init = None
        if self.match(TokenType.ASSIGN):
            if self.at(TokenType.LBRACE):
                init = self.parse_init_list()
            else:
                init = self.parse_assignment()

        if name and name != "__skip__":
            self.declared_vars.add(name)
        return VarDecl(type_spec=ts, name=name, init=init, line=t.line, col=t.col)

    def parse_var_decl_with_type(self, type_spec, inherent_pd=0) -> Stmt:
        first = self._parse_single_declarator(type_spec)

        # Check for multiple declarators: int x, *p, **pp;
        # For subsequent declarators, use the base type but reset pointer depth
        # to only the INHERENT part (from typedef), stripping declarator-level stars.
        # e.g. `int *x, y;` → y is int (inherent_pd=0, strip the declarator `*`)
        #      `typedef T *alias; alias x, y;` → y is T* (inherent_pd=1, preserve)
        if self.match(TokenType.COMMA):
            base_for_comma = TypeSpec(
                base=type_spec.base, pointer_depth=inherent_pd,
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
            for d in decls:
                if isinstance(d, VarDecl) and d.name:
                    self.local_scope.add(d.name)
            return Block(stmts=decls, line=first.line, col=first.col)
        else:
            # Nested function definition: semicolon was already consumed (or omitted)
            if isinstance(first, VarDecl) and first.name == "__nested_skip__":
                return NullStmt(line=first.line, col=first.col)
            self.expect(TokenType.SEMICOLON, "';'")
            if isinstance(first, VarDecl) and first.name:
                self.local_scope.add(first.name)
            return first

    # ---- Top-level parsing ----

    def parse_program(self) -> Program:
        decls = []
        while not self.at(TokenType.EOF):
            decl = self.parse_top_level()
            # Iteratively lift nested functions until none remain (handles arbitrary nesting depth)
            if self._hoisted_funcs:
                staged = self._hoisted_funcs[:]
                self._hoisted_funcs.clear()
                if isinstance(decl, FuncDecl) and decl.body is not None:
                    lifted = self._lift_nested_functions(decl, staged)
                    decls.extend(lifted)
            if decl:
                if isinstance(decl, list):
                    decls.extend(decl)
                else:
                    decls.append(decl)
        return Program(declarations=decls)

    def _skip_static_assert(self):
        """Skip _Static_assert(expr, "message"); declaration."""
        self.advance()  # _Static_assert
        self.expect(TokenType.LPAREN, "'('")
        depth = 1
        while depth > 0 and not self.at(TokenType.EOF):
            if self.match(TokenType.LPAREN):
                depth += 1
            elif self.match(TokenType.RPAREN):
                depth -= 1
            else:
                self.advance()
        self.match(TokenType.SEMICOLON)

    def parse_top_level(self) -> Union[FuncDecl, GlobalVarDecl, StructDecl, EnumDecl, TypedefDecl, None]:
        # Skip leading __attribute__ before declarations
        self.skip_attribute()
        t = self.current()

        # _Static_assert: skip entirely
        if self.at(TokenType.STATIC_ASSERT):
            self._skip_static_assert()
            return None

        # Stray semicolon at top-level (e.g., trailing `;` after function definition)
        if self.match(TokenType.SEMICOLON):
            return None

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
                if type_spec.pointer_depth > 0:
                    type_spec.is_ptr_array = True
                type_spec.array_sizes = array_sizes

            init = None
            if self.match(TokenType.ASSIGN):
                if self.at(TokenType.LBRACE):
                    init = self.parse_init_list()
                else:
                    init = self.parse_assignment()
            self.expect(TokenType.SEMICOLON, "';'")
            return GlobalVarDecl(type_spec=type_spec, name=name, init=init, line=t.line, col=t.col)

        if not self.is_type_start():
            # K&R-style implicit int: only allow for empty param list `identifier() { }`
            # Typed param lists without a return type (e.g. `main(void)`) are a C99 error.
            if (t.type == TokenType.IDENTIFIER
                    and self.peek(1).type == TokenType.LPAREN
                    and self.peek(2).type == TokenType.RPAREN):
                type_spec = TypeSpec(base="int")
                name = self.advance().value
                return self.parse_func_decl(type_spec, name, t)
            self.error(f"expected declaration, got '{t.value}'")

        type_spec = self.parse_type_spec()
        self.skip_attribute()  # void __attribute__((stdcall)) foo(void)

        # Global function pointer or function returning function pointer
        if self.at(TokenType.LPAREN) and self.peek(1).type == TokenType.STAR:
            self.advance()  # (
            self.advance()  # *
            # Skip qualifiers
            while self.at(TokenType.CONST, TokenType.VOLATILE, TokenType.RESTRICT):
                self.advance()
            name = self.expect(TokenType.IDENTIFIER, "variable name").value

            # Parse optional array dimensions: (*name[4])(params) or (*name[])(params)
            fptr_arr_sizes = []
            while self.match(TokenType.LBRACKET):
                if not self.at(TokenType.RBRACKET):
                    fptr_arr_sizes.append(self.parse_expr())
                else:
                    fptr_arr_sizes.append(None)
                self.expect(TokenType.RBRACKET, "']'")

            if self.at(TokenType.LPAREN) and not fptr_arr_sizes:
                # Function returning function pointer: int (*f1(params))(ret_params)
                self.advance()  # ( for f1's params
                params = []
                is_variadic = False
                if not self.at(TokenType.RPAREN):
                    if self.at(TokenType.VOID) and self.peek(1).type == TokenType.RPAREN:
                        self.advance()
                    else:
                        params.append(self.parse_param())
                        while self.match(TokenType.COMMA):
                            if self.match(TokenType.ELLIPSIS):
                                is_variadic = True
                                break
                            params.append(self.parse_param())
                self.expect(TokenType.RPAREN, "')'")  # close f1's params
                self.expect(TokenType.RPAREN, "')'")  # close outer (*...)
                # Skip return function's param list
                if self.match(TokenType.LPAREN):
                    depth = 1
                    while depth > 0 and not self.at(TokenType.EOF):
                        if self.match(TokenType.LPAREN): depth += 1
                        elif self.match(TokenType.RPAREN): depth -= 1
                        else: self.advance()
                ret_type = TypeSpec(base=type_spec.base,
                    pointer_depth=type_spec.pointer_depth + 1,
                    struct_def=type_spec.struct_def)
                # Function body or forward declaration
                body = None
                if self.at(TokenType.LBRACE):
                    body = self.parse_block()
                else:
                    self.expect(TokenType.SEMICOLON, "';'")
                return FuncDecl(return_type=ret_type, name=name, params=params,
                                body=body, is_variadic=is_variadic,
                                line=t.line, col=t.col)
            else:
                self.expect(TokenType.RPAREN, "')'")

                if self.at(TokenType.LBRACKET) and not fptr_arr_sizes:
                    # Pointer to array: (*p)[N]
                    arr_sizes = []
                    while self.match(TokenType.LBRACKET):
                        if not self.at(TokenType.RBRACKET):
                            arr_sizes.append(self.parse_expr())
                        else:
                            arr_sizes.append(None)
                        self.expect(TokenType.RBRACKET, "']'")
                    fptr_type = TypeSpec(base=type_spec.base,
                        pointer_depth=type_spec.pointer_depth + 1,
                        is_unsigned=type_spec.is_unsigned,
                        is_extern=type_spec.is_extern, is_static=type_spec.is_static,
                        array_sizes=arr_sizes if arr_sizes else None)
                elif self.at(TokenType.LPAREN):
                    # Function pointer (possibly array): int (*name)(params) or int (*name[N])(params)
                    self.advance()  # (
                    depth = 1
                    gfp_comma_count = 0
                    gfp_is_variadic = False
                    gfp_has_params = False
                    while depth > 0 and not self.at(TokenType.EOF):
                        if self.match(TokenType.LPAREN):
                            depth += 1
                        elif self.match(TokenType.RPAREN):
                            depth -= 1
                        elif depth == 1 and self.match(TokenType.ELLIPSIS):
                            gfp_is_variadic = True
                        elif depth == 1 and self.match(TokenType.COMMA):
                            gfp_comma_count += 1
                        else:
                            tok = self.current()
                            if depth == 1 and tok.type == TokenType.IDENTIFIER:
                                gfp_has_params = True
                            self.advance()
                    gfp_param_count = (gfp_comma_count if gfp_is_variadic
                                       else (gfp_comma_count + 1 if gfp_has_params else 0))
                    fptr_type = TypeSpec(base=type_spec.base,
                        pointer_depth=type_spec.pointer_depth + 1,
                        struct_def=type_spec.struct_def, enum_def=type_spec.enum_def,
                        is_unsigned=type_spec.is_unsigned,
                        is_extern=type_spec.is_extern, is_static=type_spec.is_static,
                        is_ptr_array=bool(fptr_arr_sizes),
                        array_sizes=fptr_arr_sizes if fptr_arr_sizes else None,
                        func_ptr_is_variadic=gfp_is_variadic,
                        func_ptr_param_count=gfp_param_count if gfp_is_variadic else None)
                else:
                    # Regular function pointer variable: int (*name) = init;
                    fptr_type = TypeSpec(base=type_spec.base,
                        pointer_depth=type_spec.pointer_depth + 1,
                        struct_def=type_spec.struct_def, enum_def=type_spec.enum_def,
                        is_unsigned=type_spec.is_unsigned,
                        is_extern=type_spec.is_extern, is_static=type_spec.is_static)

                init = None
                if self.match(TokenType.ASSIGN):
                    if self.at(TokenType.LBRACE):
                        init = self.parse_init_list()
                    else:
                        init = self.parse_expr()
                self.skip_attribute()
                self.expect(TokenType.SEMICOLON, "';'")
                return GlobalVarDecl(type_spec=fptr_type, name=name, init=init, line=t.line, col=t.col)

        # Parenthesized function name: int (func_name)(params)
        # Or parenthesized variable declarator: int (var_name) = 42; int (arr[]) = {...};
        global_parenthesized = False
        if self.at(TokenType.LPAREN) and self.peek(1).type == TokenType.IDENTIFIER and self.peek(2).type == TokenType.RPAREN:
            self.advance()  # (
            name = self.advance().value  # identifier
            self.advance()  # )
            if self.at(TokenType.LPAREN):
                return self.parse_func_decl(type_spec, name, t)
            # Fallthrough to variable declaration
        elif self.at(TokenType.LPAREN) and self.peek(1).type == TokenType.IDENTIFIER and self.peek(2).type == TokenType.LBRACKET:
            # Parenthesized array declarator: int (arr[]) = {...};
            self.advance()  # (
            name = self.advance().value  # identifier
            global_parenthesized = True
            # Fall through; array brackets will be consumed below, then RPAREN
        else:
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
            if type_spec.pointer_depth > 0:
                type_spec.is_ptr_array = True
            # If the base type (e.g. typedef) already has array dimensions,
            # append them after our outer dimensions so stride is correct.
            if type_spec.array_sizes:
                type_spec.array_sizes = array_sizes + type_spec.array_sizes
            else:
                type_spec.array_sizes = array_sizes

        # Close parenthesized declarator: (name[...])
        if global_parenthesized:
            self.expect(TokenType.RPAREN, "')'")

        # Global variable (with possible comma-separated additional declarations)
        init = None
        if self.match(TokenType.ASSIGN):
            if self.at(TokenType.LBRACE):
                init = self.parse_init_list()
            else:
                init = self.parse_assignment()

        self.skip_attribute()  # e.g. void (*fp)(int) __attribute__((common));
        first = GlobalVarDecl(type_spec=type_spec, name=name, init=init, line=t.line, col=t.col)

        # Handle comma-separated global declarations: int a, b = 3, c;
        if self.match(TokenType.COMMA):
            extra = [first]
            while True:
                # Parse additional declarators
                self.skip_attribute()  # e.g. __attribute__((deprecated)) before next name
                extra_ptrs = 0
                while self.match(TokenType.STAR):
                    extra_ptrs += 1
                ename = self.expect(TokenType.IDENTIFIER, "identifier").value
                ets = TypeSpec(base=type_spec.base, pointer_depth=extra_ptrs,
                               is_unsigned=type_spec.is_unsigned, struct_def=type_spec.struct_def,
                               is_static=type_spec.is_static, is_extern=type_spec.is_extern)
                # Array declarator (supports multidimensional)
                arr_sizes = []
                while self.match(TokenType.LBRACKET):
                    if self.at(TokenType.RBRACKET):
                        arr_sizes.append(None)
                    else:
                        arr_sizes.append(self.parse_expr())
                    self.expect(TokenType.RBRACKET, "']'")
                if arr_sizes:
                    ets.array_sizes = arr_sizes
                einit = None
                if self.match(TokenType.ASSIGN):
                    if self.at(TokenType.LBRACE):
                        einit = self.parse_init_list()
                    else:
                        einit = self.parse_assignment()
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
            designator_path = None
            designator_end = None
            if self.at(TokenType.DOT):
                self.advance()
                designator = self.expect(TokenType.IDENTIFIER, "field name").value
                # Chained designator: .a.b = val -> path ["a", "b"]
                if self.at(TokenType.DOT):
                    designator_path = [designator]
                    while self.at(TokenType.DOT):
                        self.advance()
                        designator_path.append(self.expect(TokenType.IDENTIFIER, "field name").value)
                    designator = designator_path[0]
                self.expect(TokenType.ASSIGN, "'='")
            elif self.at(TokenType.LBRACKET):
                self.advance()
                idx_expr = self.parse_expr()
                if isinstance(idx_expr, IntLiteral):
                    designator_index = idx_expr.value
                # Range designator (GCC extension): [start ... end]
                if self.match(TokenType.ELLIPSIS):
                    end_expr = self.parse_expr()
                    if isinstance(end_expr, IntLiteral):
                        designator_end = end_expr.value
                self.expect(TokenType.RBRACKET, "']'")
                self.expect(TokenType.ASSIGN, "'='")

            # Value (could be a nested init list)
            if self.at(TokenType.LBRACE):
                value = self.parse_init_list()
            else:
                value = self.parse_assignment()

            items.append(InitItem(designator=designator, designator_index=designator_index,
                                  designator_path=designator_path, designator_end=designator_end,
                                  value=value))

            if not self.match(TokenType.COMMA):
                break

        self.expect(TokenType.RBRACE, "'}'")
        return InitList(items=items, line=t.line, col=t.col)

    def parse_typedef(self) -> TypedefDecl:
        t = self.advance()  # typedef
        type_spec = self.parse_type_spec()
        td_attrs = self.skip_attribute() or set()  # } __attribute__((packed)) Name;
        if "packed" in td_attrs and type_spec.struct_def:
            type_spec.struct_def.is_packed = True

        # Parenthesized function-type typedef: typedef void (FnName)(params);
        # (different from function POINTER: typedef void (*FnPtr)(params))
        if (self.at(TokenType.LPAREN) and self.peek(1).type == TokenType.IDENTIFIER
                and self.peek(2).type == TokenType.RPAREN):
            self.advance()  # (
            name = self.advance().value  # FnName
            self.advance()  # )
            # Skip param list
            if self.match(TokenType.LPAREN):
                depth = 1
                while depth > 0 and not self.at(TokenType.EOF):
                    if self.match(TokenType.LPAREN): depth += 1
                    elif self.match(TokenType.RPAREN): depth -= 1
                    else: self.advance()
            fn_type = TypeSpec(base=type_spec.base, pointer_depth=type_spec.pointer_depth,
                                struct_def=type_spec.struct_def, enum_def=type_spec.enum_def,
                                is_unsigned=type_spec.is_unsigned, is_func_type=True,
                                func_ptr_native_depth=1)
            self.typedefs[name] = fn_type
            self.skip_attribute()
            self.expect(TokenType.SEMICOLON, "';'")
            return TypedefDecl(type_spec=fn_type, name=name, line=t.line, col=t.col)

        # Function pointer typedef: typedef int (*name)(params);
        # Also handles Apple block pointer typedef: typedef void (^name)(params);
        if self.at(TokenType.LPAREN) and self.peek(1).type in (TokenType.STAR, TokenType.CARET):
            self.advance()  # (
            self.advance()  # * or ^
            # Skip qualifiers and nullability annotations between * and name
            while self.match(TokenType.CONST, TokenType.VOLATILE, TokenType.RESTRICT):
                pass
            while self.at(TokenType.IDENTIFIER) and self.current().value in ("_Nullable", "_Nonnull", "_Null_unspecified", "__nonnull", "__nullable"):
                self.advance()
            name = self.expect(TokenType.IDENTIFIER, "typedef name").value
            # Skip array brackets in fptr array typedef: (*name[4])
            while self.match(TokenType.LBRACKET):
                if not self.at(TokenType.RBRACKET):
                    self.parse_expr()
                self.expect(TokenType.RBRACKET, "']'")
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
                                  is_unsigned=type_spec.is_unsigned, is_func_ptr=True,
                                  func_ptr_native_depth=type_spec.pointer_depth + 1)
            self.typedefs[name] = fptr_type
            self.skip_attribute()
            return TypedefDecl(type_spec=fptr_type, name=name, line=t.line, col=t.col)

        name = self.expect(TokenType.IDENTIFIER, "typedef name").value

        # Function-type typedef: typedef void fn(params); — fn is a function type, fn* is callable
        if self.at(TokenType.LPAREN):
            if self.match(TokenType.LPAREN):
                depth = 1
                while depth > 0 and not self.at(TokenType.EOF):
                    if self.match(TokenType.LPAREN): depth += 1
                    elif self.match(TokenType.RPAREN): depth -= 1
                    else: self.advance()
            fn_type = TypeSpec(base=type_spec.base, pointer_depth=0,
                                struct_def=type_spec.struct_def, enum_def=type_spec.enum_def,
                                is_unsigned=type_spec.is_unsigned, is_func_type=True,
                                func_ptr_native_depth=1)
            self.typedefs[name] = fn_type
            self.skip_attribute()
            self.expect(TokenType.SEMICOLON, "';'")
            return TypedefDecl(type_spec=fn_type, name=name, line=t.line, col=t.col)

        # Handle typedef for arrays: typedef int arr_t[10]; or typedef int mat_t[3][4];
        if self.match(TokenType.LBRACKET):
            dims = []
            if self.at(TokenType.RBRACKET):
                dims.append(None)
            else:
                dims.append(self.parse_expr())
            self.expect(TokenType.RBRACKET, "']'")
            # Additional dimensions
            while self.match(TokenType.LBRACKET):
                if self.at(TokenType.RBRACKET):
                    dims.append(None)
                else:
                    dims.append(self.parse_expr())
                self.expect(TokenType.RBRACKET, "']'")
            type_spec.array_sizes = dims
        self.typedefs[name] = type_spec
        self.skip_attribute()
        # Handle comma-separated typedef names: typedef struct X *A, B;
        # Each name starts from the BASE type (without pointer from first declarator)
        base_pd = type_spec.pointer_depth - (type_spec.pointer_depth if type_spec.pointer_depth > 0 else 0)
        while self.match(TokenType.COMMA):
            extra_ptrs = 0
            while self.match(TokenType.STAR):
                extra_ptrs += 1
            extra_name = self.expect(TokenType.IDENTIFIER, "typedef name").value
            from copy import copy
            extra_ts = copy(type_spec)
            # Reset to base type, then add this declarator's pointer depth
            extra_ts.pointer_depth = extra_ptrs
            self.typedefs[extra_name] = extra_ts
        self.expect(TokenType.SEMICOLON, "';'")
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
        self.skip_attribute()  # void foo(void) __attribute__((stdcall));
        self._skip_asm_label()  # void foo(void) __asm__("name")
        self.skip_attribute()  # void foo(void) __asm__("name") __attribute__(...)

        # Function body or declaration
        if self.at(TokenType.LBRACE):
            outer_name = self._current_func_name
            outer_scope = self.local_scope
            self._current_func_name = name
            self.local_scope = {p.name for p in params if p.name}
            body = self.parse_block()
            self._current_func_name = outer_name
            self.local_scope = outer_scope
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
            param_stars = 0
            while self.match(TokenType.STAR):
                param_stars += 1
            while self.at(TokenType.CONST, TokenType.VOLATILE, TokenType.RESTRICT):
                self.advance()
            if self.at(TokenType.IDENTIFIER):
                name = self.advance().value
            # Skip array brackets: (*name[4]) or (*[4])
            while self.match(TokenType.LBRACKET):
                if not self.at(TokenType.RBRACKET):
                    self.parse_expr()
                self.expect(TokenType.RBRACKET, "']'")
            self.expect(TokenType.RPAREN, "')'")
            type_spec.pointer_depth += param_stars
            # Skip function params if present: (*fp)(int, int)
            if self.match(TokenType.LPAREN):
                depth = 1
                while depth > 0 and not self.at(TokenType.EOF):
                    if self.match(TokenType.LPAREN): depth += 1
                    elif self.match(TokenType.RPAREN): depth -= 1
                    else: self.advance()
            return Param(type_spec=type_spec, name=name)
        # Named function-type parameter: void(callback)(int) → callback is void(*)(int)
        if (not name and self.at(TokenType.LPAREN) and
                self.peek(1).type == TokenType.IDENTIFIER and
                self.peek(1).value not in self.typedefs and
                self.peek(2).type == TokenType.RPAREN):
            self.advance()  # (
            name = self.advance().value  # callback
            self.advance()  # )
            # Skip trailing parameter list: (int, ...)
            if self.match(TokenType.LPAREN):
                depth = 1
                while depth > 0 and not self.at(TokenType.EOF):
                    if self.match(TokenType.LPAREN): depth += 1
                    elif self.match(TokenType.RPAREN): depth -= 1
                    else: self.advance()
            type_spec.pointer_depth += 1  # function type decays to pointer
            return Param(type_spec=type_spec, name=name)
        # Abstract function/array type param: int (), int (int), int ([4]) — decays to ptr
        if not name and self.at(TokenType.LPAREN) and self.peek(1).type != TokenType.STAR:
            if (self.peek(1).type == TokenType.RPAREN or
                    self.peek(1).type == TokenType.LBRACKET or
                    self.peek(1).type in self.TYPE_SPECIFIERS or
                    (self.peek(1).type == TokenType.IDENTIFIER and self.peek(1).value in self.typedefs)):
                self.advance()  # (
                depth = 1
                while depth > 0 and not self.at(TokenType.EOF):
                    if self.match(TokenType.LPAREN): depth += 1
                    elif self.match(TokenType.RPAREN): depth -= 1
                    else: self.advance()
                type_spec.pointer_depth += 1  # function type decays to pointer
                return Param(type_spec=type_spec, name=name)
        if self.at(TokenType.IDENTIFIER):
            name = self.advance().value
        self.skip_attribute()  # e.g. int x __attribute__((unused))
        if self.at(TokenType.LPAREN):
            depth = 0
            while self.match(TokenType.LPAREN):
                depth += 1
            while depth > 0 and not self.at(TokenType.EOF):
                if self.match(TokenType.LPAREN):
                    depth += 1
                elif self.match(TokenType.RPAREN):
                    depth -= 1
                else:
                    self.advance()
            type_spec.pointer_depth += 1  # function type decays to pointer in params
            return Param(type_spec=type_spec, name=name)
        # Array parameter: int a[] or int a[100] or int a[const 5] — decays to pointer
        # Supports multidimensional: int a[][2], int a[n][m]
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
            # Parse additional dimensions (e.g. [][2], [n][m]) and preserve them
            inner_dims = []
            while self.match(TokenType.LBRACKET):
                if not self.at(TokenType.RBRACKET):
                    inner_dims.append(self.parse_expr())
                else:
                    inner_dims.append(None)
                self.expect(TokenType.RBRACKET, "']'")
            if inner_dims:
                type_spec.array_sizes = inner_dims
        # Typedef'd array type decays to pointer in function parameters.
        # For multi-dim typedef arrays T[N][M], decay the outer dim only:
        # becomes T (*)[M] — pointer to array of M, keeping inner dim for stride.
        elif type_spec.is_array() and type_spec.array_sizes:
            type_spec.pointer_depth += 1
            # Keep inner dimensions (for stride); drop only the outer dim
            if len(type_spec.array_sizes) > 1:
                type_spec.array_sizes = type_spec.array_sizes[1:]
            else:
                type_spec.array_sizes = None
        return Param(type_spec=type_spec, name=name)

    # ---- Nested function lifting ----

    def _collect_local_types(self, node, out):
        """Recursively collect VarDecl name -> TypeSpec from a statement tree."""
        if node is None:
            return
        if isinstance(node, Block):
            for s in node.stmts:
                self._collect_local_types(s, out)
        elif isinstance(node, VarDecl):
            if node.name and node.name != "__skip__":
                out[node.name] = node.type_spec
        elif isinstance(node, IfStmt):
            self._collect_local_types(node.then_body, out)
            self._collect_local_types(node.else_body, out)
        elif isinstance(node, (WhileStmt, DoWhileStmt)):
            self._collect_local_types(node.body, out)
        elif isinstance(node, ForStmt):
            self._collect_local_types(node.init, out)
            self._collect_local_types(node.body, out)
        elif isinstance(node, SwitchStmt):
            self._collect_local_types(node.body, out)
        elif isinstance(node, CaseStmt):
            self._collect_local_types(node.stmt, out)
        elif isinstance(node, LabelStmt):
            self._collect_local_types(node.stmt, out)

    def _collect_local_names(self, node, out):
        """Recursively collect VarDecl names from a statement tree."""
        if node is None:
            return
        if isinstance(node, Block):
            for s in node.stmts:
                self._collect_local_names(s, out)
        elif isinstance(node, VarDecl):
            if node.name and node.name != "__skip__":
                out.add(node.name)
        elif isinstance(node, IfStmt):
            self._collect_local_names(node.then_body, out)
            self._collect_local_names(node.else_body, out)
        elif isinstance(node, (WhileStmt, DoWhileStmt)):
            self._collect_local_names(node.body, out)
        elif isinstance(node, ForStmt):
            self._collect_local_names(node.init, out)
            self._collect_local_names(node.body, out)
        elif isinstance(node, SwitchStmt):
            self._collect_local_names(node.body, out)
        elif isinstance(node, CaseStmt):
            self._collect_local_names(node.stmt, out)
        elif isinstance(node, LabelStmt):
            self._collect_local_names(node.stmt, out)

    def _find_free_vars(self, node, bound):
        """Return set of identifier names referenced in node that are not in bound."""
        free = set()
        self._collect_free(node, bound, free)
        return free

    def _collect_free(self, node, bound, free):
        if node is None:
            return
        if isinstance(node, Identifier):
            if node.name not in bound:
                free.add(node.name)
        elif isinstance(node, (IntLiteral, CharLiteral, StringLiteral, FloatLiteral)):
            pass
        elif isinstance(node, BinaryOp):
            self._collect_free(node.left, bound, free)
            self._collect_free(node.right, bound, free)
        elif isinstance(node, UnaryOp):
            self._collect_free(node.operand, bound, free)
        elif isinstance(node, Assignment):
            self._collect_free(node.target, bound, free)
            self._collect_free(node.value, bound, free)
        elif isinstance(node, FuncCall):
            self._collect_free(node.name, bound, free)
            for a in node.args:
                self._collect_free(a, bound, free)
        elif isinstance(node, ArrayAccess):
            self._collect_free(node.array, bound, free)
            self._collect_free(node.index, bound, free)
        elif isinstance(node, MemberAccess):
            self._collect_free(node.obj, bound, free)
        elif isinstance(node, TernaryOp):
            self._collect_free(node.condition, bound, free)
            self._collect_free(node.true_expr, bound, free)
            self._collect_free(node.false_expr, bound, free)
        elif isinstance(node, CastExpr):
            self._collect_free(node.operand, bound, free)
        elif isinstance(node, SizeofExpr):
            if not node.is_type:
                self._collect_free(node.operand, bound, free)
        elif isinstance(node, CommaExpr):
            for e in node.exprs:
                self._collect_free(e, bound, free)
        elif isinstance(node, InitList):
            for item in node.items:
                if item.value:
                    self._collect_free(item.value, bound, free)
        elif isinstance(node, StatementExpr):
            self._collect_free(node.body, bound, free)
        elif isinstance(node, BuiltinVaArg):
            self._collect_free(node.ap, bound, free)
        elif isinstance(node, GenericSelection):
            self._collect_free(node.controlling, bound, free)
            for assoc in node.associations:
                self._collect_free(assoc.expr, bound, free)
        elif isinstance(node, Block):
            for s in node.stmts:
                self._collect_free(s, bound, free)
        elif isinstance(node, ReturnStmt):
            self._collect_free(node.value, bound, free)
        elif isinstance(node, ExprStmt):
            self._collect_free(node.expr, bound, free)
        elif isinstance(node, VarDecl):
            if node.init:
                self._collect_free(node.init, bound, free)
        elif isinstance(node, IfStmt):
            self._collect_free(node.condition, bound, free)
            self._collect_free(node.then_body, bound, free)
            self._collect_free(node.else_body, bound, free)
        elif isinstance(node, WhileStmt):
            self._collect_free(node.condition, bound, free)
            self._collect_free(node.body, bound, free)
        elif isinstance(node, DoWhileStmt):
            self._collect_free(node.condition, bound, free)
            self._collect_free(node.body, bound, free)
        elif isinstance(node, ForStmt):
            self._collect_free(node.init, bound, free)
            self._collect_free(node.condition, bound, free)
            self._collect_free(node.update, bound, free)
            self._collect_free(node.body, bound, free)
        elif isinstance(node, SwitchStmt):
            self._collect_free(node.expr, bound, free)
            self._collect_free(node.body, bound, free)
        elif isinstance(node, CaseStmt):
            self._collect_free(node.value, bound, free)
            self._collect_free(node.stmt, bound, free)
        elif isinstance(node, LabelStmt):
            self._collect_free(node.stmt, bound, free)

    def _rewrite_expr(self, expr, scalar_caps, array_caps, func_rename, cap_order, in_nested):
        """
        Rewrite an expression for nested-function lifting.
          scalar_caps:  set of scalar captured var names
          array_caps:   set of array captured var names
          func_rename:  {old_name: new_name}
          cap_order:    ordered list of all captured var names (for appending to calls)
          in_nested:    True  = inside nested body (deref caps, forward __cap_ to recursive calls)
                        False = inside outer body (no deref, pass &scalar / array to calls)
        """
        if expr is None:
            return None
        if isinstance(expr, Identifier):
            if in_nested and expr.name in scalar_caps:
                return UnaryOp(op="*",
                               operand=Identifier(name=f"__cap_{expr.name}"))
            if in_nested and expr.name in array_caps:
                return Identifier(name=f"__cap_{expr.name}")
            if expr.name in func_rename:
                return Identifier(name=func_rename[expr.name])
            return expr
        if isinstance(expr, FuncCall):
            callee_orig = expr.name.name if isinstance(expr.name, Identifier) else None
            expr.name = self._rewrite_expr(expr.name, scalar_caps, array_caps,
                                            func_rename, cap_order, in_nested)
            expr.args = [self._rewrite_expr(a, scalar_caps, array_caps,
                                             func_rename, cap_order, in_nested)
                         for a in expr.args]
            if callee_orig in func_rename:
                for cap_name in cap_order:
                    if in_nested:
                        expr.args.append(Identifier(name=f"__cap_{cap_name}"))
                    elif cap_name in scalar_caps:
                        expr.args.append(UnaryOp(op="&",
                                                  operand=Identifier(name=cap_name)))
                    else:
                        # Array capture: array name decays to pointer
                        expr.args.append(Identifier(name=cap_name))
            return expr
        if isinstance(expr, BinaryOp):
            expr.left  = self._rewrite_expr(expr.left,  scalar_caps, array_caps, func_rename, cap_order, in_nested)
            expr.right = self._rewrite_expr(expr.right, scalar_caps, array_caps, func_rename, cap_order, in_nested)
        elif isinstance(expr, UnaryOp):
            expr.operand = self._rewrite_expr(expr.operand, scalar_caps, array_caps, func_rename, cap_order, in_nested)
        elif isinstance(expr, Assignment):
            expr.target = self._rewrite_expr(expr.target, scalar_caps, array_caps, func_rename, cap_order, in_nested)
            expr.value  = self._rewrite_expr(expr.value,  scalar_caps, array_caps, func_rename, cap_order, in_nested)
        elif isinstance(expr, ArrayAccess):
            expr.array = self._rewrite_expr(expr.array, scalar_caps, array_caps, func_rename, cap_order, in_nested)
            expr.index = self._rewrite_expr(expr.index, scalar_caps, array_caps, func_rename, cap_order, in_nested)
        elif isinstance(expr, MemberAccess):
            expr.obj = self._rewrite_expr(expr.obj, scalar_caps, array_caps, func_rename, cap_order, in_nested)
        elif isinstance(expr, TernaryOp):
            expr.condition = self._rewrite_expr(expr.condition, scalar_caps, array_caps, func_rename, cap_order, in_nested)
            expr.true_expr  = self._rewrite_expr(expr.true_expr,  scalar_caps, array_caps, func_rename, cap_order, in_nested)
            expr.false_expr = self._rewrite_expr(expr.false_expr, scalar_caps, array_caps, func_rename, cap_order, in_nested)
        elif isinstance(expr, CastExpr):
            expr.operand = self._rewrite_expr(expr.operand, scalar_caps, array_caps, func_rename, cap_order, in_nested)
        elif isinstance(expr, SizeofExpr):
            if not expr.is_type:
                expr.operand = self._rewrite_expr(expr.operand, scalar_caps, array_caps, func_rename, cap_order, in_nested)
        elif isinstance(expr, CommaExpr):
            expr.exprs = [self._rewrite_expr(e, scalar_caps, array_caps, func_rename, cap_order, in_nested)
                          for e in expr.exprs]
        elif isinstance(expr, InitList):
            for item in expr.items:
                if item.value:
                    item.value = self._rewrite_expr(item.value, scalar_caps, array_caps, func_rename, cap_order, in_nested)
        elif isinstance(expr, StatementExpr):
            self._rewrite_stmts(expr.body, scalar_caps, array_caps, func_rename, cap_order, in_nested)
        elif isinstance(expr, BuiltinVaArg):
            expr.ap = self._rewrite_expr(expr.ap, scalar_caps, array_caps, func_rename, cap_order, in_nested)
        elif isinstance(expr, GenericSelection):
            expr.controlling = self._rewrite_expr(expr.controlling, scalar_caps, array_caps, func_rename, cap_order, in_nested)
            for assoc in expr.associations:
                assoc.expr = self._rewrite_expr(assoc.expr, scalar_caps, array_caps, func_rename, cap_order, in_nested)
        return expr

    def _rewrite_stmts(self, node, scalar_caps, array_caps, func_rename, cap_order, in_nested):
        """Recursively rewrite statements in place."""
        if node is None:
            return
        R = lambda e: self._rewrite_expr(e, scalar_caps, array_caps, func_rename, cap_order, in_nested)
        S = lambda n: self._rewrite_stmts(n, scalar_caps, array_caps, func_rename, cap_order, in_nested)
        if isinstance(node, Block):
            for s in node.stmts:
                S(s)
        elif isinstance(node, ExprStmt):
            node.expr = R(node.expr)
        elif isinstance(node, ReturnStmt):
            if node.value:
                node.value = R(node.value)
        elif isinstance(node, VarDecl):
            if node.init:
                node.init = R(node.init)
        elif isinstance(node, IfStmt):
            node.condition = R(node.condition)
            S(node.then_body)
            if node.else_body:
                S(node.else_body)
        elif isinstance(node, WhileStmt):
            node.condition = R(node.condition)
            S(node.body)
        elif isinstance(node, DoWhileStmt):
            node.condition = R(node.condition)
            S(node.body)
        elif isinstance(node, ForStmt):
            if node.init:
                S(node.init)
            if node.condition:
                node.condition = R(node.condition)
            if node.update:
                node.update = R(node.update)
            S(node.body)
        elif isinstance(node, SwitchStmt):
            node.expr = R(node.expr)
            S(node.body)
        elif isinstance(node, CaseStmt):
            if node.value:
                node.value = R(node.value)
            if node.stmt:
                S(node.stmt)
        elif isinstance(node, LabelStmt):
            if node.stmt:
                S(node.stmt)

    def _lift_nested_functions(self, outer_func, all_staged, match_name=None):
        """
        Lift all nested functions belonging to outer_func (and recursively to their children).
        match_name: the name to match against in all_staged (defaults to outer_func.name,
                    but uses the original pre-mangling name when recursing).
        Returns list of hoisted FuncDecl nodes (innermost-first order).
        """
        from copy import deepcopy
        if match_name is None:
            match_name = outer_func.name

        outer_names = {}
        for p in outer_func.params:
            outer_names[p.name] = p.type_spec
        self._collect_local_types(outer_func.body, outer_names)

        mine      = [(f, n) for f, n in all_staged if n == match_name]
        remaining = [(f, n) for f, n in all_staged if n != match_name]

        result = []
        for nested_func, _ in mine:
            original_name = nested_func.name
            mangled_name  = f"__nested_{match_name}__{original_name}"

            # Nested function's own scope (params + locals)
            nested_scope = {p.name for p in nested_func.params}
            self._collect_local_names(nested_func.body, nested_scope)

            # Captured = free vars in nested body that exist in outer scope
            free = self._find_free_vars(nested_func.body, nested_scope)
            captured = sorted(free & set(outer_names))

            scalar_caps = {n for n in captured if not outer_names[n].is_array()}
            array_caps  = {n for n in captured if     outer_names[n].is_array()}

            # Append hidden pointer params to nested function
            for cap_name in captured:
                cap_ts = outer_names[cap_name]
                ptr_ts = deepcopy(cap_ts)
                if cap_ts.is_array():
                    # Array: strip dimensions, use pointer to element type
                    ptr_ts.array_sizes = None
                    ptr_ts.pointer_depth += 1
                else:
                    ptr_ts.pointer_depth += 1
                nested_func.params.append(Param(type_spec=ptr_ts, name=f"__cap_{cap_name}"))

            nested_func.name = mangled_name
            func_rename = {original_name: mangled_name}

            # Rewrite nested body: deref captured vars, rename self-recursive calls
            self._rewrite_stmts(nested_func.body, scalar_caps, array_caps,
                                 func_rename, captured, in_nested=True)

            # Rewrite outer body: rename call sites, append addresses/values
            self._rewrite_stmts(outer_func.body, scalar_caps, array_caps,
                                 func_rename, captured, in_nested=False)

            # Recursively lift functions staged inside nested_func
            child_items = [(f, n) for f, n in remaining if n == original_name]
            remaining   = [(f, n) for f, n in remaining if n != original_name]
            child_hoisted = self._lift_nested_functions(nested_func, child_items + remaining,
                                                         match_name=original_name)

            result.extend(child_hoisted)
            result.append(nested_func)

        return result
