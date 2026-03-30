"""JMCC AST Node definitions."""

from dataclasses import dataclass, field
from typing import List, Optional, Union


# Types

@dataclass
class StructDef:
    """Definition of a struct/union type."""
    name: Optional[str] = None  # None for anonymous structs
    members: List['StructMember'] = field(default_factory=list)
    is_union: bool = False

    def _member_total_size(self, ts):
        """Get total size of a type including array dimensions."""
        size = ts.size_bytes()
        if ts.is_array() and ts.array_sizes:
            from jmcc.ast_nodes import IntLiteral  # avoid circular at module level
            first = ts.array_sizes[0]
            if isinstance(first, IntLiteral):
                size *= first.value
        return size

    def size_bytes(self):
        if self.is_union:
            return max((self._member_total_size(m.type_spec) for m in self.members), default=0)
        total = 0
        for m in self.members:
            elem_size = m.type_spec.size_bytes()  # element size for alignment
            actual_size = self._member_total_size(m.type_spec)
            # Align to element size
            align = min(elem_size, 8)
            if align > 0:
                total = (total + align - 1) & ~(align - 1)
            total += actual_size
        # Align total to 8
        if total > 0:
            total = (total + 7) & ~7
        return total

    def member_offset(self, name):
        if self.is_union:
            return 0
        offset = 0
        for m in self.members:
            elem_size = m.type_spec.size_bytes()
            actual_size = self._member_total_size(m.type_spec)
            align = min(elem_size, 8)
            if align > 0:
                offset = (offset + align - 1) & ~(align - 1)
            if m.name == name:
                return offset
            offset += actual_size
        return None

    def member_type(self, name):
        for m in self.members:
            if m.name == name:
                return m.type_spec
        return None


@dataclass
class StructMember:
    type_spec: 'TypeSpec' = None
    name: str = ""


@dataclass
class EnumDef:
    """Definition of an enum type."""
    name: Optional[str] = None
    members: List['EnumMember'] = field(default_factory=list)


@dataclass
class EnumMember:
    name: str = ""
    value: Optional[int] = None


@dataclass
class TypeSpec:
    """Represents a C type."""
    base: str  # "int", "char", "void", "long", "short", "unsigned", "struct X", "enum X"
    pointer_depth: int = 0  # number of * levels
    is_unsigned: bool = False
    is_const: bool = False
    is_volatile: bool = False
    is_static: bool = False
    is_extern: bool = False
    array_sizes: Optional[List[Optional['Expr']]] = None  # None = unsized, e.g. int[]
    struct_def: Optional[StructDef] = None  # populated for struct types
    enum_def: Optional[EnumDef] = None  # populated for enum types

    def is_pointer(self):
        return self.pointer_depth > 0

    def is_array(self):
        return self.array_sizes is not None and len(self.array_sizes) > 0

    def is_void(self):
        return self.base == "void" and self.pointer_depth == 0

    def is_struct(self):
        return self.struct_def is not None

    def is_enum(self):
        return self.enum_def is not None

    def size_bytes(self):
        """Return size in bytes for basic types (x86-64)."""
        if self.pointer_depth > 0:
            return 8
        if self.struct_def:
            return self.struct_def.size_bytes()
        if self.enum_def:
            return 4  # enums are int-sized
        sizes = {
            "char": 1,
            "short": 2,
            "int": 4,
            "long": 8,
            "long long": 8,
            "float": 4,
            "double": 8,
            "long double": 16,
            "void": 0,
        }
        return sizes.get(self.base, 4)

    def __eq__(self, other):
        if not isinstance(other, TypeSpec):
            return False
        return (self.base == other.base and
                self.pointer_depth == other.pointer_depth and
                self.is_unsigned == other.is_unsigned)

    def __hash__(self):
        return hash((self.base, self.pointer_depth, self.is_unsigned))

    def __repr__(self):
        parts = []
        if self.is_unsigned:
            parts.append("unsigned")
        parts.append(self.base)
        parts.append("*" * self.pointer_depth)
        return " ".join(parts)


# Expressions

@dataclass
class Expr:
    line: int = 0
    col: int = 0


@dataclass
class IntLiteral(Expr):
    value: int = 0


@dataclass
class CharLiteral(Expr):
    value: str = ""


@dataclass
class StringLiteral(Expr):
    value: str = ""


@dataclass
class FloatLiteral(Expr):
    value: float = 0.0


@dataclass
class Identifier(Expr):
    name: str = ""


@dataclass
class BinaryOp(Expr):
    op: str = ""  # "+", "-", "*", "/", "%", "==", "!=", "<", ">", "<=", ">=", "&&", "||", "&", "|", "^", "<<", ">>"
    left: Optional[Expr] = None
    right: Optional[Expr] = None


@dataclass
class UnaryOp(Expr):
    op: str = ""  # "-", "!", "~", "&", "*", "++", "--"
    operand: Optional[Expr] = None
    prefix: bool = True  # True for prefix, False for postfix (++/--)


@dataclass
class Assignment(Expr):
    op: str = "="  # "=", "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=", "<<=", ">>="
    target: Optional[Expr] = None
    value: Optional[Expr] = None


@dataclass
class FuncCall(Expr):
    name: Optional[Expr] = None
    args: List[Expr] = field(default_factory=list)


@dataclass
class ArrayAccess(Expr):
    array: Optional[Expr] = None
    index: Optional[Expr] = None


@dataclass
class MemberAccess(Expr):
    obj: Optional[Expr] = None
    member: str = ""
    arrow: bool = False  # True for ->, False for .


@dataclass
class TernaryOp(Expr):
    condition: Optional[Expr] = None
    true_expr: Optional[Expr] = None
    false_expr: Optional[Expr] = None


@dataclass
class CastExpr(Expr):
    target_type: Optional[TypeSpec] = None
    operand: Optional[Expr] = None


@dataclass
class SizeofExpr(Expr):
    operand: Optional[Union[Expr, TypeSpec]] = None
    is_type: bool = False


@dataclass
class CommaExpr(Expr):
    exprs: List[Expr] = field(default_factory=list)


@dataclass
class InitList(Expr):
    """Initializer list: { expr, expr, ... } or { .field = expr, ... }"""
    items: List['InitItem'] = field(default_factory=list)


@dataclass
class InitItem:
    designator: Optional[str] = None  # field name for designated init, or None
    designator_index: Optional[int] = None  # array index for [n] = expr
    value: Optional[Expr] = None


# Statements

@dataclass
class Stmt:
    line: int = 0
    col: int = 0


@dataclass
class ReturnStmt(Stmt):
    value: Optional[Expr] = None


@dataclass
class ExprStmt(Stmt):
    expr: Optional[Expr] = None


@dataclass
class VarDecl(Stmt):
    type_spec: Optional[TypeSpec] = None
    name: str = ""
    init: Optional[Expr] = None


@dataclass
class Block(Stmt):
    stmts: List[Stmt] = field(default_factory=list)


@dataclass
class IfStmt(Stmt):
    condition: Optional[Expr] = None
    then_body: Optional[Stmt] = None
    else_body: Optional[Stmt] = None


@dataclass
class WhileStmt(Stmt):
    condition: Optional[Expr] = None
    body: Optional[Stmt] = None


@dataclass
class DoWhileStmt(Stmt):
    condition: Optional[Expr] = None
    body: Optional[Stmt] = None


@dataclass
class ForStmt(Stmt):
    init: Optional[Stmt] = None  # VarDecl or ExprStmt
    condition: Optional[Expr] = None
    update: Optional[Expr] = None
    body: Optional[Stmt] = None


@dataclass
class BreakStmt(Stmt):
    pass


@dataclass
class ContinueStmt(Stmt):
    pass


@dataclass
class GotoStmt(Stmt):
    label: str = ""


@dataclass
class LabelStmt(Stmt):
    label: str = ""
    stmt: Optional[Stmt] = None


@dataclass
class SwitchStmt(Stmt):
    expr: Optional[Expr] = None
    body: Optional[Stmt] = None


@dataclass
class CaseStmt(Stmt):
    value: Optional[Expr] = None  # None for default
    stmt: Optional[Stmt] = None
    is_default: bool = False


@dataclass
class NullStmt(Stmt):
    """Empty statement (just a semicolon)."""
    pass


# Top-level declarations

@dataclass
class Param:
    type_spec: Optional[TypeSpec] = None
    name: str = ""


@dataclass
class FuncDecl:
    return_type: Optional[TypeSpec] = None
    name: str = ""
    params: List[Param] = field(default_factory=list)
    body: Optional[Block] = None  # None for forward declarations
    is_variadic: bool = False
    line: int = 0
    col: int = 0


@dataclass
class GlobalVarDecl:
    type_spec: Optional[TypeSpec] = None
    name: str = ""
    init: Optional[Expr] = None
    line: int = 0
    col: int = 0


@dataclass
class StructDecl:
    """Top-level struct/union definition (also used as statement)."""
    struct_def: Optional[StructDef] = None
    line: int = 0
    col: int = 0


@dataclass
class EnumDecl:
    """Top-level enum definition."""
    enum_def: Optional[EnumDef] = None
    line: int = 0
    col: int = 0


@dataclass
class TypedefDecl:
    """Typedef declaration."""
    type_spec: Optional[TypeSpec] = None
    name: str = ""
    line: int = 0
    col: int = 0


@dataclass
class Program:
    declarations: List[Union[FuncDecl, GlobalVarDecl, StructDecl, EnumDecl, TypedefDecl]] = field(default_factory=list)
