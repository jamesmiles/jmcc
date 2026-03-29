"""JMCC AST Node definitions."""

from dataclasses import dataclass, field
from typing import List, Optional, Union


# Types

@dataclass
class TypeSpec:
    """Represents a C type."""
    base: str  # "int", "char", "void", "long", "short", "unsigned", etc.
    pointer_depth: int = 0  # number of * levels
    is_unsigned: bool = False
    is_const: bool = False
    is_volatile: bool = False
    is_static: bool = False
    is_extern: bool = False
    array_sizes: Optional[List[Optional['Expr']]] = None  # None = unsized, e.g. int[]

    def is_pointer(self):
        return self.pointer_depth > 0

    def is_array(self):
        return self.array_sizes is not None and len(self.array_sizes) > 0

    def is_void(self):
        return self.base == "void" and self.pointer_depth == 0

    def size_bytes(self):
        """Return size in bytes for basic types (x86-64)."""
        if self.pointer_depth > 0:
            return 8
        sizes = {
            "char": 1,
            "short": 2,
            "int": 4,
            "long": 8,
            "long long": 8,
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
class Program:
    declarations: List[Union[FuncDecl, GlobalVarDecl]] = field(default_factory=list)
