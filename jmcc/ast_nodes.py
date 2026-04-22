"""JMCC AST Node definitions."""

from dataclasses import dataclass, field
from typing import List, Optional, Union
from .targets import resolve_target


# Types

@dataclass
class StructDef:
    """Definition of a struct/union type."""
    name: Optional[str] = None  # None for anonymous structs
    members: List['StructMember'] = field(default_factory=list)
    is_union: bool = False
    is_packed: bool = False

    @staticmethod
    def _eval_dim(dim, target=None):
        """Evaluate an array dimension expression to an integer."""
        if dim is None:
            return None
        if isinstance(dim, IntLiteral):
            return dim.value
        if isinstance(dim, BinaryOp):
            left = StructDef._eval_dim(dim.left, target)
            right = StructDef._eval_dim(dim.right, target)
            if left is not None and right is not None:
                ops = {'+': lambda a, b: a + b, '-': lambda a, b: a - b,
                       '*': lambda a, b: a * b, '/': lambda a, b: a // b if b else 0,
                       '%': lambda a, b: a % b if b else 0,
                       '<<': lambda a, b: a << b, '>>': lambda a, b: a >> b}
                if dim.op in ops:
                    return ops[dim.op](left, right)
        if isinstance(dim, UnaryOp) and dim.op == '-':
            val = StructDef._eval_dim(dim.operand, target)
            return -val if val is not None else None
        if isinstance(dim, SizeofExpr):
            if dim.is_type:
                ts = dim.operand
                size = ts.size_bytes(target)
                if ts.struct_def and not ts.is_pointer():
                    size = ts.struct_def.size_bytes(target)
                if (ts.is_array() or ts.is_ptr_array) and ts.array_sizes:
                    for d in ts.array_sizes:
                        dv = StructDef._eval_dim(d, target)
                        if dv is not None:
                            size *= dv
                return size
            else:
                return StructDef._eval_dim(dim.operand, target)
        if isinstance(dim, CastExpr):
            return StructDef._eval_dim(dim.operand, target)
        if isinstance(dim, Identifier):
            # Try enum values via EnumDef lookup (not directly accessible here; return None)
            return None
        return None

    def _member_total_size(self, ts, target=None):
        """Get total size of a type including all array dimensions."""
        size = ts.size_bytes(target)
        if ts.struct_def and not ts.is_pointer():
            size = ts.struct_def.size_bytes(target)
        if (ts.is_array() or ts.is_ptr_array) and ts.array_sizes:
            for dim in ts.array_sizes:
                if dim is None:
                    return 0  # Flexible array member: size 0
                dv = self._eval_dim(dim, target)
                if dv is not None:
                    size *= dv
        return size

    def _member_align(self, ts, target=None):
        """Get alignment of a type (element alignment for arrays, recursive for structs)."""
        target_spec = resolve_target(target)
        if ts.is_pointer():
            return target_spec.layout.pointer_size
        if ts.struct_def:
            return ts.struct_def.alignment(target)
        # For arrays, alignment is element alignment
        size = ts.size_bytes(target)
        return min(size, target_spec.layout.max_scalar_align) if size > 0 else 1

    def alignment(self, target=None):
        """Return the alignment of this struct/union."""
        if self.is_packed:
            return 1
        max_align = 1
        for m in self.members:
            ma = self._member_align(m.type_spec, target)
            if ma > max_align:
                max_align = ma
        return max_align

    def _layout_members(self, target=None):
        """Compute layout for each member, with bitfield packing.
        Returns list of tuples:
          (offset, size) for non-bitfields
          (unit_offset, unit_size, bit_start, bit_width) for bitfields
        And total struct size."""
        if self.is_union:
            return [(0, self._member_total_size(m.type_spec, target)) for m in self.members], \
                   max((self._member_total_size(m.type_spec, target) for m in self.members), default=0)
        result = []
        total = 0
        bf_bits_used = 0  # bits consumed in current bitfield unit
        bf_unit_size = 0  # size of current bitfield unit (bytes)
        bf_unit_start = 0  # byte offset where current bitfield unit starts
        for m in self.members:
            if m.bit_width is not None:
                # Bitfield member
                unit_size = self._member_total_size(m.type_spec, target)  # e.g., 4 for unsigned int
                unit_bits = unit_size * 8
                if bf_unit_size == 0 or bf_bits_used + m.bit_width > unit_bits:
                    # Start new bitfield unit
                    total += bf_unit_size  # close previous unit if any
                    align = self._member_align(m.type_spec, target)
                    if align > 0:
                        total = (total + align - 1) & ~(align - 1)
                    bf_unit_start = total
                    bf_unit_size = unit_size
                    bit_start = 0
                    bf_bits_used = m.bit_width
                else:
                    # Pack into current unit
                    bit_start = bf_bits_used
                    bf_bits_used += m.bit_width
                result.append((bf_unit_start, unit_size, bit_start, m.bit_width))
            else:
                # Non-bitfield: close any pending bitfield unit
                total += bf_unit_size
                bf_unit_size = 0
                bf_bits_used = 0
                align = self._member_align(m.type_spec, target)
                actual_size = self._member_total_size(m.type_spec, target)
                # Packed structs: no alignment padding between members
                if align > 0 and not self.is_packed:
                    total = (total + align - 1) & ~(align - 1)
                result.append((total, actual_size))
                total += actual_size
        total += bf_unit_size  # close final bitfield unit
        return result, total

    def bitfield_info(self, name, target=None):
        """For a bitfield member, return (unit_offset, unit_size, bit_start, bit_width).
        For a non-bitfield or missing member, returns None."""
        layout, _ = self._layout_members(target)
        for i, m in enumerate(self.members):
            if m.name == name:
                entry = layout[i]
                if len(entry) == 4:
                    return entry
                return None
        return None

    def size_bytes(self, target=None):
        if self.is_union:
            raw = max((self._member_total_size(m.type_spec, target) for m in self.members), default=0)
            # Round up to alignment
            a = self.alignment(target)
            if a > 1 and raw > 0:
                raw = (raw + a - 1) & ~(a - 1)
            return raw
        _, total = self._layout_members(target)
        # Align total to struct alignment
        max_align = self.alignment(target)
        if total > 0 and max_align > 1:
            total = (total + max_align - 1) & ~(max_align - 1)
        return total

    def member_offset(self, name, target=None):
        if self.is_union:
            # Union: all members at offset 0, but also check anonymous sub-members
            for m in self.members:
                if m.name == name:
                    return 0
                if m.name == "" and m.type_spec.struct_def:
                    sub_off = m.type_spec.struct_def.member_offset(name, target)
                    if sub_off is not None:
                        return sub_off
            return None
        layout, _ = self._layout_members(target)
        for i, m in enumerate(self.members):
            entry = layout[i]
            off = entry[0]  # works for both 2-tuple and 4-tuple (bitfield)
            if m.name == name:
                return off
            # Search anonymous struct/union members
            if m.name == "" and m.type_spec.struct_def:
                sub_off = m.type_spec.struct_def.member_offset(name, target)
                if sub_off is not None:
                    return off + sub_off
        return None

    def member_type(self, name):
        for m in self.members:
            if m.name == name:
                return m.type_spec
            # Search anonymous struct/union members
            if m.name == "" and m.type_spec.struct_def:
                t = m.type_spec.struct_def.member_type(name)
                if t is not None:
                    return t
        return None


@dataclass
class StructMember:
    type_spec: 'TypeSpec' = None
    name: str = ""
    bit_width: Optional[int] = None  # None = not a bitfield


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
    is_ptr_array: bool = False  # True for "array of pointers" (e.g., fptr table[3])
    is_static: bool = False
    is_extern: bool = False
    is_func_ptr: bool = False  # True for function pointer typedefs
    func_ptr_native_depth: int = 0  # pointer_depth at which this type is callable (for func ptr typedefs)
    is_func_type: bool = False  # True for function-type typedefs: typedef void fn(params); — fn* is callable
    func_ptr_is_variadic: bool = False  # True if the pointed-to function is variadic (has ...)
    func_ptr_param_count: Optional[int] = None  # number of fixed named params for variadic func ptr types
    array_sizes: Optional[List[Optional['Expr']]] = None  # None = unsized, e.g. int[]
    struct_def: Optional[StructDef] = None  # populated for struct types
    enum_def: Optional[EnumDef] = None  # populated for enum types

    def is_pointer(self):
        return self.pointer_depth > 0

    def is_array(self):
        # Pointer-to-array (ptr>0 with array_sizes) is a pointer, not an array
        if self.pointer_depth > 0:
            return False
        return self.array_sizes is not None and len(self.array_sizes) > 0

    def is_void(self):
        return self.base == "void" and self.pointer_depth == 0

    def is_struct(self):
        return self.struct_def is not None

    def is_enum(self):
        return self.enum_def is not None

    def size_bytes(self, target=None):
        """Return size in bytes for the selected target."""
        target_spec = resolve_target(target)
        if self.pointer_depth > 0:
            return target_spec.layout.pointer_size
        if self.struct_def:
            return self.struct_def.size_bytes(target)
        if self.enum_def:
            return target_spec.layout.enum_size
        sizes = {
            "_Bool": 1,
            "char": 1,
            "short": 2,
            "int": 4,
            "long": 8,
            "long long": 8,
            "__int128": 16,
            "float": 4,
            "double": 8,
            "long double": target_spec.layout.long_double_size,
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
    suffix: str = ""  # e.g. "L", "UL", "LL" — used for _Generic type matching


@dataclass
class CharLiteral(Expr):
    value: str = ""


@dataclass
class StringLiteral(Expr):
    value: str = ""
    wide: bool = False


@dataclass
class FloatLiteral(Expr):
    value: float = 0.0
    is_single: bool = False  # True for float (f suffix), False for double
    is_long_double: bool = False  # True for long double (L suffix)


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
class AlignofExpr(Expr):
    operand: Optional[Union[Expr, "TypeSpec"]] = None
    is_type: bool = False


@dataclass
class GenericAssoc:
    type_spec: Optional['TypeSpec'] = None  # None means 'default'
    expr: Optional[Expr] = None


@dataclass
class GenericSelection(Expr):
    controlling: Optional[Expr] = None
    associations: List[GenericAssoc] = field(default_factory=list)


@dataclass
class StatementExpr(Expr):
    """GNU statement expression: ({ stmt; stmt; expr; })"""
    body: Optional['Block'] = None


@dataclass
class BuiltinVaArg(Expr):
    ap: Optional[Expr] = None
    target_type: Optional['TypeSpec'] = None


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
    designator_path: Optional[List[str]] = None  # chained designators: .a.j -> ["a", "j"]
    designator_end: Optional[int] = None  # end index for range designator [start ... end]
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
class IndirectGotoStmt(Stmt):
    target: Optional["Expr"] = None


@dataclass
class LabelAddrExpr(Expr):
    label: str = ""
    func_name: str = ""


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
