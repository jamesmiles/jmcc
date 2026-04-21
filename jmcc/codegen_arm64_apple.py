"""Minimal arm64 Apple Darwin code generator for hosted JMCC tests."""

from typing import Dict, List, Optional

from .ast_nodes import (
    ArrayAccess,
    AlignofExpr,
    Assignment,
    BinaryOp,
    Block,
    BreakStmt,
    BuiltinVaArg,
    CaseStmt,
    ContinueStmt,
    CastExpr,
    DoWhileStmt,
    EnumDecl,
    Expr,
    ExprStmt,
    FloatLiteral,
    ForStmt,
    FuncCall,
    FuncDecl,
    GenericSelection,
    GlobalVarDecl,
    GotoStmt,
    Identifier,
    IfStmt,
    IndirectGotoStmt,
    IntLiteral,
    LabelAddrExpr,
    LabelStmt,
    MemberAccess,
    CommaExpr,
    CharLiteral,
    InitList,
    NullStmt,
    Program,
    ReturnStmt,
    SizeofExpr,
    StringLiteral,
    Stmt,
    StructDecl,
    SwitchStmt,
    TernaryOp,
    TypeSpec,
    TypedefDecl,
    UnaryOp,
    VarDecl,
    WhileStmt,
)
from .errors import CodeGenError


class Arm64AppleCodeGen:
    """Generate a minimal Mach-O arm64 backend for the phase-1 hosted suite."""

    ARG_REGS_32 = [f"w{i}" for i in range(8)]
    ARG_REGS_64 = [f"x{i}" for i in range(8)]

    def __init__(self, target):
        self.target = target
        self.output: List[str] = []
        self.label_count = 0
        self.locals: Dict[str, int] = {}
        self.local_types: Dict[str, object] = {}
        self.static_locals: Dict[str, str] = {}
        self.static_local_decls: Dict[str, VarDecl] = {}
        self.globals: Dict[str, GlobalVarDecl] = {}
        self.functions: Dict[str, FuncDecl] = {}
        self.string_literals: Dict[str, str] = {}
        self.stack_size = 0
        self.return_label: Optional[str] = None
        self.current_func: Optional[FuncDecl] = None
        self.func_is_variadic: bool = False
        self.break_labels: List[str] = []
        self.continue_labels: List[str] = []
        self.float_literals: Dict[tuple, str] = {}  # (bits, size) -> label
        self.vla_ptr_locals: set = set()  # locals whose slot holds a VLA base pointer

    def error(self, msg, line=0, col=0):
        raise CodeGenError(msg, line=line, col=col)

    def emit(self, line: str):
        self.output.append(line)

    def label(self, name: str):
        self.emit(f"{name}:")

    def new_label(self, prefix="L") -> str:
        self.label_count += 1
        return f"L{prefix}{self.label_count}"

    def mangle(self, name: str) -> str:
        return f"{self.target.layout.global_symbol_prefix}{name}"

    def user_label(self, name: str) -> str:
        func_name = self.current_func.name if self.current_func is not None else "global"
        return f"Luser_{func_name}_{name}"

    def user_label_for(self, func_name: str, name: str) -> str:
        return f"Luser_{func_name}_{name}"
    def static_local_label(self, name: str) -> str:
        func_name = self.current_func.name if self.current_func is not None else "global"
        return f"Lstatic_{func_name}_{name}"

    def string_label(self, value: str) -> str:
        if value not in self.string_literals:
            self.string_literals[value] = self.new_label("str")
        return self.string_literals[value]

    def escape_string(self, value: str) -> str:
        result = []
        for ch in value:
            code = ord(ch)
            if code >= 0xF700:  # PUA: lexer-encoded raw bytes >= 0x80
                code -= 0xF700
                result.append(f'\\{code:03o}')
            elif ch == '\\':
                result.append('\\\\')
            elif ch == '"':
                result.append('\\"')
            elif ch == '\n':
                result.append('\\n')
            elif ch == '\t':
                result.append('\\t')
            elif ch == '\r':
                result.append('\\r')
            elif code == 0:
                result.append('\\000')
            elif code < 0x20 or code == 0x7f:
                result.append(f'\\{code:03o}')
            else:
                result.append(ch)
        return ''.join(result)

    def slot_size(self, type_spec) -> int:
        if type_spec is not None and self.is_array_type(type_spec):
            if self._has_vla_dim(type_spec):
                return 8  # slot holds a pointer to dynamically allocated array
            return (self.total_size(type_spec) + 7) & ~7
        if type_spec is not None and type_spec.is_struct() and not type_spec.is_pointer():
            return (type_spec.struct_def.size_bytes(self.target) + 7) & ~7
        return 8

    def get_var_type(self, name: str):
        if name in self.local_types:
            return self.local_types[name]
        if name in self.globals:
            return self.globals[name].type_spec
        return None

    def is_byte_type(self, type_spec) -> bool:
        """Return True for char and _Bool types (1-byte scalar, non-pointer)."""
        return (type_spec is not None and
                type_spec.base in ("char", "_Bool") and
                not type_spec.is_pointer())

    def is_pointer_type(self, type_spec) -> bool:
        return type_spec is not None and type_spec.is_pointer()

    def is_array_type(self, type_spec) -> bool:
        if type_spec is None:
            return False
        # is_array() requires pointer_depth==0; is_ptr_array covers pointer-arrays declared with []
        # Also handle cloned types that lost is_ptr_array but still have array_sizes + pointer_depth>0
        return (type_spec.is_array() or type_spec.is_ptr_array or
                (type_spec.pointer_depth > 0 and type_spec.array_sizes is not None and len(type_spec.array_sizes) > 0))

    def element_size(self, type_spec) -> int:
        if type_spec is None:
            return 4
        if self.is_array_type(type_spec):
            elem = self.element_type(type_spec)
            if elem is not None:
                return max(1, self.total_size(elem))
            return max(1, type_spec.size_bytes(self.target))
        if type_spec.is_pointer():
            if type_spec.pointer_depth > 1:
                return self.target.layout.pointer_size
            scalar_type = type_spec.struct_def.size_bytes(self.target) if type_spec.struct_def else {
                "_Bool": 1,
                "char": 1,
                "short": 2,
                "int": 4,
                "long": 8,
                "long long": 8,
            }.get(type_spec.base, 4)
            return max(1, scalar_type)
        return max(1, type_spec.size_bytes(self.target))

    def total_size(self, type_spec) -> int:
        if type_spec is None:
            return 4
        size = type_spec.size_bytes(self.target)
        if self.is_array_type(type_spec):
            for dim in type_spec.array_sizes or []:
                if isinstance(dim, IntLiteral):
                    size *= dim.value
                elif isinstance(dim, SizeofExpr):
                    size *= self.sizeof_value(dim)
                else:
                    val = self._global_const_int(dim)
                    if val is not None:
                        size *= val
        return max(1, size)

    def _has_vla_dim(self, type_spec) -> bool:
        """Return True if type_spec contains any runtime (VLA) array dimension."""
        if not self.is_array_type(type_spec):
            return False
        for dim in (type_spec.array_sizes or []):
            if not isinstance(dim, (IntLiteral, SizeofExpr)):
                if self._global_const_int(dim) is None:
                    return True
        return False

    def _emit_runtime_size(self, type_spec):
        """Emit code that places the byte-size of type_spec into x0.
        Handles VLA dimensions; may clobber x1. Uses push/pop stack."""
        if not self.is_array_type(type_spec):
            self.emit(f"    mov x0, #{self.total_size(type_spec)}")
            return
        base_size = type_spec.size_bytes(self.target)
        static_factor = 1
        runtime_dims = []
        for dim in (type_spec.array_sizes or []):
            if isinstance(dim, IntLiteral):
                static_factor *= dim.value
            elif isinstance(dim, SizeofExpr):
                static_factor *= self.sizeof_value(dim)
            else:
                v = self._global_const_int(dim)
                if v is not None:
                    static_factor *= v
                else:
                    runtime_dims.append(dim)
        self.emit(f"    mov x0, #{base_size * static_factor}")
        for dim in runtime_dims:
            self.push_x0()
            self.gen_expr(dim)
            self.emit("    sxtw x0, w0")
            self.pop_reg("x1")
            self.emit("    mul x0, x1, x0")

    def clone_type(self, type_spec, pointer_depth=None, array_sizes=..., is_ptr_array=...):
        if type_spec is None:
            return None
        return TypeSpec(
            base=type_spec.base,
            pointer_depth=type_spec.pointer_depth if pointer_depth is None else pointer_depth,
            is_unsigned=type_spec.is_unsigned,
            array_sizes=type_spec.array_sizes if array_sizes is ... else array_sizes,
            struct_def=type_spec.struct_def,
            enum_def=type_spec.enum_def,
            is_ptr_array=type_spec.is_ptr_array if is_ptr_array is ... else is_ptr_array,
        )

    def emit_symbol_addr(self, symbol: str, reg: str = "x0"):
        self.emit(f"    adrp {reg}, {symbol}@PAGE")
        self.emit(f"    add {reg}, {reg}, {symbol}@PAGEOFF")

    def emit_extern_func_addr(self, symbol: str, reg: str = "x0"):
        """Load address of an external function via GOT on macOS arm64."""
        self.emit(f"    adrp {reg}, {symbol}@GOTPAGE")
        self.emit(f"    ldr {reg}, [{reg}, {symbol}@GOTPAGEOFF]")

    def is_wide_scalar(self, type_spec) -> bool:
        return type_spec is not None and not type_spec.is_pointer() and not self.is_array_type(type_spec) and type_spec.size_bytes(self.target) > 4

    def _is_struct_by_reg_value(self, expr) -> bool:
        """Returns True if gen_expr(expr) puts struct bytes in x0[/x1] (not an address).
        This is the case for FuncCall returning a struct ≤ 16 bytes, or compound literals."""
        if isinstance(expr, FuncCall):
            func_type = self.get_expr_type(expr)
            return (func_type is not None and func_type.struct_def is not None and
                    not func_type.is_pointer() and func_type.struct_def.size_bytes(self.target) <= 16)
        if isinstance(expr, CastExpr) and isinstance(expr.operand, InitList):
            t = expr.target_type
            return (t is not None and t.is_struct() and not t.is_pointer()
                    and t.struct_def is not None and t.struct_def.size_bytes(self.target) <= 16)
        return False

    def literal_is_wide(self, expr: IntLiteral) -> bool:
        return "L" in expr.suffix.upper() or expr.value > 0xFFFFFFFF or expr.value < -(1 << 31)

    def emit_int_constant(self, value: int, reg: str = "w0"):
        bits = 64 if reg.startswith("x") else 32
        mask = (1 << bits) - 1
        value &= mask
        chunks = [(value >> shift) & 0xFFFF for shift in range(0, bits, 16)]
        first = True
        for index, chunk in enumerate(chunks):
            if chunk == 0 and not first:
                continue
            op = "movz" if first else "movk"
            shift = index * 16
            if shift == 0:
                self.emit(f"    {op} {reg}, #{chunk}")
            else:
                self.emit(f"    {op} {reg}, #{chunk}, lsl #{shift}")
            first = False
        if first:
            self.emit(f"    movz {reg}, #0")

    def infer_unsized_array(self, type_spec, init):
        if type_spec is None or not self.is_array_type(type_spec) or not type_spec.array_sizes:
            return
        if type_spec.array_sizes[0] is not None:
            return
        if isinstance(init, InitList):
            type_spec.array_sizes[0] = IntLiteral(value=len(init.items))
        elif isinstance(init, StringLiteral) and type_spec.base == "char":
            type_spec.array_sizes[0] = IntLiteral(value=len(init.value) + 1)

    def element_type(self, type_spec):
        if type_spec is None:
            return None
        if self.is_array_type(type_spec):
            if type_spec.array_sizes and len(type_spec.array_sizes) > 1:
                return self.clone_type(type_spec, array_sizes=type_spec.array_sizes[1:])
            if type_spec.pointer_depth > 0 and not type_spec.is_array() and not type_spec.is_ptr_array:
                # Pointer-to-array T(*)[n]: element is T[n] (decrement pd, keep array_sizes)
                return self.clone_type(type_spec, pointer_depth=type_spec.pointer_depth - 1)
            # Strip last array dimension; clear is_ptr_array since result is a plain pointer
            return self.clone_type(type_spec, array_sizes=None, is_ptr_array=False)
        if type_spec.is_pointer():
            return self.clone_type(type_spec, pointer_depth=max(type_spec.pointer_depth - 1, 0), array_sizes=None)
        return None

    def get_expr_type(self, expr: Expr):
        if isinstance(expr, Identifier):
            if expr.name in ("__func__", "__FUNCTION__", "__PRETTY_FUNCTION__"):
                return TypeSpec(base="char", pointer_depth=1)
            var_type = self.get_var_type(expr.name)
            if var_type is not None:
                return var_type
            if expr.name in self.functions:
                return TypeSpec(base="void", pointer_depth=1)
            return None
        if isinstance(expr, IntLiteral):
            suffix_up = (expr.suffix or "").upper()
            is_u = "U" in suffix_up
            if self.literal_is_wide(expr):
                ts = TypeSpec(base="long long", is_unsigned=is_u)
                return ts
            return TypeSpec(base="int", is_unsigned=is_u)
        if isinstance(expr, FloatLiteral):
            return TypeSpec(base="float" if expr.is_single else "double")
        if isinstance(expr, StringLiteral):
            return TypeSpec(base="char", pointer_depth=1)
        if isinstance(expr, Assignment):
            return self.get_expr_type(expr.target)
        if isinstance(expr, CastExpr):
            return expr.target_type
        if isinstance(expr, CommaExpr):
            return self.get_expr_type(expr.exprs[-1]) if expr.exprs else TypeSpec(base="int")
        if isinstance(expr, ArrayAccess):
            array_type = self.get_expr_type(expr.array)
            if array_type is None:
                return None
            return self.element_type(array_type)
        if isinstance(expr, MemberAccess):
            obj_type = self.get_expr_type(expr.obj)
            if obj_type is None:
                return None
            struct_type = self.clone_type(obj_type, pointer_depth=obj_type.pointer_depth - 1) if expr.arrow else obj_type
            if struct_type is None or struct_type.struct_def is None:
                return None
            return struct_type.struct_def.member_type(expr.member)
        if isinstance(expr, UnaryOp):
            operand_type = self.get_expr_type(expr.operand)
            if expr.op == "&" and operand_type is not None:
                return self.clone_type(operand_type, pointer_depth=operand_type.pointer_depth + 1)
            if expr.op == "*" and operand_type is not None:
                new_pd = max(operand_type.pointer_depth - 1, 0)
                # T(*)[n]: dereferencing pointer-to-array gives T[n], keep array_sizes
                if operand_type.pointer_depth > 0 and not operand_type.is_ptr_array and operand_type.array_sizes:
                    return self.clone_type(operand_type, pointer_depth=new_pd)
                return self.clone_type(operand_type, pointer_depth=new_pd, array_sizes=None)
            if expr.op in {"-", "~", "++", "--"} and operand_type is not None:
                return operand_type
            return TypeSpec(base="int")
        if isinstance(expr, BinaryOp):
            left_type = self.get_expr_type(expr.left)
            right_type = self.get_expr_type(expr.right)
            if expr.op in {"==", "!=", "<", "<=", ">", ">=", "&&", "||"}:
                return TypeSpec(base="int")
            if expr.op in {"+", "-"}:
                if left_type is not None and left_type.is_pointer():
                    return left_type
                if right_type is not None and right_type.is_pointer():
                    return right_type
            if self.is_fp_type(left_type):
                return left_type
            if self.is_fp_type(right_type):
                return right_type
            return left_type or right_type or TypeSpec(base="int")
        if isinstance(expr, SizeofExpr):
            return TypeSpec(base="int")
        if isinstance(expr, AlignofExpr):
            return TypeSpec(base="int")
        if isinstance(expr, GenericSelection):
            selected = self._resolve_generic(expr)
            if selected is not None:
                return self.get_expr_type(selected)
            return TypeSpec(base="int")
        if isinstance(expr, TernaryOp):
            # The type of a ternary is the type of its branches (use true branch)
            t = self.get_expr_type(expr.true_expr)
            if t is not None:
                return t
            return self.get_expr_type(expr.false_expr)
        if isinstance(expr, BuiltinVaArg):
            return expr.target_type
        if isinstance(expr, FuncCall):
            if isinstance(expr.name, Identifier):
                func_decl = self.functions.get(expr.name.name)
                if func_decl is not None and func_decl.return_type is not None:
                    return func_decl.return_type
            return TypeSpec(base="int")
        return TypeSpec(base="int")

    def generate(self, program: Program) -> str:
        self.globals = {}
        for decl in program.declarations:
            if isinstance(decl, GlobalVarDecl):
                self.infer_unsized_array(decl.type_spec, decl.init)
                existing = self.globals.get(decl.name)
                if existing is None or (existing.type_spec.is_extern and not decl.type_spec.is_extern):
                    self.globals[decl.name] = decl
        self.functions = {
            decl.name: decl
            for decl in program.declarations
            if isinstance(decl, FuncDecl)
        }

        self.emit("    .text")
        for decl in program.declarations:
            if isinstance(decl, FuncDecl) and decl.body is not None:
                self.gen_function(decl)
            elif not isinstance(decl, (FuncDecl, GlobalVarDecl, EnumDecl, StructDecl, TypedefDecl)):
                self.error(
                    f"arm64-apple-darwin backend does not yet support top-level declaration type {type(decl).__name__}",
                    getattr(decl, "line", 0),
                    getattr(decl, "col", 0),
                )

        for decl in self.globals.values():
            if decl.type_spec.is_extern:
                continue
            self.emit_global_decl(
                self.mangle(decl.name),
                decl.type_spec,
                decl.init,
                decl.line,
                decl.col,
                exported=not decl.type_spec.is_static,
            )

        for label, decl in self.static_local_decls.items():
            self.emit_global_decl(label, decl.type_spec, decl.init, decl.line, decl.col, exported=False)

        if self.string_literals:
            self.emit("")
            self.emit("    .data")
            for value, label in self.string_literals.items():
                self.emit("    .p2align 2")
                self.label(label)
                self.emit(f'    .asciz "{self.escape_string(value)}"')

        if self.float_literals:
            self.emit("")
            # Separate 4-byte and 8-byte float literals into their proper sections
            float4 = [(k, v) for k, v in self.float_literals.items() if k[1] == 4]
            float8 = [(k, v) for k, v in self.float_literals.items() if k[1] == 8]
            if float8:
                self.emit("    .section __TEXT,__literal8,8byte_literals")
                for (bits, size), label in float8:
                    self.emit("    .p2align 3")
                    self.label(label)
                    self.emit(f"    .quad {bits}")
            if float4:
                self.emit("    .section __TEXT,__literal4,4byte_literals")
                for (bits, size), label in float4:
                    self.emit("    .p2align 2")
                    self.label(label)
                    self.emit(f"    .long {bits}")

        return "\n".join(self.output) + "\n"

    def emit_global_decl(self, label: str, type_spec, init, line: int, col: int, exported: bool = True):
        self.emit("")
        self.emit("    .data")
        if type_spec is not None:
            if type_spec.is_struct() and not type_spec.is_pointer() and type_spec.struct_def is not None:
                align = type_spec.struct_def.alignment(self.target)
            else:
                align = min(type_spec.size_bytes(self.target), self.target.layout.max_scalar_align)
            if align <= 1:
                p2 = 0
            elif align <= 2:
                p2 = 1
            elif align <= 4:
                p2 = 2
            else:
                p2 = 3
        else:
            p2 = 2
        self.emit(f"    .p2align {p2}")
        if exported:
            self.emit(f"    .globl {label}")
        self.label(label)

        if init is None:
            self.emit(f"    .zero {self.total_size(type_spec)}")
            return

        if isinstance(init, IntLiteral):
            size = type_spec.size_bytes(self.target)
            if size <= 1:
                self.emit(f"    .byte {init.value & 0xff}")
            elif size <= 2:
                self.emit(f"    .short {init.value & 0xffff}")
            elif size <= 4:
                self.emit(f"    .long {init.value & 0xffffffff}")
            else:
                self.emit(f"    .quad {init.value}")
            return

        if isinstance(init, StringLiteral) and type_spec is not None and type_spec.is_array() and type_spec.base == "char":
            self.emit(f'    .asciz "{self.escape_string(init.value)}"')
            return

        if isinstance(init, StringLiteral) and type_spec is not None and type_spec.is_pointer():
            label = self.string_label(init.value)
            self.emit(f"    .quad {label}")
            return

        if isinstance(init, InitList) and type_spec is not None and self.is_array_type(type_spec):
            self.emit_global_array_init(type_spec, init, line, col)
            return

        if isinstance(init, InitList) and type_spec is not None and type_spec.is_struct() and not type_spec.is_pointer():
            self.emit_global_value(type_spec, init, line, col)
            return

        self.emit_global_value(type_spec, init, line, col)

    def _array_dim_count(self, type_spec) -> int:
        """Return total number of scalar elements in an array type."""
        if not self.is_array_type(type_spec):
            return 1
        dims = type_spec.array_sizes or []
        count = 1
        for d in dims:
            if isinstance(d, IntLiteral):
                count *= d.value
            else:
                v = self._global_const_int(d)
                if v is not None:
                    count *= v
        return count

    def emit_global_array_init(self, type_spec, init: InitList, line: int, col: int):
        """Emit global array data, supporting both braced and flat initializers."""
        elem_type = self.element_type(type_spec)
        if type_spec.array_sizes and type_spec.array_sizes[0] is not None:
            dim = type_spec.array_sizes[0]
            if isinstance(dim, IntLiteral):
                count = dim.value
            else:
                count = self._global_const_int(dim)
                if count is None:
                    count = len(init.items)
        else:
            count = len(init.items)

        # Detect flat init: 2D+ array but items are scalars, not sub-InitLists.
        # String literals are row-level initializers for char sub-arrays — exclude them.
        is_nested_array = self.is_array_type(elem_type)
        has_flat_items = (is_nested_array and init.items
                          and not isinstance(init.items[0].value, (InitList, StringLiteral)))

        if has_flat_items:
            # Flat initializer: consume items sequentially across all sub-arrays
            flat_items = [item.value for item in init.items]
            flat_idx = 0
            for _ in range(count):
                sub_count = self._array_dim_count(elem_type)
                sub_items = flat_items[flat_idx:flat_idx + sub_count]
                flat_idx += sub_count
                from jmcc.ast_nodes import InitItem
                dummy = InitList(items=[InitItem(value=v) for v in sub_items], line=line, col=col)
                self.emit_global_array_init(elem_type, dummy, line, col)
            return

        for index in range(count):
            item = init.items[index].value if index < len(init.items) else None
            self.emit_global_value(elem_type, item, line, col)

    def emit_global_struct_init(self, type_spec, value: 'InitList', line: int, col: int):
        struct_def = type_spec.struct_def
        total = struct_def.size_bytes(self.target)

        # For unions: emit only the first (or only initialized) member, then zero-pad to union size.
        if struct_def.is_union:
            first_val = value.items[0].value if value.items else None
            first_member = next((m for m in struct_def.members if m.name != ""), None)
            if first_member is not None and first_val is not None:
                self.emit_global_value(first_member.type_spec, first_val, line, col)
                emitted = self.total_size(first_member.type_spec)
            else:
                emitted = 0
            if total > emitted:
                self.emit(f"    .zero {total - emitted}")
            return

        current_offset = 0
        members = [m for m in struct_def.members if m.name != ""]
        for i, member in enumerate(members):
            member_off = struct_def.member_offset(member.name) or 0
            if member_off > current_offset:
                self.emit(f"    .zero {member_off - current_offset}")
                current_offset = member_off
            member_type = member.type_spec
            member_value = value.items[i].value if i < len(value.items) else None
            if self.is_array_type(member_type):
                size = self.total_size(member_type)
                if member_value is None:
                    self.emit(f"    .zero {size}")
                elif member_type.base == "char" and isinstance(member_value, StringLiteral):
                    raw = member_value.value.encode("utf-8") + b"\0"
                    raw = raw[:size] + b"\0" * max(0, size - len(raw))
                    for byte in raw:
                        self.emit(f"    .byte {byte}")
                else:
                    self.emit_global_array_init(member_type, member_value, line, col)
                current_offset += size
            elif member_type.is_pointer():
                ptr_size = self.target.layout.pointer_size
                if member_value is None:
                    self.emit(f"    .quad 0")
                elif isinstance(member_value, StringLiteral):
                    label = self.string_label(member_value.value)
                    self.emit(f"    .quad {label}")
                elif isinstance(member_value, Identifier) and member_value.name in self.functions:
                    self.emit(f"    .quad {self.mangle(member_value.name)}")
                elif isinstance(member_value, (IntLiteral, CharLiteral)):
                    intval = member_value.value if isinstance(member_value, IntLiteral) else ord(member_value.value)
                    self.emit(f"    .quad {intval}")
                else:
                    sym = self._global_addr_str(member_value)
                    if sym is not None:
                        self.emit(f"    .quad {sym}")
                    else:
                        intval = self._global_const_int(member_value)
                        if intval is not None:
                            self.emit(f"    .quad {intval}")
                        else:
                            self.error("arm64-apple-darwin backend does not yet support this struct global initializer", line, col)
                current_offset += ptr_size
            elif isinstance(member_value, (IntLiteral, CharLiteral)):
                size = member_type.size_bytes(self.target)
                intval = member_value.value if isinstance(member_value, IntLiteral) else ord(member_value.value)
                if size <= 1:
                    self.emit(f"    .byte {intval & 0xff}")
                elif size <= 2:
                    self.emit(f"    .short {intval & 0xffff}")
                elif size <= 4:
                    self.emit(f"    .long {intval & 0xffffffff}")
                else:
                    self.emit(f"    .quad {intval}")
                current_offset += size
            elif member_value is None:
                size = member_type.size_bytes(self.target)
                self.emit(f"    .zero {size}")
                current_offset += size
            elif member_type.is_struct() and not member_type.is_pointer() and isinstance(member_value, InitList):
                self.emit_global_struct_init(member_type, member_value, line, col)
                current_offset += member_type.struct_def.size_bytes(self.target)
            else:
                size = member_type.size_bytes(self.target)
                # Try constant integer expression (e.g. -1, cast expressions)
                intval = self._global_const_int(member_value)
                if intval is not None:
                    if size <= 1:
                        self.emit(f"    .byte {intval & 0xff}")
                    elif size <= 2:
                        self.emit(f"    .short {intval & 0xffff}")
                    elif size <= 4:
                        self.emit(f"    .long {intval & 0xffffffff}")
                    else:
                        self.emit(f"    .quad {intval}")
                    current_offset += size
                elif isinstance(member_value, InitList):
                    # Union initializer — use only the first element
                    if member_value.items:
                        nested_val = member_value.items[0].value
                        from jmcc.ast_nodes import InitItem
                        dummy_list = InitList(items=[InitItem(value=nested_val)], line=line, col=col)
                        # emit the first field's worth of bytes
                        nested_intval = self._global_const_int(nested_val)
                        nested_sym = self._global_addr_str(nested_val)
                        if nested_sym is not None:
                            self.emit(f"    .quad {nested_sym}")
                        elif nested_intval is not None:
                            if size <= 1:
                                self.emit(f"    .byte {nested_intval & 0xff}")
                            elif size <= 2:
                                self.emit(f"    .short {nested_intval & 0xffff}")
                            elif size <= 4:
                                self.emit(f"    .long {nested_intval & 0xffffffff}")
                            else:
                                self.emit(f"    .quad {nested_intval}")
                        else:
                            self.emit(f"    .zero {size}")
                    else:
                        self.emit(f"    .zero {size}")
                    current_offset += size
                else:
                    self.error("arm64-apple-darwin backend does not yet support this struct global initializer", line, col)
        total = struct_def.size_bytes(self.target)
        if total > current_offset:
            self.emit(f"    .zero {total - current_offset}")

    def emit_global_value(self, type_spec, value, line: int, col: int):
        if self.is_array_type(type_spec):
            if value is None:
                self.emit(f"    .zero {self.total_size(type_spec)}")
                return
            if type_spec.base == "char" and isinstance(value, StringLiteral):
                raw = value.value.encode("utf-8") + b"\0"
                limit = self.total_size(type_spec)
                raw = raw[:limit] + b"\0" * max(0, limit - len(raw))
                for byte in raw:
                    self.emit(f"    .byte {byte}")
                return
            if isinstance(value, InitList):
                self.emit_global_array_init(type_spec, value, line, col)
                return
        if type_spec is not None and type_spec.is_struct() and not type_spec.is_pointer():
            if not isinstance(value, InitList):
                self.error("arm64-apple-darwin backend expects struct init list here", line, col)
            self.emit_global_struct_init(type_spec, value, line, col)
            return
        if value is None:
            self.emit(f"    .zero {self.total_size(type_spec)}")
            return
        if isinstance(value, StringLiteral) and type_spec is not None and type_spec.is_pointer():
            label = self.string_label(value.value)
            self.emit(f"    .quad {label}")
            return
        if isinstance(value, Identifier) and value.name in self.functions:
            self.emit(f"    .quad {self.mangle(value.name)}")
            return
        addr = self._global_addr_str(value)
        if addr is not None:
            self.emit(f"    .quad {addr}")
            return
        if isinstance(value, LabelAddrExpr):
            fname = value.func_name or (self.current_func.name if self.current_func else "")
            lbl = self.user_label_for(fname, value.label)
            self.emit(f"    .quad {lbl}")
            return
        if isinstance(value, (IntLiteral, CharLiteral)):
            intval = value.value if isinstance(value, IntLiteral) else ord(value.value)
            size = type_spec.size_bytes(self.target)
            if size <= 1:
                self.emit(f"    .byte {intval & 0xff}")
            elif size <= 2:
                self.emit(f"    .short {intval & 0xffff}")
            elif size <= 4:
                self.emit(f"    .long {intval & 0xffffffff}")
            else:
                self.emit(f"    .quad {intval}")
            return
        if isinstance(value, FloatLiteral):
            import struct
            if value.is_single or (type_spec is not None and type_spec.base == "float"):
                bits = struct.unpack('<I', struct.pack('<f', value.value))[0]
                self.emit(f"    .long {bits}")
            else:
                bits = struct.unpack('<Q', struct.pack('<d', value.value))[0]
                self.emit(f"    .quad {bits}")
            return
        # Try constant integer expression (e.g. -1, (type)expr)
        intval = self._global_const_int(value)
        if intval is not None and type_spec is not None:
            size = type_spec.size_bytes(self.target)
            if size <= 1:
                self.emit(f"    .byte {intval & 0xff}")
            elif size <= 2:
                self.emit(f"    .short {intval & 0xffff}")
            elif size <= 4:
                self.emit(f"    .long {intval & 0xffffffff}")
            else:
                self.emit(f"    .quad {intval}")
            return
        self.error("arm64-apple-darwin backend does not yet support this global initializer value", line, col)

    def alloc_slot(self, name: str, type_spec=None):
        if name in self.locals:
            return
        self.stack_size += self.slot_size(type_spec)
        self.locals[name] = self.stack_size
        self.local_types[name] = type_spec
        if type_spec is not None and self.is_array_type(type_spec) and self._has_vla_dim(type_spec):
            self.vla_ptr_locals.add(name)

    def collect_locals_stmt(self, stmt: Stmt):
        if isinstance(stmt, Block):
            for child in stmt.stmts:
                self.collect_locals_stmt(child)
        elif isinstance(stmt, VarDecl):
            self.infer_unsized_array(stmt.type_spec, stmt.init)
            if stmt.type_spec is not None and stmt.type_spec.is_extern and self.current_func is not None:
                if stmt.name not in self.globals:
                    self.globals[stmt.name] = GlobalVarDecl(type_spec=stmt.type_spec, name=stmt.name, init=None)
                self.local_types[stmt.name] = stmt.type_spec
                return
            if stmt.type_spec is not None and stmt.type_spec.is_static:
                self.static_locals[stmt.name] = self.static_local_label(stmt.name)
                self.static_local_decls[self.static_locals[stmt.name]] = stmt
                self.local_types[stmt.name] = stmt.type_spec
            else:
                self.alloc_slot(stmt.name, stmt.type_spec)
        elif isinstance(stmt, IfStmt):
            self.collect_locals_stmt(stmt.then_body)
            if stmt.else_body is not None:
                self.collect_locals_stmt(stmt.else_body)
        elif isinstance(stmt, WhileStmt):
            self.collect_locals_stmt(stmt.body)
        elif isinstance(stmt, DoWhileStmt):
            self.collect_locals_stmt(stmt.body)
        elif isinstance(stmt, ForStmt):
            if stmt.init is not None:
                self.collect_locals_stmt(stmt.init)
            self.collect_locals_stmt(stmt.body)
        elif isinstance(stmt, SwitchStmt):
            self.collect_locals_stmt(stmt.body)
        elif isinstance(stmt, CaseStmt):
            if stmt.stmt is not None:
                self.collect_locals_stmt(stmt.stmt)
        elif isinstance(stmt, LabelStmt):
            if stmt.stmt is not None:
                self.collect_locals_stmt(stmt.stmt)
        elif isinstance(stmt, (ReturnStmt, ExprStmt, BreakStmt, ContinueStmt, GotoStmt, IndirectGotoStmt, NullStmt)):
            return
        else:
            self.error(
                f"arm64-apple-darwin backend does not yet support statement type {type(stmt).__name__}",
                stmt.line,
                stmt.col,
            )

    def prepare_function(self, func: FuncDecl):
        self.locals = {}
        self.local_types = {}
        self.static_locals = {}
        self.vla_ptr_locals = set()
        self.stack_size = 0
        for param in func.params:
            self.alloc_slot(param.name, param.type_spec)
        self.collect_locals_stmt(func.body)
        self.stack_size = (self.stack_size + 15) & ~15

    def load_var(self, name: str, line=0, col=0):
        type_spec = self.get_var_type(name)
        if name in self.locals:
            if type_spec is not None and (type_spec.is_array() or type_spec.is_ptr_array):
                if name in self.vla_ptr_locals:
                    self.emit_local_load("ldur", "x0", self.locals[name])
                else:
                    self.emit(f"    sub x0, x29, #{self.locals[name]}")
            elif type_spec is not None and type_spec.is_struct() and not type_spec.is_pointer():
                self.emit(f"    sub x0, x29, #{self.locals[name]}")
            elif self.is_fp_type(type_spec):
                if type_spec.base == "float":
                    self.emit_local_load("ldur", "s0", self.locals[name])
                    self.emit("    fcvt d0, s0")
                else:
                    self.emit_local_load("ldur", "d0", self.locals[name])
            elif self.is_pointer_type(type_spec):
                self.emit_local_load("ldur", "x0", self.locals[name])
            elif self.is_byte_type(type_spec):
                self.emit_local_load("ldurb" if (type_spec.is_unsigned or type_spec.base == "_Bool") else "ldursb", "w0", self.locals[name])
            elif type_spec is not None and type_spec.base == "short":
                self.emit_local_load("ldurh" if type_spec.is_unsigned else "ldursh", "w0", self.locals[name])
            elif self.is_wide_scalar(type_spec):
                self.emit_local_load("ldur", "x0", self.locals[name])
            else:
                self.emit_local_load("ldur", "w0", self.locals[name])
            return
        if name in self.static_locals:
            label = self.static_locals[name]
            self.emit_symbol_addr(label, "x9")
            if type_spec is not None and (type_spec.is_array() or type_spec.is_ptr_array) or (type_spec is not None and type_spec.is_struct() and not type_spec.is_pointer()):
                self.emit("    mov x0, x9")
            elif self.is_fp_type(type_spec):
                if type_spec.base == "float":
                    self.emit("    ldr s0, [x9]")
                    self.emit("    fcvt d0, s0")
                else:
                    self.emit("    ldr d0, [x9]")
            elif self.is_pointer_type(type_spec):
                self.emit("    ldr x0, [x9]")
            elif type_spec is not None and type_spec.base == "short":
                self.emit("    ldrh w0, [x9]" if type_spec.is_unsigned else "    ldrsh w0, [x9]")
            elif self.is_wide_scalar(type_spec):
                self.emit("    ldr x0, [x9]")
            elif self.is_byte_type(type_spec):
                self.emit("    ldrb w0, [x9]" if type_spec.is_unsigned else "    ldrsb w0, [x9]")
            else:
                self.emit("    ldr w0, [x9]")
            return
        if name in self.globals:
            mangled = self.mangle(name)
            g = self.globals[name]
            is_extern_global = g.type_spec is not None and g.type_spec.is_extern
            if is_extern_global:
                self.emit(f"    adrp x9, {mangled}@GOTPAGE")
                self.emit(f"    ldr x9, [x9, {mangled}@GOTPAGEOFF]")
            else:
                self.emit_symbol_addr(mangled, "x9")
            if type_spec is not None and (type_spec.is_array() or type_spec.is_ptr_array) or (type_spec is not None and type_spec.is_struct() and not type_spec.is_pointer()):
                self.emit("    mov x0, x9")
            elif self.is_fp_type(type_spec):
                if type_spec.base == "float":
                    self.emit("    ldr s0, [x9]")
                    self.emit("    fcvt d0, s0")
                else:
                    self.emit("    ldr d0, [x9]")
            elif self.is_pointer_type(type_spec):
                self.emit("    ldr x0, [x9]")
            elif type_spec is not None and type_spec.base == "short":
                self.emit("    ldrh w0, [x9]" if type_spec.is_unsigned else "    ldrsh w0, [x9]")
            elif self.is_wide_scalar(type_spec):
                self.emit("    ldr x0, [x9]")
            elif self.is_byte_type(type_spec):
                self.emit("    ldrb w0, [x9]" if type_spec.is_unsigned else "    ldrsb w0, [x9]")
            else:
                self.emit("    ldr w0, [x9]")
            return
        if name in self.functions:
            func_decl = self.functions.get(name)
            if func_decl is not None and func_decl.body is not None:
                self.emit_symbol_addr(self.mangle(name))
            else:
                self.emit_extern_func_addr(self.mangle(name))
            return
        self.error(f"undefined variable '{name}'", line, col)

    def store_var(self, name: str, src_reg=None, line=0, col=0):
        type_spec = self.get_var_type(name)
        is_fp = self.is_fp_type(type_spec)
        if src_reg is None:
            if is_fp:
                src_reg = "s0" if type_spec is not None and type_spec.base == "float" else "d0"
            elif self.is_pointer_type(type_spec) or self.is_wide_scalar(type_spec):
                src_reg = "x0"
            else:
                src_reg = "w0"
        if is_fp and type_spec is not None and type_spec.base == "float":
            self.emit("    fcvt s0, d0")
            src_reg = "s0"
        if type_spec is not None and type_spec.base == "_Bool" and not is_fp:
            # _Bool stores 0 or 1 — normalize the value before storing
            self.emit("    cmp w0, #0")
            self.emit("    cset w0, ne")
            src_reg = "w0"
        if name in self.locals:
            if is_fp:
                self.emit_local_store("stur", src_reg, self.locals[name])
            elif self.is_byte_type(type_spec):
                self.emit_local_store("sturb", src_reg, self.locals[name])
            elif type_spec is not None and type_spec.base == "short" and not type_spec.is_pointer():
                self.emit_local_store("sturh", src_reg, self.locals[name])
            else:
                self.emit_local_store("stur", src_reg, self.locals[name])
            return
        if name in self.static_locals:
            label = self.static_locals[name]
            self.emit_symbol_addr(label, "x9")
            if is_fp:
                self.emit(f"    str {src_reg}, [x9]")
            elif self.is_byte_type(type_spec):
                self.emit(f"    strb {src_reg}, [x9]")
            elif type_spec is not None and type_spec.base == "short" and not type_spec.is_pointer():
                self.emit(f"    strh {src_reg}, [x9]")
            else:
                self.emit(f"    str {src_reg}, [x9]")
            return
        if name in self.globals:
            mangled = self.mangle(name)
            g = self.globals[name]
            is_extern_global = g.type_spec is not None and g.type_spec.is_extern
            if is_extern_global:
                self.emit(f"    adrp x9, {mangled}@GOTPAGE")
                self.emit(f"    ldr x9, [x9, {mangled}@GOTPAGEOFF]")
            else:
                self.emit_symbol_addr(mangled, "x9")
            if is_fp:
                self.emit(f"    str {src_reg}, [x9]")
            elif self.is_byte_type(type_spec):
                self.emit(f"    strb {src_reg}, [x9]")
            elif type_spec is not None and type_spec.base == "short" and not type_spec.is_pointer():
                self.emit(f"    strh {src_reg}, [x9]")
            else:
                self.emit(f"    str {src_reg}, [x9]")
            return
        self.error(f"undefined variable '{name}'", line, col)

    def push_x0(self):
        self.emit("    str x0, [sp, #-16]!")

    def pop_reg(self, reg: str):
        self.emit(f"    ldr {reg}, [sp], #16")

    def push_d0(self):
        self.emit("    str d0, [sp, #-16]!")

    def pop_d0(self, reg: str = "d1"):
        self.emit(f"    ldr {reg}, [sp], #16")

    def emit_local_load(self, instr: str, reg: str, offset: int):
        """Emit load from [x29, #-offset], using x9 as scratch for offsets > 255."""
        if offset <= 255:
            self.emit(f"    {instr} {reg}, [x29, #-{offset}]")
        else:
            self.emit(f"    sub x9, x29, #{offset}")
            scaled = instr.replace("ldur", "ldr")
            self.emit(f"    {scaled} {reg}, [x9]")

    def emit_local_store(self, instr: str, reg: str, offset: int):
        """Emit store to [x29, #-offset], using x9 as scratch for offsets > 255."""
        if offset <= 255:
            self.emit(f"    {instr} {reg}, [x29, #-{offset}]")
        else:
            self.emit(f"    sub x9, x29, #{offset}")
            scaled = instr.replace("stur", "str")
            self.emit(f"    {scaled} {reg}, [x9]")

    _FP_BASES = frozenset({"float", "double", "long double"})

    def _global_const_int(self, value) -> Optional[int]:
        """Try to evaluate value as a compile-time constant integer. Returns None if not possible."""
        if isinstance(value, IntLiteral):
            return value.value
        if isinstance(value, CharLiteral):
            return ord(value.value)
        if isinstance(value, CastExpr):
            return self._global_const_int(value.operand)
        if isinstance(value, UnaryOp) and value.op == "-":
            inner = self._global_const_int(value.operand)
            return -inner if inner is not None else None
        if isinstance(value, BinaryOp):
            l = self._global_const_int(value.left)
            r = self._global_const_int(value.right)
            if l is not None and r is not None:
                op = value.op
                if op == "+": return l + r
                if op == "-": return l - r
                if op == "*": return l * r
                if op == "/" and r != 0: return l // r
                if op == "%" and r != 0: return l % r
                if op == "<<": return l << r
                if op == ">>": return l >> r
                if op == "&": return l & r
                if op == "|": return l | r
                if op == "^": return l ^ r
        return None

    def _global_addr_str(self, value) -> Optional[str]:
        """Try to resolve value to a static address string (e.g. '_sym' or '_sym+8').
        Returns None if not a static address expression."""
        while isinstance(value, CastExpr):
            value = value.operand
        if isinstance(value, UnaryOp) and value.op == "&":
            operand = value.operand
            if isinstance(operand, Identifier):
                name = operand.name
                if name in self.globals:
                    return self.mangle(name)
                if name in self.static_locals:
                    return self.static_locals[name]
            elif isinstance(operand, ArrayAccess):
                arr = operand.array
                idx = self._global_const_int(operand.index)
                if idx is not None:
                    if isinstance(arr, Identifier) and arr.name in self.globals:
                        arr_type = self.globals[arr.name].type_spec
                        elem_sz = self.element_size(arr_type)
                        off = idx * elem_sz
                        mangled = self.mangle(arr.name)
                        return mangled if off == 0 else f"{mangled}+{off}"
                    elif isinstance(arr, MemberAccess) and isinstance(arr.obj, Identifier) and arr.obj.name in self.globals:
                        # &global.member[idx]
                        base_decl = self.globals[arr.obj.name]
                        struct_def = base_decl.type_spec.struct_def
                        if struct_def is not None:
                            member_off = struct_def.member_offset(arr.member) or 0
                            member_ts = struct_def.member_type(arr.member)
                            elem_sz = self.element_size(member_ts) if member_ts is not None else 1
                            total_off = member_off + idx * elem_sz
                            mangled = self.mangle(arr.obj.name)
                            return mangled if total_off == 0 else f"{mangled}+{total_off}"
        # Bare array decay: table[0] -> &table[0] (pointer to element)
        if isinstance(value, ArrayAccess) and isinstance(value.array, Identifier):
            arr_name = value.array.name
            idx = self._global_const_int(value.index)
            if idx is not None and arr_name in self.globals:
                arr_type = self.globals[arr_name].type_spec
                elem_sz = self.element_size(arr_type)
                off = idx * elem_sz
                mangled = self.mangle(arr_name)
                return mangled if off == 0 else f"{mangled}+{off}"
        if isinstance(value, Identifier):
            if value.name in self.functions:
                return self.mangle(value.name)
            if value.name in self.globals:
                return self.mangle(value.name)
            if value.name in self.static_locals:
                return self.static_locals[value.name]
        if isinstance(value, InitList) and value.items:
            return self._global_addr_str(value.items[0].value)
        return None

    def is_fp_type(self, ts) -> bool:
        return ts is not None and ts.base in self._FP_BASES and not ts.is_pointer() and not self.is_array_type(ts)

    def is_fp_expr(self, expr) -> bool:
        return self.is_fp_type(self.get_expr_type(expr))

    def gen_condition(self, expr):
        """Evaluate expr, leaving an integer boolean result in w0."""
        self.gen_expr(expr)
        if self.is_fp_expr(expr):
            self.emit("    fcmp d0, #0.0")
            self.emit("    cset w0, ne")
            return
        expr_type = self.get_expr_type(expr)
        if self.is_pointer_type(expr_type) or self.is_wide_scalar(expr_type):
            # Normalize 64-bit value to 0/1 so callers' cbz/cbnz on w0 work
            self.emit("    cmp x0, #0")
            self.emit("    cset w0, ne")

    def float_literal_label(self, bits: int, size: int) -> str:
        key = (bits, size)
        if key not in self.float_literals:
            self.float_literals[key] = self.new_label("fpconst")
        return self.float_literals[key]

    def gen_float_literal(self, expr):
        import struct
        if expr.is_single:
            bits = struct.unpack('<I', struct.pack('<f', expr.value))[0]
            label = self.float_literal_label(bits, 4)
            self.emit(f"    adrp x9, {label}@PAGE")
            self.emit(f"    ldr s0, [x9, {label}@PAGEOFF]")
            self.emit("    fcvt d0, s0")
        else:
            bits = struct.unpack('<Q', struct.pack('<d', expr.value))[0]
            label = self.float_literal_label(bits, 8)
            self.emit(f"    adrp x9, {label}@PAGE")
            self.emit(f"    ldr d0, [x9, {label}@PAGEOFF]")

    def gen_function(self, func: FuncDecl):
        if len(func.params) > len(self.ARG_REGS_32):
            self.error("more than 8 integer parameters are not yet supported on arm64-apple-darwin", func.line, func.col)

        self.current_func = func
        self.func_is_variadic = func.is_variadic
        self.prepare_function(func)
        self.return_label = self.new_label(f"{func.name}_return")

        self.emit("")
        self.emit("    .p2align 2")
        if func.return_type is None or not func.return_type.is_static:
            self.emit(f"    .globl {self.mangle(func.name)}")
        self.label(self.mangle(func.name))
        self.emit("    stp x29, x30, [sp, #-16]!")
        self.emit("    mov x29, sp")
        if self.stack_size:
            self.emit(f"    sub sp, sp, #{self.stack_size}")

        int_idx = 0
        fp_idx = 0
        for param in func.params:
            if self.is_fp_type(param.type_spec):
                self.store_var(param.name, src_reg=f"d{fp_idx}", line=func.line, col=func.col)
                fp_idx += 1
            elif (param.type_spec is not None and param.type_spec.is_struct()
                  and not param.type_spec.is_pointer()):
                struct_size = param.type_spec.struct_def.size_bytes(self.target)
                dest_offset = self.locals.get(param.name, 0)
                if struct_size <= 4:
                    self.emit_local_store("stur", f"w{int_idx}", dest_offset)
                elif struct_size <= 8:
                    self.emit_local_store("stur", f"x{int_idx}", dest_offset)
                elif struct_size <= 16:
                    self.emit_local_store("stur", f"x{int_idx}", dest_offset)
                    rem = struct_size - 8
                    self.emit_local_store(
                        "stur",
                        f"w{int_idx + 1}" if rem <= 4 else f"x{int_idx + 1}",
                        dest_offset - 8,
                    )
                    int_idx += 1  # consumed an extra register
                else:
                    # > 16 bytes: hidden pointer in x{int_idx} — store as pointer for now
                    self.emit_local_store("stur", f"x{int_idx}", dest_offset)
                int_idx += 1
            else:
                arg_reg = self.ARG_REGS_64[int_idx] if (self.is_pointer_type(param.type_spec) or self.is_wide_scalar(param.type_spec)) else self.ARG_REGS_32[int_idx]
                self.store_var(param.name, src_reg=arg_reg, line=func.line, col=func.col)
                int_idx += 1

        self.gen_block(func.body)
        self.emit("    mov w0, #0")
        self.label(self.return_label)
        self.emit("    mov sp, x29")
        self.emit("    ldp x29, x30, [sp], #16")
        self.emit("    ret")

    def gen_block(self, block: Block):
        for stmt in block.stmts:
            self.gen_stmt(stmt)

    def gen_stmt(self, stmt: Stmt):
        if isinstance(stmt, Block):
            self.gen_block(stmt)
        elif isinstance(stmt, ReturnStmt):
            self.gen_return(stmt)
        elif isinstance(stmt, VarDecl):
            self.gen_var_decl(stmt)
        elif isinstance(stmt, ExprStmt):
            if stmt.expr is not None:
                self.gen_expr(stmt.expr)
        elif isinstance(stmt, IfStmt):
            self.gen_if(stmt)
        elif isinstance(stmt, WhileStmt):
            self.gen_while(stmt)
        elif isinstance(stmt, DoWhileStmt):
            self.gen_do_while(stmt)
        elif isinstance(stmt, ForStmt):
            self.gen_for(stmt)
        elif isinstance(stmt, SwitchStmt):
            self.gen_switch(stmt)
        elif isinstance(stmt, CaseStmt):
            if hasattr(stmt, "_label"):
                self.label(stmt._label)
            if stmt.stmt is not None:
                self.gen_stmt(stmt.stmt)
        elif isinstance(stmt, BreakStmt):
            if not self.break_labels:
                self.error("break outside loop", stmt.line, stmt.col)
            self.emit(f"    b {self.break_labels[-1]}")
        elif isinstance(stmt, ContinueStmt):
            if not self.continue_labels:
                self.error("continue outside loop", stmt.line, stmt.col)
            self.emit(f"    b {self.continue_labels[-1]}")
        elif isinstance(stmt, GotoStmt):
            self.emit(f"    b {self.user_label(stmt.label)}")
        elif isinstance(stmt, IndirectGotoStmt):
            self.gen_expr(stmt.target)
            self.emit("    br x0")
        elif isinstance(stmt, LabelStmt):
            self.label(self.user_label(stmt.label))
            if stmt.stmt is not None:
                self.gen_stmt(stmt.stmt)
        elif isinstance(stmt, NullStmt):
            return
        else:
            self.error(
                f"arm64-apple-darwin backend does not yet support statement type {type(stmt).__name__}",
                stmt.line,
                stmt.col,
            )

    def gen_return(self, stmt: ReturnStmt):
        if stmt.value is None:
            self.emit("    mov w0, #0")
        else:
            self.gen_expr(stmt.value)
            ret_type = self.current_func.return_type if self.current_func else None
            if ret_type is not None and ret_type.is_struct() and not ret_type.is_pointer():
                # gen_expr put either an address (Identifier/MemberAccess) or bytes (FuncCall)
                # in x0.  Load struct bytes into x0[/x1] unless already done.
                if not self._is_struct_by_reg_value(stmt.value):
                    struct_size = ret_type.struct_def.size_bytes(self.target)
                    if struct_size <= 4:
                        self.emit("    ldr w0, [x0]")
                    elif struct_size <= 8:
                        self.emit("    ldr x0, [x0]")
                    elif struct_size <= 16:
                        self.emit("    mov x9, x0")
                        self.emit("    ldr x0, [x9]")
                        rem = struct_size - 8
                        self.emit("    ldr w1, [x9, #8]" if rem <= 4 else "    ldr x1, [x9, #8]")
            elif ret_type is not None and self.is_wide_scalar(ret_type):
                expr_type = self.get_expr_type(stmt.value)
                if expr_type is None or not (self.is_wide_scalar(expr_type) or expr_type.is_pointer()):
                    expr_size = expr_type.size_bytes(self.target) if expr_type is not None else 4
                    if expr_size <= 1:
                        self.emit("    sxtb w0, w0")
                    elif expr_size <= 2:
                        self.emit("    sxth w0, w0")
                    self.emit("    sxtw x0, w0")
        self.emit(f"    b {self.return_label}")

    def gen_var_decl(self, decl: VarDecl):
        if decl.type_spec is not None and decl.type_spec.is_extern and self.current_func is not None:
            if decl.name not in self.globals:
                self.globals[decl.name] = GlobalVarDecl(type_spec=decl.type_spec, name=decl.name, init=None)
            return
        if decl.type_spec is not None and decl.type_spec.is_static:
            return
        if decl.type_spec is not None and self.is_array_type(decl.type_spec) and isinstance(decl.init, StringLiteral) and decl.type_spec.base == "char":
            # char a[] = "string" — copy bytes to stack
            offset = self.locals[decl.name]
            self.emit(f"    sub x9, x29, #{offset}")
            for i, ch in enumerate(decl.init.value):
                code = ord(ch)
                if code >= 0xF700:
                    code -= 0xF700
                self.emit(f"    movz w0, #{code}")
                self.emit(f"    strb w0, [x9, #{i}]")
            self.emit(f"    strb wzr, [x9, #{len(decl.init.value)}]")
            return
        if decl.type_spec is not None and self.is_array_type(decl.type_spec) and isinstance(decl.init, InitList):
            self.gen_local_array_init(decl)
            return
        if decl.type_spec is not None and decl.type_spec.is_struct() and not decl.type_spec.is_pointer() and isinstance(decl.init, InitList):
            self.gen_local_struct_init(decl)
            return
        # Compound literal: (Type){init} — treat as struct/array init
        if (isinstance(decl.init, CastExpr) and isinstance(decl.init.operand, InitList)):
            compound_type = decl.init.target_type
            # If var is a struct and compound type is also struct: unwrap and use struct init path
            if (decl.type_spec is not None and decl.type_spec.is_struct() and not decl.type_spec.is_pointer()
                    and compound_type is not None and compound_type.is_struct() and not compound_type.is_pointer()):
                unwrapped = VarDecl(
                    name=decl.name, type_spec=decl.type_spec,
                    init=decl.init.operand, line=decl.line, col=decl.col,
                )
                return self.gen_var_decl(unwrapped)
            # Otherwise: gen_cast materializes it, returns value/address in x0
            self.gen_expr(decl.init)
            if decl.name in self.locals:
                if self.is_pointer_type(decl.type_spec) or self.is_wide_scalar(decl.type_spec):
                    self.emit_local_store("stur", "x0", self.locals[decl.name])
                else:
                    self.emit_local_store("stur", "w0", self.locals[decl.name])
            return
        if decl.type_spec is not None and decl.type_spec.is_struct() and not decl.type_spec.is_pointer() and decl.init is not None:
            self.gen_expr(decl.init)
            struct_size = decl.type_spec.struct_def.size_bytes(self.target)
            if self._is_struct_by_reg_value(decl.init):
                # FuncCall returned bytes in x0[/x1] — store directly
                if decl.name in self.locals:
                    dest_offset = self.locals[decl.name]
                    if struct_size <= 4:
                        self.emit_local_store("stur", "w0", dest_offset)
                    elif struct_size <= 8:
                        self.emit_local_store("stur", "x0", dest_offset)
                    elif struct_size <= 16:
                        self.emit_local_store("stur", "x0", dest_offset)
                        rem = struct_size - 8
                        self.emit_local_store("stur", "w1" if rem <= 4 else "x1", dest_offset - 8)
                elif decl.name in self.static_locals:
                    self.push_x0()
                    self.emit_symbol_addr(self.static_locals[decl.name], "x0")
                    self.pop_reg("x1")
                    self.emit(f"    mov x2, #{struct_size}")
                    self.emit("    bl _memcpy")
                elif decl.name in self.globals:
                    self.push_x0()
                    self.emit_symbol_addr(self.mangle(decl.name), "x0")
                    self.pop_reg("x1")
                    self.emit(f"    mov x2, #{struct_size}")
                    self.emit("    bl _memcpy")
            else:
                # gen_expr returned source address in x0 — copy via memcpy
                self.push_x0()
                if decl.name in self.locals:
                    self.emit(f"    sub x0, x29, #{self.locals[decl.name]}")
                elif decl.name in self.static_locals:
                    self.emit_symbol_addr(self.static_locals[decl.name], "x0")
                elif decl.name in self.globals:
                    self.emit_symbol_addr(self.mangle(decl.name), "x0")
                self.pop_reg("x1")
                self.emit(f"    mov x2, #{struct_size}")
                self.emit("    bl _memcpy")
            return
        if decl.type_spec is not None and decl.init is None:
            if decl.name in self.vla_ptr_locals:
                # VLA array: compute size at runtime and allocate on stack
                self._emit_runtime_size(decl.type_spec)
                self.emit("    add x0, x0, #15")
                self.emit("    bic x0, x0, #15")
                self.emit("    sub sp, sp, x0")
                self.emit("    mov x0, sp")
                self.emit_local_store("stur", "x0", self.locals[decl.name])
                return
            if decl.type_spec.is_array() or (decl.type_spec.is_struct() and not decl.type_spec.is_pointer()):
                return
        if decl.init is None:
            self.emit("    mov w0, #0")
        else:
            self.gen_expr(decl.init)
            # If target is FP but value is integer, convert now
            if decl.type_spec is not None and self.is_fp_type(decl.type_spec):
                val_type = self.get_expr_type(decl.init)
                if not self.is_fp_type(val_type):
                    if val_type is not None and val_type.is_unsigned:
                        self.emit("    ucvtf d0, x0" if self.is_wide_scalar(val_type) else "    ucvtf d0, w0")
                    else:
                        self.emit("    scvtf d0, x0" if self.is_wide_scalar(val_type) else "    scvtf d0, w0")
            # Sign-extend narrow expressions into wide (i64) local variables
            elif decl.type_spec is not None and self.is_wide_scalar(decl.type_spec) and not decl.type_spec.is_unsigned:
                expr_type = self.get_expr_type(decl.init)
                if expr_type is None or not (self.is_wide_scalar(expr_type) or expr_type.is_pointer()):
                    expr_size = expr_type.size_bytes(self.target) if expr_type is not None else 4
                    if expr_size <= 1:
                        self.emit("    sxtb w0, w0")
                    elif expr_size <= 2:
                        self.emit("    sxth w0, w0")
                    self.emit("    sxtw x0, w0")
        self.store_var(decl.name, line=decl.line, col=decl.col)

    def gen_local_array_init(self, decl: VarDecl):
        self.emit(f"    sub x9, x29, #{self.locals[decl.name]}")
        elem_type = self.element_type(decl.type_spec)
        elem_size = self.total_size(elem_type)
        for index, item in enumerate(decl.init.items):
            value = item.value
            if value is None:
                continue
            offset = index * elem_size
            if elem_type is not None and elem_type.is_struct() and not elem_type.is_pointer() and isinstance(value, InitList):
                # Array of structs: init each struct element using x29-relative addressing
                x29_neg_off = self.locals[decl.name] - offset
                self.gen_struct_init_at_addr(elem_type, value, x29_neg_off)
                continue
            if self.is_array_type(elem_type) and isinstance(value, InitList):
                # 2D array: recursively init sub-array
                sub_decl = VarDecl(
                    name=decl.name, type_spec=elem_type,
                    init=value, line=decl.line, col=decl.col,
                )
                # Temporarily shift locals so sub-array starts at correct offset
                orig_offset = self.locals[decl.name]
                self.locals[decl.name] = orig_offset - offset
                self.gen_local_array_init(sub_decl)
                self.locals[decl.name] = orig_offset
                continue
            if self.is_array_type(elem_type) and isinstance(value, StringLiteral) and elem_type.base == "char":
                # char sub-array initialized from string literal — copy bytes
                str_bytes = [ord(c) for c in value.value] + [0]
                for i in range(self.total_size(elem_type)):
                    b = str_bytes[i] if i < len(str_bytes) else 0
                    self.emit(f"    movz w0, #{b}")
                    self.emit(f"    strb w0, [x9, #{offset + i}]")
                continue
            self.gen_expr(value)
            if self.is_fp_type(elem_type):
                if elem_type is not None and elem_type.base == "float":
                    self.emit("    fcvt s0, d0")
                    self.emit(f"    str s0, [x9, #{offset}]")
                else:
                    self.emit(f"    str d0, [x9, #{offset}]")
            elif elem_type is not None and self.is_pointer_type(elem_type):
                self.emit(f"    str x0, [x9, #{offset}]")
            elif self.is_byte_type(elem_type):
                self.emit(f"    strb w0, [x9, #{offset}]")
            elif elem_type is not None and elem_type.base == "short" and not elem_type.is_pointer():
                self.emit(f"    strh w0, [x9, #{offset}]")
            else:
                self.emit(f"    str w0, [x9, #{offset}]")

    def gen_struct_init_at_addr(self, type_spec, init: 'InitList', x29_neg_offset: int):
        """Write struct init list items to [x29 - x29_neg_offset + member_off] for each member.
        Uses x29-relative stores so gen_expr clobbering scratch regs is safe."""
        struct_def = type_spec.struct_def
        if struct_def is None:
            return
        members = [m for m in struct_def.members if m.name != ""]
        for i, item in enumerate(init.items):
            if i >= len(members):
                break
            if item.value is None:
                continue
            member = members[i]
            member_off = struct_def.member_offset(member.name) or 0
            member_type = member.type_spec
            if member_type is not None and member_type.is_struct() and not member_type.is_pointer() and isinstance(item.value, InitList):
                self.gen_struct_init_at_addr(member_type, item.value, x29_neg_offset - member_off)
                continue
            self.gen_expr(item.value)
            # Compute address: x29 - x29_neg_offset + member_off
            final_neg = x29_neg_offset - member_off
            self.emit(f"    sub x9, x29, #{final_neg}")
            if self.is_fp_type(member_type):
                if member_type.base == "float":
                    self.emit("    fcvt s0, d0")
                    self.emit("    str s0, [x9]")
                else:
                    self.emit("    str d0, [x9]")
            elif self.is_pointer_type(member_type) or self.is_wide_scalar(member_type):
                self.emit("    str x0, [x9]")
            elif member_type is not None and member_type.size_bytes(self.target) <= 1:
                self.emit("    strb w0, [x9]")
            elif member_type is not None and member_type.size_bytes(self.target) <= 2:
                self.emit("    strh w0, [x9]")
            else:
                self.emit("    str w0, [x9]")

    def gen_local_struct_init(self, decl: VarDecl):
        struct_def = decl.type_spec.struct_def
        if struct_def is None:
            return
        self.emit(f"    sub x9, x29, #{self.locals[decl.name]}")
        members = [m for m in struct_def.members if m.name != ""]
        for i, item in enumerate(decl.init.items):
            if i >= len(members):
                break
            if item.value is None:
                continue
            member = members[i]
            member_off = struct_def.member_offset(member.name) or 0
            member_type = member.type_spec
            self.gen_expr(item.value)
            if self.is_fp_type(member_type):
                if member_type.base == "float":
                    self.emit("    fcvt s0, d0")
                    self.emit(f"    str s0, [x9, #{member_off}]")
                else:
                    self.emit(f"    str d0, [x9, #{member_off}]")
            elif self.is_pointer_type(member_type) or self.is_wide_scalar(member_type):
                self.emit(f"    str x0, [x9, #{member_off}]")
            elif member_type.size_bytes(self.target) <= 1:
                self.emit(f"    strb w0, [x9, #{member_off}]")
            elif member_type.size_bytes(self.target) <= 2:
                self.emit(f"    strh w0, [x9, #{member_off}]")
            else:
                self.emit(f"    str w0, [x9, #{member_off}]")

    def gen_if(self, stmt: IfStmt):
        else_label = self.new_label("else")
        end_label = self.new_label("ifend")
        self.gen_condition(stmt.condition)
        self.emit(f"    cbz w0, {else_label}")
        self.gen_stmt(stmt.then_body)
        if stmt.else_body is not None:
            self.emit(f"    b {end_label}")
            self.label(else_label)
            self.gen_stmt(stmt.else_body)
            self.label(end_label)
        else:
            self.label(else_label)

    def gen_while(self, stmt: WhileStmt):
        start_label = self.new_label("while")
        end_label = self.new_label("whileend")
        self.break_labels.append(end_label)
        self.continue_labels.append(start_label)
        self.label(start_label)
        self.gen_condition(stmt.condition)
        self.emit(f"    cbz w0, {end_label}")
        self.gen_stmt(stmt.body)
        self.emit(f"    b {start_label}")
        self.label(end_label)
        self.break_labels.pop()
        self.continue_labels.pop()

    def gen_do_while(self, stmt: DoWhileStmt):
        start_label = self.new_label("dowhile")
        cond_label = self.new_label("dowhilecond")
        end_label = self.new_label("dowhileend")
        self.break_labels.append(end_label)
        self.continue_labels.append(cond_label)
        self.label(start_label)
        self.gen_stmt(stmt.body)
        self.label(cond_label)
        self.gen_condition(stmt.condition)
        self.emit(f"    cbnz w0, {start_label}")
        self.label(end_label)
        self.break_labels.pop()
        self.continue_labels.pop()

    def gen_for(self, stmt: ForStmt):
        cond_label = self.new_label("for")
        update_label = self.new_label("forupd")
        end_label = self.new_label("forend")
        self.break_labels.append(end_label)
        self.continue_labels.append(update_label)

        if stmt.init is not None:
            self.gen_stmt(stmt.init)

        self.label(cond_label)
        if stmt.condition is not None:
            self.gen_condition(stmt.condition)
            self.emit(f"    cbz w0, {end_label}")

        self.gen_stmt(stmt.body)

        self.label(update_label)
        if stmt.update is not None:
            self.gen_expr(stmt.update)
        self.emit(f"    b {cond_label}")
        self.label(end_label)
        self.break_labels.pop()
        self.continue_labels.pop()

    def gen_switch(self, stmt: SwitchStmt):
        end_label = self.new_label("switchend")
        self.break_labels.append(end_label)

        self.gen_expr(stmt.expr)
        self.emit("    mov w10, w0")

        body = stmt.body
        if not isinstance(body, Block):
            if isinstance(body, CaseStmt):
                body = Block(stmts=[body], line=body.line, col=body.col)
            else:
                self.emit(f"    b {end_label}")
                self.gen_stmt(body)
                self.label(end_label)
                self.break_labels.pop()
                return
        stmt.body = body

        cases = []
        default_label = None

        def collect_cases(node):
            nonlocal default_label
            if isinstance(node, CaseStmt):
                label = self.new_label("case")
                if node.is_default:
                    default_label = label
                else:
                    cases.append((node, label))
                node._label = label
                if node.stmt is not None:
                    collect_cases(node.stmt)
            elif isinstance(node, Block):
                for child in node.stmts:
                    collect_cases(child)
            elif isinstance(node, IfStmt):
                if node.then_body is not None:
                    collect_cases(node.then_body)
                if node.else_body is not None:
                    collect_cases(node.else_body)
            elif isinstance(node, WhileStmt):
                collect_cases(node.body)
            elif isinstance(node, DoWhileStmt):
                collect_cases(node.body)
            elif isinstance(node, ForStmt):
                collect_cases(node.body)
            elif isinstance(node, LabelStmt) and node.stmt is not None:
                collect_cases(node.stmt)

        collect_cases(stmt.body)

        for case_stmt, label in cases:
            value = case_stmt.value
            if isinstance(value, IntLiteral):
                case_val = value.value
            elif (isinstance(value, UnaryOp) and value.op == "-"
                  and isinstance(value.operand, IntLiteral)):
                case_val = -value.operand.value
            elif (isinstance(value, UnaryOp) and value.op == "+"
                  and isinstance(value.operand, IntLiteral)):
                case_val = value.operand.value
            else:
                self.error("arm64-apple-darwin switch requires integer literal case labels", case_stmt.line, case_stmt.col)
                continue
            if 0 <= case_val <= 4095:
                self.emit(f"    cmp w10, #{case_val}")
            else:
                self.emit_int_constant(case_val & 0xFFFFFFFF, "w11")
                self.emit("    cmp w10, w11")
            self.emit(f"    b.eq {label}")

        self.emit(f"    b {default_label or end_label}")
        self.gen_stmt(stmt.body)
        self.label(end_label)
        self.break_labels.pop()

    def gen_expr(self, expr: Expr):
        if isinstance(expr, IntLiteral):
            self.emit_int_constant(expr.value, "x0" if self.literal_is_wide(expr) else "w0")
        elif isinstance(expr, FloatLiteral):
            self.gen_float_literal(expr)
        elif isinstance(expr, Identifier):
            if expr.name in ("__func__", "__FUNCTION__", "__PRETTY_FUNCTION__"):
                self.gen_string_literal(StringLiteral(value=self.current_func.name if self.current_func else ""))
            else:
                self.load_var(expr.name, expr.line, expr.col)
        elif isinstance(expr, CastExpr):
            self.gen_cast(expr)
        elif isinstance(expr, CommaExpr):
            self.gen_comma(expr)
        elif isinstance(expr, StringLiteral):
            self.gen_string_literal(expr)
        elif isinstance(expr, SizeofExpr):
            self.gen_sizeof(expr)
        elif isinstance(expr, AlignofExpr):
            self.gen_alignof(expr)
        elif isinstance(expr, ArrayAccess):
            self.gen_array_access(expr)
        elif isinstance(expr, Assignment):
            self.gen_assignment(expr)
        elif isinstance(expr, BinaryOp):
            self.gen_binary_op(expr)
        elif isinstance(expr, UnaryOp):
            self.gen_unary_op(expr)
        elif isinstance(expr, MemberAccess):
            self.gen_member_access(expr)
        elif isinstance(expr, TernaryOp):
            self.gen_ternary(expr)
        elif isinstance(expr, BuiltinVaArg):
            self._gen_builtin_va_arg(expr)
        elif isinstance(expr, LabelAddrExpr):
            fname = expr.func_name or (self.current_func.name if self.current_func else "")
            lbl = self.user_label_for(fname, expr.label)
            self.emit(f"    adrp x0, {lbl}@PAGE")
            self.emit(f"    add x0, x0, {lbl}@PAGEOFF")
        elif isinstance(expr, FuncCall):
            self.gen_func_call(expr)
        elif isinstance(expr, GenericSelection):
            self._gen_generic_selection(expr)
        else:
            self.error(
                f"arm64-apple-darwin backend does not yet support expression type {type(expr).__name__}",
                expr.line,
                expr.col,
            )

    def gen_assignment(self, expr: Assignment):
        if expr.op != "=":
            target_type = (self.get_var_type(expr.target.name)
                           if isinstance(expr.target, Identifier)
                           else self.get_expr_type(expr.target))
            wide = self.is_wide_scalar(target_type)
            op = expr.op[:-1]
            is_short = target_type is not None and target_type.base == "short" and not target_type.is_pointer()
            is_char = self.is_byte_type(target_type)

            if self.is_fp_type(target_type):
                # FP compound assignment — load current, compute, store
                if isinstance(expr.target, Identifier):
                    self.load_var(expr.target.name, expr.line, expr.col)
                else:
                    self.gen_expr(expr.target)
                self.push_d0()
                self.gen_expr(expr.value)
                if not self.is_fp_type(self.get_expr_type(expr.value)):
                    val_type = self.get_expr_type(expr.value)
                    if val_type is not None and val_type.is_unsigned:
                        self.emit("    ucvtf d0, x0" if self.is_wide_scalar(val_type) else "    ucvtf d0, w0")
                    else:
                        self.emit("    scvtf d0, x0" if self.is_wide_scalar(val_type) else "    scvtf d0, w0")
                self.pop_d0("d1")
                if op == "+":
                    self.emit("    fadd d0, d1, d0")
                elif op == "-":
                    self.emit("    fsub d0, d1, d0")
                elif op == "*":
                    self.emit("    fmul d0, d1, d0")
                elif op == "/":
                    self.emit("    fdiv d0, d1, d0")
                else:
                    self.error(f"compound assignment '{expr.op}' is not supported for FP on arm64-apple-darwin", expr.line, expr.col)
                if isinstance(expr.target, Identifier):
                    self.store_var(expr.target.name, line=expr.line, col=expr.col)
                else:
                    self.push_d0()
                    self.gen_lvalue_addr(expr.target)
                    self.pop_d0("d1")
                    if target_type is not None and target_type.base == "float":
                        self.emit("    fcvt s1, d1")
                        self.emit("    str s1, [x0]")
                    else:
                        self.emit("    str d1, [x0]")
                    self.emit("    fmov d0, d1")
                return

            # Integer compound assignment
            if isinstance(expr.target, Identifier):
                self.load_var(expr.target.name, expr.line, expr.col)
                self.push_x0()
                self.gen_expr(expr.value)
                self.pop_reg("x1")
            else:
                # Non-identifier target: load via address, compute, store back
                self.gen_expr(expr.target)
                self.push_x0()
                self.gen_expr(expr.value)
                self.pop_reg("x1")

            if op == "+":
                self.emit("    add x0, x1, x0" if wide else "    add w0, w1, w0")
            elif op == "-":
                self.emit("    sub x0, x1, x0" if wide else "    sub w0, w1, w0")
            elif op == "*":
                self.emit("    mul x0, x1, x0" if wide else "    mul w0, w1, w0")
            elif op == "/":
                if target_type is not None and target_type.is_unsigned:
                    self.emit("    udiv x0, x1, x0" if wide else "    udiv w0, w1, w0")
                else:
                    self.emit("    sdiv x0, x1, x0" if wide else "    sdiv w0, w1, w0")
            elif op == "%":
                if target_type is not None and target_type.is_unsigned:
                    if wide:
                        self.emit("    udiv x2, x1, x0")
                        self.emit("    msub x0, x2, x0, x1")
                    else:
                        self.emit("    udiv w2, w1, w0")
                        self.emit("    msub w0, w2, w0, w1")
                else:
                    if wide:
                        self.emit("    sdiv x2, x1, x0")
                        self.emit("    msub x0, x2, x0, x1")
                    else:
                        self.emit("    sdiv w2, w1, w0")
                        self.emit("    msub w0, w2, w0, w1")
            elif op == "&":
                self.emit("    and x0, x1, x0" if wide else "    and w0, w1, w0")
            elif op == "|":
                self.emit("    orr x0, x1, x0" if wide else "    orr w0, w1, w0")
            elif op == "^":
                self.emit("    eor x0, x1, x0" if wide else "    eor w0, w1, w0")
            elif op == "<<":
                self.emit("    lslv x0, x1, x0" if wide else "    lslv w0, w1, w0")
            elif op == ">>":
                if target_type is not None and target_type.is_unsigned:
                    self.emit("    lsrv x0, x1, x0" if wide else "    lsrv w0, w1, w0")
                else:
                    self.emit("    asrv x0, x1, x0" if wide else "    asrv w0, w1, w0")
            else:
                self.error(f"compound assignment '{expr.op}' is not yet supported on arm64-apple-darwin", expr.line, expr.col)

            # Truncate to target size for short/char
            if is_short:
                self.emit("    and w0, w0, #0xffff")
            elif is_char:
                self.emit("    and w0, w0, #0xff")

            if isinstance(expr.target, Identifier):
                self.store_var(expr.target.name, line=expr.line, col=expr.col)
            else:
                # Store result back via address
                self.push_x0()
                self.gen_lvalue_addr(expr.target)
                self.pop_reg("x1")
                if target_type is not None and target_type.is_pointer():
                    self.emit("    str x1, [x0]")
                elif is_char:
                    self.emit("    strb w1, [x0]")
                elif is_short:
                    self.emit("    strh w1, [x0]")
                elif wide:
                    self.emit("    str x1, [x0]")
                else:
                    self.emit("    str w1, [x0]")
                self.emit("    mov x0, x1")
            return

        self.gen_expr(expr.value)
        if isinstance(expr.target, Identifier):
            target_type = self.get_var_type(expr.target.name)
            if target_type is not None and target_type.is_struct() and not target_type.is_pointer():
                struct_size = target_type.struct_def.size_bytes(self.target)
                if self._is_struct_by_reg_value(expr.value):
                    # FuncCall bytes in x0[/x1] — store directly
                    if expr.target.name in self.locals:
                        dest_offset = self.locals[expr.target.name]
                        if struct_size <= 4:
                            self.emit_local_store("stur", "w0", dest_offset)
                        elif struct_size <= 8:
                            self.emit_local_store("stur", "x0", dest_offset)
                        elif struct_size <= 16:
                            self.emit_local_store("stur", "x0", dest_offset)
                            rem = struct_size - 8
                            self.emit_local_store("stur", "w1" if rem <= 4 else "x1", dest_offset - 8)
                    else:
                        self.push_x0()
                        self.gen_lvalue_addr(expr.target)
                        self.pop_reg("x1")
                        self.emit(f"    mov x2, #{struct_size}")
                        self.emit("    bl _memcpy")
                else:
                    self.push_x0()
                    self.gen_lvalue_addr(expr.target)
                    self.pop_reg("x1")
                    self.emit(f"    mov x2, #{struct_size}")
                    self.emit("    bl _memcpy")
                return
            if self.is_fp_type(target_type):
                val_type = self.get_expr_type(expr.value)
                if not self.is_fp_type(val_type):
                    if val_type is not None and val_type.is_unsigned:
                        self.emit("    ucvtf d0, x0" if self.is_wide_scalar(val_type) else "    ucvtf d0, w0")
                    else:
                        self.emit("    scvtf d0, x0" if self.is_wide_scalar(val_type) else "    scvtf d0, w0")
            self.store_var(expr.target.name, line=expr.line, col=expr.col)
            return

        # Bitfield assignment
        if isinstance(expr.target, MemberAccess) and expr.op == "=":
            obj_type = self.get_expr_type(expr.target.obj)
            sdef = obj_type.struct_def if obj_type else None
            if sdef:
                bf = sdef.bitfield_info(expr.target.member, self.target)
                if bf:
                    unit_off, unit_size, bit_start, bit_width = bf
                    mask = (1 << bit_width) - 1
                    self.push_x0()
                    self.gen_member_addr(expr.target)
                    self.emit("    mov x9, x0")  # x9 = addr of storage unit
                    # load current storage unit
                    if unit_size == 1:
                        self.emit("    ldrb w10, [x9]")
                    elif unit_size == 2:
                        self.emit("    ldrh w10, [x9]")
                    elif unit_size == 8:
                        self.emit("    ldr x10, [x9]")
                    else:
                        self.emit("    ldr w10, [x9]")
                    # clear the bitfield bits
                    clear_mask = (~(mask << bit_start)) & ((1 << (unit_size * 8)) - 1)
                    if unit_size == 8:
                        self.emit_int_constant(clear_mask, "x11")
                        self.emit("    and x10, x10, x11")
                    else:
                        self.emit_int_constant(clear_mask & 0xFFFFFFFF, "w11")
                        self.emit("    and w10, w10, w11")
                    # pop new value, mask and shift
                    self.pop_reg("x0")
                    if unit_size == 8:
                        self.emit(f"    and x0, x0, #{mask}")
                        if bit_start > 0:
                            self.emit(f"    lsl x0, x0, #{bit_start}")
                        self.emit("    orr x10, x10, x0")
                        self.emit("    str x10, [x9]")
                    else:
                        self.emit(f"    and w0, w0, #{mask}")
                        if bit_start > 0:
                            self.emit(f"    lsl w0, w0, #{bit_start}")
                        self.emit("    orr w10, w10, w0")
                        if unit_size == 1:
                            self.emit("    strb w10, [x9]")
                        elif unit_size == 2:
                            self.emit("    strh w10, [x9]")
                        else:
                            self.emit("    str w10, [x9]")
                    return

        if isinstance(expr.target, (UnaryOp, ArrayAccess, MemberAccess, GenericSelection)):
            target_type = self.get_expr_type(expr.target)
            if target_type is not None and target_type.is_struct() and not target_type.is_pointer():
                struct_size = target_type.struct_def.size_bytes(self.target)
                if self._is_struct_by_reg_value(expr.value):
                    # FuncCall bytes in x0[/x1] — compute dest address, then store
                    if struct_size <= 4:
                        self.push_x0()
                        self.gen_lvalue_addr(expr.target)
                        self.pop_reg("x1")
                        self.emit("    str w1, [x0]")
                    elif struct_size <= 8:
                        self.push_x0()
                        self.gen_lvalue_addr(expr.target)
                        self.pop_reg("x1")
                        self.emit("    str x1, [x0]")
                    elif struct_size <= 16:
                        self.push_x0()  # save x0 (bytes 0-7)
                        self.emit("    mov x10, x1")  # save x1 (bytes 8-15 or w1)
                        self.gen_lvalue_addr(expr.target)
                        self.pop_reg("x1")
                        self.emit("    str x1, [x0]")
                        rem = struct_size - 8
                        if rem <= 4:
                            self.emit("    str w10, [x0, #8]")
                        else:
                            self.emit("    str x10, [x0, #8]")
                    else:
                        self.push_x0()
                        self.gen_lvalue_addr(expr.target)
                        self.pop_reg("x1")
                        self.emit(f"    mov x2, #{struct_size}")
                        self.emit("    bl _memcpy")
                else:
                    self.push_x0()
                    self.gen_lvalue_addr(expr.target)
                    self.pop_reg("x1")
                    self.emit(f"    mov x2, #{struct_size}")
                    self.emit("    bl _memcpy")
                return
            if self.is_fp_type(target_type):
                val_type = self.get_expr_type(expr.value)
                if not self.is_fp_type(val_type):
                    # Convert integer to double before storing
                    if val_type is not None and val_type.is_unsigned:
                        self.emit("    ucvtf d0, x0" if self.is_wide_scalar(val_type) else "    ucvtf d0, w0")
                    else:
                        self.emit("    scvtf d0, x0" if self.is_wide_scalar(val_type) else "    scvtf d0, w0")
                self.push_d0()
                self.gen_lvalue_addr(expr.target)
                self.pop_d0("d1")
                if target_type.base == "float":
                    self.emit("    fcvt s1, d1")
                    self.emit("    str s1, [x0]")
                else:
                    self.emit("    str d1, [x0]")
                self.emit("    fmov d0, d1")
            else:
                self.push_x0()
                self.gen_lvalue_addr(expr.target)
                self.pop_reg("x1")
                if target_type is not None and target_type.is_pointer():
                    self.emit("    str x1, [x0]")
                    self.emit("    mov x0, x1")
                elif self.is_byte_type(target_type):
                    self.emit("    strb w1, [x0]")
                    self.emit("    and w0, w1, #0xff")
                elif target_type is not None and target_type.base == "short" and not target_type.is_pointer():
                    self.emit("    strh w1, [x0]")
                    self.emit("    and w0, w1, #0xffff")
                elif self.is_wide_scalar(target_type):
                    src_type = self.get_expr_type(expr.value)
                    if src_type is None or (not self.is_wide_scalar(src_type) and not self.is_pointer_type(src_type) and not src_type.is_unsigned):
                        self.emit("    sxtw x1, w1")
                    self.emit("    str x1, [x0]")
                    self.emit("    mov x0, x1")
                else:
                    self.emit("    str w1, [x0]")
                    self.emit("    mov w0, w1")
            return

        self.error("assignment target is not yet supported on arm64-apple-darwin", expr.line, expr.col)

    def gen_binary_op(self, expr: BinaryOp):
        if expr.op == "&&":
            false_label = self.new_label("andfalse")
            end_label = self.new_label("andend")
            self.gen_condition(expr.left)
            self.emit(f"    cbz w0, {false_label}")
            self.gen_condition(expr.right)
            self.emit(f"    cbz w0, {false_label}")
            self.emit("    mov w0, #1")
            self.emit(f"    b {end_label}")
            self.label(false_label)
            self.emit("    mov w0, #0")
            self.label(end_label)
            return

        if expr.op == "||":
            true_label = self.new_label("ortrue")
            end_label = self.new_label("orend")
            self.gen_condition(expr.left)
            self.emit(f"    cbnz w0, {true_label}")
            self.gen_condition(expr.right)
            self.emit(f"    cbnz w0, {true_label}")
            self.emit("    mov w0, #0")
            self.emit(f"    b {end_label}")
            self.label(true_label)
            self.emit("    mov w0, #1")
            self.label(end_label)
            return

        left_type = self.get_expr_type(expr.left)
        right_type = self.get_expr_type(expr.right)
        is_fp_op = self.is_fp_type(left_type) or self.is_fp_type(right_type)

        if is_fp_op:
            self.gen_expr(expr.left)
            if not self.is_fp_type(left_type):
                if left_type is not None and left_type.is_unsigned:
                    self.emit("    ucvtf d0, x0" if self.is_wide_scalar(left_type) else "    ucvtf d0, w0")
                else:
                    self.emit("    scvtf d0, x0" if self.is_wide_scalar(left_type) else "    scvtf d0, w0")
            self.push_d0()
            self.gen_expr(expr.right)
            if not self.is_fp_type(right_type):
                if right_type is not None and right_type.is_unsigned:
                    self.emit("    ucvtf d0, x0" if self.is_wide_scalar(right_type) else "    ucvtf d0, w0")
                else:
                    self.emit("    scvtf d0, x0" if self.is_wide_scalar(right_type) else "    scvtf d0, w0")
            self.pop_d0("d1")
            fp_cond = {
                "==": "eq", "!=": "ne",
                "<": "mi", "<=": "ls",
                ">": "gt", ">=": "ge",
            }
            if expr.op in fp_cond:
                self.emit("    fcmp d1, d0")
                self.emit(f"    cset w0, {fp_cond[expr.op]}")
            elif expr.op == "+":
                self.emit("    fadd d0, d1, d0")
            elif expr.op == "-":
                self.emit("    fsub d0, d1, d0")
            elif expr.op == "*":
                self.emit("    fmul d0, d1, d0")
            elif expr.op == "/":
                self.emit("    fdiv d0, d1, d0")
            else:
                self.error(f"binary operator '{expr.op}' is not supported for floating-point on arm64-apple-darwin", expr.line, expr.col)
            return

        self.gen_expr(expr.left)
        self.push_x0()
        self.gen_expr(expr.right)
        self.pop_reg("x1")

        left_ptr = left_type is not None and (left_type.is_pointer() or self.is_array_type(left_type))
        right_ptr = right_type is not None and (right_type.is_pointer() or self.is_array_type(right_type))
        result_type = self.get_expr_type(expr)
        wide = self.is_wide_scalar(left_type) or self.is_wide_scalar(right_type) or self.is_wide_scalar(result_type)
        is_unsigned = (left_type is not None and left_type.is_unsigned) or (right_type is not None and right_type.is_unsigned)

        # Sign-extend narrow operands when mixing 32-bit and 64-bit scalars
        if wide and not right_ptr and right_type is not None and not self.is_wide_scalar(right_type) and not right_type.is_pointer() and not right_type.is_unsigned:
            self.emit("    sxtw x0, w0")
        if wide and not left_ptr and left_type is not None and not self.is_wide_scalar(left_type) and not left_type.is_pointer() and not left_type.is_unsigned:
            self.emit("    sxtw x1, w1")

        if expr.op == "+" and left_ptr and not right_ptr:
            scale = self.element_size(left_type)
            self.emit("    sxtw x0, w0")
            if scale != 1:
                self.emit(f"    mov x2, #{scale}")
                self.emit("    mul x0, x0, x2")
            self.emit("    add x0, x1, x0")
        elif expr.op == "+" and right_ptr and not left_ptr:
            scale = self.element_size(right_type)
            self.emit("    sxtw x1, w1")
            if scale != 1:
                self.emit(f"    mov x2, #{scale}")
                self.emit("    mul x1, x1, x2")
            self.emit("    add x0, x0, x1")
        elif expr.op == "-" and left_ptr and right_ptr:
            # pointer - pointer = ptrdiff_t (divide byte-diff by element size)
            self.emit("    sub x0, x1, x0")
            scale = self.element_size(left_type)
            if scale > 1:
                self.emit(f"    mov x2, #{scale}")
                self.emit("    sdiv x0, x0, x2")
        elif expr.op == "-" and left_ptr and not right_ptr:
            scale = self.element_size(left_type)
            self.emit("    sxtw x0, w0")
            if scale != 1:
                self.emit(f"    mov x2, #{scale}")
                self.emit("    mul x0, x0, x2")
            self.emit("    sub x0, x1, x0")
        elif expr.op == "+":
            self.emit("    add x0, x1, x0" if wide else "    add w0, w1, w0")
        elif expr.op == "-":
            self.emit("    sub x0, x1, x0" if wide else "    sub w0, w1, w0")
        elif expr.op == "*":
            self.emit("    mul x0, x1, x0" if wide else "    mul w0, w1, w0")
        elif expr.op == "/":
            div = "udiv" if is_unsigned else "sdiv"
            self.emit(f"    {div} x0, x1, x0" if wide else f"    {div} w0, w1, w0")
        elif expr.op == "%":
            div = "udiv" if is_unsigned else "sdiv"
            if wide:
                self.emit(f"    {div} x2, x1, x0")
                self.emit("    msub x0, x2, x0, x1")
            else:
                self.emit(f"    {div} w2, w1, w0")
                self.emit("    msub w0, w2, w0, w1")
        elif expr.op == "&":
            self.emit("    and x0, x1, x0" if wide else "    and w0, w1, w0")
        elif expr.op == "|":
            self.emit("    orr x0, x1, x0" if wide else "    orr w0, w1, w0")
        elif expr.op == "^":
            self.emit("    eor x0, x1, x0" if wide else "    eor w0, w1, w0")
        elif expr.op == "<<":
            self.emit("    lslv x0, x1, x0" if wide else "    lslv w0, w1, w0")
        elif expr.op == ">>":
            shr = "lsrv" if is_unsigned else "asrv"
            self.emit(f"    {shr} x0, x1, x0" if wide else f"    {shr} w0, w1, w0")
        elif expr.op in {"==", "!=", "<", "<=", ">", ">="}:
            self.emit("    cmp x1, x0" if (left_ptr or right_ptr or wide) else "    cmp w1, w0")
            if is_unsigned or left_ptr or right_ptr:
                cond = {"==": "eq", "!=": "ne", "<": "lo", "<=": "ls", ">": "hi", ">=": "hs"}[expr.op]
            else:
                cond = {"==": "eq", "!=": "ne", "<": "lt", "<=": "le", ">": "gt", ">=": "ge"}[expr.op]
            self.emit(f"    cset w0, {cond}")
        else:
            self.error(f"binary operator '{expr.op}' is not yet supported on arm64-apple-darwin", expr.line, expr.col)

    def gen_unary_op(self, expr: UnaryOp):
        if expr.op in {"++", "--"}:
            if isinstance(expr.operand, Identifier):
                name = expr.operand.name
                type_spec = self.get_var_type(name)
                is_pointer = self.is_pointer_type(type_spec)
                delta = self.element_size(type_spec) if is_pointer else 1
                self.load_var(name, expr.line, expr.col)
                if expr.prefix:
                    op = "add" if expr.op == "++" else "sub"
                    if is_pointer:
                        self.emit(f"    {op} x0, x0, #{delta}")
                        self.store_var(name, src_reg="x0", line=expr.line, col=expr.col)
                    else:
                        self.emit(f"    {op} w0, w0, #1")
                        self.store_var(name, src_reg="w0", line=expr.line, col=expr.col)
                else:
                    op = "add" if expr.op == "++" else "sub"
                    if is_pointer:
                        self.emit("    mov x1, x0")
                        self.emit(f"    {op} x1, x1, #{delta}")
                        self.store_var(name, src_reg="x1", line=expr.line, col=expr.col)
                    else:
                        self.emit("    mov w1, w0")
                        self.emit(f"    {op} w1, w1, #1")
                        self.store_var(name, src_reg="w1", line=expr.line, col=expr.col)
                return
            # Non-Identifier target: MemberAccess, ArrayAccess, pointer deref
            target_type = self.get_expr_type(expr.operand)
            is_pointer = self.is_pointer_type(target_type)
            delta = self.element_size(target_type) if is_pointer else 1
            wide = is_pointer or self.is_wide_scalar(target_type)
            self.gen_expr(expr.operand)
            op = "add" if expr.op == "++" else "sub"
            if expr.prefix:
                if wide:
                    self.emit(f"    {op} x0, x0, #{delta}")
                else:
                    self.emit(f"    {op} w0, w0, #1")
                if self.is_byte_type(target_type):
                    self.emit("    and w0, w0, #0xFF")
                elif target_type is not None and target_type.base == "short" and not target_type.is_pointer():
                    self.emit("    and w0, w0, #0xFFFF")
                self.push_x0()
                self.gen_lvalue_addr(expr.operand)
                self.pop_reg("x1")
                if is_pointer or wide:
                    self.emit("    str x1, [x0]")
                    self.emit("    mov x0, x1")
                elif self.is_byte_type(target_type):
                    self.emit("    strb w1, [x0]")
                    self.emit("    mov w0, w1")
                elif target_type is not None and target_type.base == "short" and not target_type.is_pointer():
                    self.emit("    strh w1, [x0]")
                    self.emit("    mov w0, w1")
                else:
                    self.emit("    str w1, [x0]")
                    self.emit("    mov w0, w1")
            else:
                # Post: save original, compute new, store, return original
                self.push_x0()
                self.push_x0()
                self.gen_lvalue_addr(expr.operand)
                # x0 = addr, stack: [orig_val, orig_val]
                self.emit("    mov x9, x0")  # x9 = addr
                self.pop_reg("x1")           # x1 = new value to compute
                if wide:
                    self.emit(f"    {op} x1, x1, #{delta}")
                    self.emit("    str x1, [x9]")
                elif self.is_byte_type(target_type):
                    self.emit(f"    {op} w1, w1, #1")
                    self.emit("    and w1, w1, #0xFF")
                    self.emit("    strb w1, [x9]")
                elif target_type is not None and target_type.base == "short" and not target_type.is_pointer():
                    self.emit(f"    {op} w1, w1, #1")
                    self.emit("    and w1, w1, #0xFFFF")
                    self.emit("    strh w1, [x9]")
                else:
                    self.emit(f"    {op} w1, w1, #1")
                    self.emit("    str w1, [x9]")
                self.pop_reg("x0")  # return original value
            return

        self.gen_expr(expr.operand)
        operand_type = self.get_expr_type(expr.operand)
        wide = self.is_wide_scalar(operand_type) or self.is_wide_scalar(self.get_expr_type(expr))

        if self.is_fp_type(operand_type):
            if expr.op == "-":
                self.emit("    fneg d0, d0")
            elif expr.op == "!":
                self.emit("    fcmp d0, #0.0")
                self.emit("    cset w0, eq")
            elif expr.op == "&":
                self.gen_lvalue_addr(expr.operand)
            else:
                self.error(f"unary operator '{expr.op}' is not supported for floating-point on arm64-apple-darwin", expr.line, expr.col)
            return

        if expr.op == "-":
            self.emit("    neg x0, x0" if wide else "    neg w0, w0")
        elif expr.op == "!":
            is_64bit = wide or self.is_pointer_type(operand_type)
            self.emit("    cmp x0, #0" if is_64bit else "    cmp w0, #0")
            self.emit("    cset w0, eq")
        elif expr.op == "~":
            self.emit("    mvn x0, x0" if wide else "    mvn w0, w0")
        elif expr.op == "&":
            self.gen_lvalue_addr(expr.operand)
        elif expr.op == "*":
            if operand_type is not None and operand_type.base == "char" and operand_type.pointer_depth == 1:
                self.emit("    ldrb w0, [x0]" if operand_type.is_unsigned else "    ldrsb w0, [x0]")
            elif operand_type is not None and operand_type.base == "short" and operand_type.pointer_depth == 1:
                self.emit("    ldrh w0, [x0]" if operand_type.is_unsigned else "    ldrsh w0, [x0]")
            elif operand_type is not None and operand_type.pointer_depth > 1:
                self.emit("    ldr x0, [x0]")
            elif operand_type is not None and operand_type.is_struct() and operand_type.pointer_depth == 1:
                return
            elif operand_type is not None and self.is_wide_scalar(self.element_type(operand_type)):
                self.emit("    ldr x0, [x0]")
            else:
                self.emit("    ldr w0, [x0]")
        else:
            self.error(f"unary operator '{expr.op}' is not yet supported on arm64-apple-darwin", expr.line, expr.col)

    def gen_ternary(self, expr: TernaryOp):
        false_label = self.new_label("ternfalse")
        end_label = self.new_label("ternend")
        self.gen_condition(expr.condition)
        self.emit(f"    cbz w0, {false_label}")
        self.gen_expr(expr.true_expr)
        self.emit(f"    b {end_label}")
        self.label(false_label)
        self.gen_expr(expr.false_expr)
        self.label(end_label)

    def gen_lvalue_addr(self, expr: Expr):
        if isinstance(expr, Identifier):
            if expr.name in self.locals:
                if expr.name in self.vla_ptr_locals:
                    self.emit_local_load("ldur", "x0", self.locals[expr.name])
                else:
                    self.emit(f"    sub x0, x29, #{self.locals[expr.name]}")
                return
            if expr.name in self.static_locals:
                self.emit_symbol_addr(self.static_locals[expr.name])
                return
            if expr.name in self.globals:
                g = self.globals[expr.name]
                is_extern_global = g.type_spec is not None and g.type_spec.is_extern
                if is_extern_global:
                    self.emit(f"    adrp x0, {self.mangle(expr.name)}@GOTPAGE")
                    self.emit(f"    ldr x0, [x0, {self.mangle(expr.name)}@GOTPAGEOFF]")
                else:
                    self.emit_symbol_addr(self.mangle(expr.name))
                return
            if expr.name in self.functions:
                func_decl = self.functions.get(expr.name)
                if func_decl is not None and func_decl.body is not None:
                    # Locally defined function — ADRP+ADD ok
                    self.emit_symbol_addr(self.mangle(expr.name))
                else:
                    # External function — use GOT indirection
                    self.emit_extern_func_addr(self.mangle(expr.name))
                return
            self.error(f"undefined variable '{expr.name}'", expr.line, expr.col)
        elif isinstance(expr, UnaryOp) and expr.op == "*":
            self.gen_expr(expr.operand)
            return
        elif isinstance(expr, ArrayAccess):
            self.gen_array_addr(expr)
            return
        elif isinstance(expr, MemberAccess):
            self.gen_member_addr(expr)
            return
        elif isinstance(expr, GenericSelection):
            selected = self._resolve_generic(expr)
            if selected is not None:
                self.gen_lvalue_addr(selected)
                return
        self.error("expression is not an lvalue", expr.line, expr.col)

    def _resolve_generic(self, expr: GenericSelection):
        """Select the matching association expr from a _Generic expression."""
        ct = self.get_expr_type(expr.controlling)
        selected = None
        default_expr = None
        for assoc in expr.associations:
            if assoc.type_spec is None:
                default_expr = assoc.expr
            elif ct is not None and self._generic_types_match(ct, assoc.type_spec):
                selected = assoc.expr
                break
        return selected if selected is not None else default_expr

    def _generic_types_match(self, controlling, assoc):
        ctrl_const = controlling.is_const if controlling.pointer_depth > 0 else False
        if controlling.pointer_depth != assoc.pointer_depth:
            return False
        if controlling.is_unsigned != assoc.is_unsigned:
            return False
        if controlling.base != assoc.base:
            return False
        if ctrl_const != assoc.is_const:
            return False
        return True

    def _gen_generic_selection(self, expr: GenericSelection):
        selected = self._resolve_generic(expr)
        if selected is not None:
            self.gen_expr(selected)

    def gen_array_addr(self, expr: ArrayAccess):
        if isinstance(expr.array, Identifier):
            array_type = self.get_var_type(expr.array.name)
            if array_type is not None and (array_type.is_array() or array_type.is_ptr_array):
                self.gen_lvalue_addr(expr.array)
            else:
                self.gen_expr(expr.array)
        else:
            array_type = self.get_expr_type(expr.array)
            if array_type is not None and (array_type.is_array() or array_type.is_ptr_array):
                self.gen_lvalue_addr(expr.array)
            else:
                self.gen_expr(expr.array)

        self.push_x0()
        self.gen_expr(expr.index)
        self.emit("    sxtw x0, w0")
        self.pop_reg("x1")

        elem_type = self.element_type(array_type)

        if self._has_vla_dim(elem_type):
            # VLA element: compute stride at runtime.
            # x0=index, x1=base. Save both, compute size into x0, then multiply.
            self.emit("    str x0, [sp, #-16]!")  # push index
            self.emit("    str x1, [sp, #-16]!")  # push base
            self._emit_runtime_size(elem_type)     # x0 = stride (may use stack/x1)
            self.pop_reg("x1")                     # restore base
            self.pop_reg("x2")                     # restore index
            self.emit("    mul x0, x2, x0")        # x0 = index * stride
        else:
            elem_size = self.total_size(elem_type)
            if elem_size != 1:
                self.emit(f"    mov x2, #{elem_size}")
                self.emit("    mul x0, x0, x2")
        self.emit("    add x0, x1, x0")

    def gen_array_access(self, expr: ArrayAccess):
        self.gen_array_addr(expr)
        result_type = self.get_expr_type(expr)
        if self.is_array_type(result_type):
            return  # result is an array subtype; address stays in x0
        if result_type is not None and result_type.is_struct() and not result_type.is_pointer():
            return  # struct element: keep address in x0
        if self.is_byte_type(result_type):
            self.emit("    ldrb w0, [x0]" if result_type.is_unsigned else "    ldrsb w0, [x0]")
        elif result_type is not None and result_type.base == "short" and not result_type.is_pointer():
            self.emit("    ldrh w0, [x0]" if result_type.is_unsigned else "    ldrsh w0, [x0]")
        elif self.is_wide_scalar(result_type):
            self.emit("    ldr x0, [x0]")
        elif result_type is not None and result_type.is_pointer():
            self.emit("    ldr x0, [x0]")
        else:
            self.emit("    ldr w0, [x0]")

    def gen_member_addr(self, expr: MemberAccess):
        obj_type = self.get_expr_type(expr.obj)
        if obj_type is None:
            self.error("could not resolve member base type", expr.line, expr.col)
        struct_type = self.clone_type(obj_type, pointer_depth=obj_type.pointer_depth - 1) if expr.arrow else obj_type
        if struct_type is None or struct_type.struct_def is None:
            self.error("member access requires a struct type on arm64-apple-darwin", expr.line, expr.col)

        if expr.arrow:
            self.gen_expr(expr.obj)
        else:
            self.gen_lvalue_addr(expr.obj)

        offset = struct_type.struct_def.member_offset(expr.member)
        if offset is None:
            self.error(f"unknown member '{expr.member}'", expr.line, expr.col)
        self.emit(f"    add x0, x0, #{offset}")

    def gen_member_access(self, expr: MemberAccess):
        obj_type = self.get_expr_type(expr.obj)
        sdef = obj_type.struct_def if obj_type else None
        if sdef:
            bf = sdef.bitfield_info(expr.member, self.target)
            if bf:
                unit_off, unit_size, bit_start, bit_width = bf
                self.gen_member_addr(expr)  # address of the storage unit
                if unit_size == 1:
                    self.emit("    ldrb w0, [x0]")
                elif unit_size == 2:
                    self.emit("    ldrh w0, [x0]")
                elif unit_size == 8:
                    self.emit("    ldr x0, [x0]")
                else:
                    self.emit("    ldr w0, [x0]")
                if bit_start > 0:
                    self.emit(f"    lsr {'x0' if unit_size == 8 else 'w0'}, {'x0' if unit_size == 8 else 'w0'}, #{bit_start}")
                mask = (1 << bit_width) - 1
                self.emit(f"    and w0, w0, #{mask}")
                return
        self.gen_member_addr(expr)
        member_type = self.get_expr_type(expr)
        if member_type is not None and member_type.is_struct() and not member_type.is_pointer():
            return
        if member_type is not None and (member_type.is_array() or member_type.is_ptr_array):
            return
        if self.is_fp_type(member_type):
            if member_type.base == "float":
                self.emit("    ldr s0, [x0]")
                self.emit("    fcvt d0, s0")
            else:
                self.emit("    ldr d0, [x0]")
        elif self.is_byte_type(member_type):
            self.emit("    ldrb w0, [x0]" if (member_type.is_unsigned or member_type.base == "_Bool") else "    ldrsb w0, [x0]")
        elif member_type is not None and member_type.base == "short" and not member_type.is_pointer():
            self.emit("    ldrh w0, [x0]" if member_type.is_unsigned else "    ldrsh w0, [x0]")
        elif self.is_wide_scalar(member_type):
            self.emit("    ldr x0, [x0]")
        elif member_type is not None and member_type.is_pointer():
            self.emit("    ldr x0, [x0]")
        else:
            self.emit("    ldr w0, [x0]")

    def sizeof_value(self, expr: SizeofExpr) -> int:
        if expr.is_type:
            type_spec = expr.operand
        else:
            type_spec = self.get_expr_type(expr.operand)

        if type_spec is None:
            self.error("arm64-apple-darwin could not resolve sizeof operand type", expr.line, expr.col)

        return self.total_size(type_spec)

    def gen_sizeof(self, expr: SizeofExpr):
        self.emit_int_constant(self.sizeof_value(expr), "w0")

    def alignof_value(self, expr: AlignofExpr) -> int:
        if expr.is_type:
            type_spec = expr.operand
        else:
            type_spec = self.get_expr_type(expr.operand)
        if type_spec is None:
            self.error("arm64-apple-darwin could not resolve alignof operand type", expr.line, expr.col)
        if type_spec.is_struct() and not type_spec.is_pointer():
            return type_spec.struct_def.alignment(self.target)
        size = type_spec.size_bytes(self.target)
        if size <= 0:
            return 1
        return min(size, self.target.layout.max_scalar_align)

    def gen_alignof(self, expr: AlignofExpr):
        self.emit_int_constant(self.alignof_value(expr), "w0")

    def gen_cast(self, expr: CastExpr):
        # Compound literal: (Type){...} — allocate a temporary on the stack
        if isinstance(expr.operand, InitList):
            target = expr.target_type
            if target is not None:
                size = self.total_size(target)
                alloc = (size + 15) & ~15
                # Allocate temp space on stack dynamically
                self.emit(f"    sub sp, sp, #{alloc}")
                self.emit(f"    mov x9, sp")
                if target.is_struct() and not target.is_pointer():
                    struct_def = target.struct_def
                    if struct_def is not None:
                        for i, item in enumerate(expr.operand.items):
                            if i >= len(struct_def.members):
                                break
                            member = struct_def.members[i]
                            moff = struct_def.member_offset(member.name) or 0
                            self.gen_expr(item.value)
                            msz = self.total_size(member.type_spec) if member.type_spec else 4
                            if msz <= 1:
                                self.emit(f"    strb w0, [x9, #{moff}]")
                            elif msz <= 2:
                                self.emit(f"    strh w0, [x9, #{moff}]")
                            elif msz <= 4:
                                self.emit(f"    str w0, [x9, #{moff}]")
                            else:
                                self.emit(f"    str x0, [x9, #{moff}]")
                    # Return struct by value if ≤ 16 bytes
                    if size <= 8:
                        self.emit("    ldr x0, [x9]")
                    elif size <= 16:
                        self.emit("    ldr x0, [x9]")
                        self.emit("    ldr x1, [x9, #8]")
                    self.emit(f"    add sp, sp, #{alloc}")
                    return
                elif self.is_array_type(target):
                    # For array compound literals, return address
                    elem_type = self.element_type(target)
                    elem_sz = self.total_size(elem_type)
                    for i, item in enumerate(expr.operand.items):
                        self.gen_expr(item.value)
                        off = i * elem_sz
                        if elem_sz <= 1:
                            self.emit(f"    strb w0, [x9, #{off}]")
                        elif elem_sz <= 2:
                            self.emit(f"    strh w0, [x9, #{off}]")
                        elif elem_sz <= 4:
                            self.emit(f"    str w0, [x9, #{off}]")
                        else:
                            self.emit(f"    str x0, [x9, #{off}]")
                    self.emit("    mov x0, x9")
                    # Note: sp is NOT restored here — array pointer stays valid
                    return
                else:
                    self.emit(f"    add sp, sp, #{alloc}")
            # Fallback: evaluate first element
            if expr.operand.items:
                self.gen_expr(expr.operand.items[0].value)
            return
        self.gen_expr(expr.operand)
        target = expr.target_type
        if target is None:
            return
        source = self.get_expr_type(expr.operand)
        src_fp = self.is_fp_type(source)
        tgt_fp = self.is_fp_type(target)
        if tgt_fp:
            if src_fp:
                if source.base == "float" and target.base != "float":
                    pass  # already d0 (float was expanded)
                elif source.base != "float" and target.base == "float":
                    self.emit("    fcvt s0, d0")
                    self.emit("    fcvt d0, s0")
                # long double == double, no-op
            else:
                # int → fp
                if self.is_wide_scalar(source) or self.is_pointer_type(source):
                    if source is not None and source.is_unsigned:
                        self.emit("    ucvtf d0, x0")
                    else:
                        self.emit("    scvtf d0, x0")
                elif source is not None and source.is_unsigned:
                    self.emit("    ucvtf d0, w0")
                else:
                    self.emit("    scvtf d0, w0")
            return
        if src_fp:
            # fp → int
            if target.is_pointer():
                self.emit("    fcvtzs x0, d0")
                return
            if target.size_bytes(self.target) > 4:
                if target.is_unsigned:
                    self.emit("    fcvtzu x0, d0")
                else:
                    self.emit("    fcvtzs x0, d0")
            else:
                if target.is_unsigned:
                    self.emit("    fcvtzu w0, d0")
                else:
                    self.emit("    fcvtzs w0, d0")
            return
        if target.is_pointer():
            return
        size = target.size_bytes(self.target)
        if size > 4:
            if source is not None and not source.is_pointer() and source.size_bytes(self.target) <= 4:
                if source.is_unsigned:
                    self.emit("    uxtw x0, w0")
                else:
                    src_size = source.size_bytes(self.target)
                    if src_size <= 1:
                        self.emit("    sxtb w0, w0")
                    elif src_size <= 2:
                        self.emit("    sxth w0, w0")
                    self.emit("    sxtw x0, w0")
            return
        if size <= 1:
            if target.is_unsigned:
                self.emit("    and w0, w0, #0xff")
            else:
                self.emit("    sxtb w0, w0")
        elif size <= 2:
            if target.is_unsigned:
                self.emit("    and w0, w0, #0xffff")
            else:
                self.emit("    sxth w0, w0")
        elif size <= 4:
            self.emit("    mov w0, w0")

    def gen_comma(self, expr: CommaExpr):
        for subexpr in expr.exprs:
            self.gen_expr(subexpr)

    def gen_string_literal(self, expr: StringLiteral):
        label = self.string_label(expr.value)
        self.emit(f"    adrp x0, {label}@PAGE")
        self.emit(f"    add x0, x0, {label}@PAGEOFF")

    def gen_func_call(self, expr: FuncCall):
        # Handle va builtins before regular call dispatch
        if isinstance(expr.name, Identifier):
            fn = expr.name.name
            if fn == "__builtin_va_start":
                self._gen_va_start(expr)
                return
            if fn in ("__builtin_va_end", "__builtin_va_copy"):
                if fn == "__builtin_va_copy" and len(expr.args) >= 2:
                    self._gen_va_copy(expr)
                return
            if fn in ("__builtin_bswap16", "__builtin_bswap32", "__builtin_bswap64"):
                self.gen_expr(expr.args[0])
                if fn == "__builtin_bswap16":
                    self.emit("    rev16 w0, w0")
                    self.emit("    and w0, w0, #0xffff")
                elif fn == "__builtin_bswap32":
                    self.emit("    rev w0, w0")
                else:
                    self.emit("    rev x0, x0")
                return
            if fn == "__builtin_alloca":
                self.gen_expr(expr.args[0])
                self.emit("    add x0, x0, #15")
                self.emit("    and x0, x0, #-16")
                self.emit("    sub sp, sp, x0")
                self.emit("    mov x0, sp")
                return
            if fn == "__builtin_constant_p":
                arg = expr.args[0] if expr.args else None
                from jmcc.ast_nodes import IntLiteral as _IL, FloatLiteral as _FL, CharLiteral as _CL, StringLiteral as _SL
                if isinstance(arg, (_IL, _FL, _CL, _SL)):
                    self.emit("    mov w0, #1")
                else:
                    self.emit("    mov w0, #0")
                return

            if fn in ("__builtin_add_overflow", "__builtin_sub_overflow", "__builtin_mul_overflow"):
                # __builtin_add_overflow(a, b, &result) -> sets *result=a+b, returns 1 if overflow
                if len(expr.args) >= 3:
                    self.gen_expr(expr.args[0])
                    self.push_x0()
                    self.gen_expr(expr.args[1])
                    self.pop_reg("x1")
                    # x1=a, x0=b; detect 64-bit operands
                    arg0_type = self.get_expr_type(expr.args[0])
                    arg1_type = self.get_expr_type(expr.args[1])
                    wide = self.is_wide_scalar(arg0_type) or self.is_wide_scalar(arg1_type)
                    if fn == "__builtin_add_overflow":
                        self.emit("    adds x2, x1, x0" if wide else "    adds w2, w1, w0")
                    elif fn == "__builtin_sub_overflow":
                        self.emit("    subs x2, x1, x0" if wide else "    subs w2, w1, w0")
                    else:
                        if wide:
                            # 64-bit mul overflow: use umulh/smulh trick
                            self.emit("    mul x2, x1, x0")
                            self.emit("    smulh x3, x1, x0")
                            self.emit("    asr x4, x2, #63")
                            self.emit("    cmp x3, x4")
                            self.emit("    cset w0, ne")
                        else:
                            self.emit("    smull x2, w1, w0")
                            self.emit("    sxtw x3, w2")
                            self.emit("    cmp x2, x3")
                            self.emit("    cset w0, ne")
                        # store result
                        self.gen_expr(expr.args[2])
                        self.emit("    str x2, [x0]" if wide else "    str w2, [x0]")
                        return
                    self.emit("    cset w0, vs")
                    # store result via pointer arg
                    self.push_x0()  # save overflow flag
                    self.gen_expr(expr.args[2])
                    self.emit("    str x2, [x0]" if wide else "    str w2, [x0]")
                    self.pop_reg("x0")  # restore overflow flag
                else:
                    self.emit("    mov w0, #0")
                return

        direct_name = expr.name.name if isinstance(expr.name, Identifier) and expr.name.name in self.functions else None
        func_decl = self.functions.get(direct_name) if direct_name is not None else None
        fixed_arg_count = len(func_decl.params) if func_decl is not None else len(expr.args)
        # Apple arm64: variadic args go on the stack; fixed args go in x0-x7 / d0-d7
        stack_varargs = func_decl is not None and func_decl.is_variadic and len(expr.args) > fixed_arg_count

        # Only limit fixed args to 8; variadic extras go on the stack
        max_reg_args = fixed_arg_count if stack_varargs else len(expr.args)
        if max_reg_args > len(self.ARG_REGS_64):
            self.error("more than 8 register call arguments are not yet supported on arm64-apple-darwin", expr.line, expr.col)
        stack_bytes = 0
        temp_arg_bytes = len(expr.args) * 16

        if direct_name is None:
            self.gen_expr(expr.name)
            self.push_x0()

        # Evaluate all args, pushing them on the stack.
        # For struct ≤ 8 bytes: load the bytes (ldr x0/w0) before pushing.
        # For struct 9-16 bytes: push address + a sentinel so pop knows to use 2 regs.
        # FP args spill as d0.
        arg_types = []
        for arg in expr.args:
            arg_types.append(self.get_expr_type(arg))
            a_type = arg_types[-1]
            self.gen_expr(arg)
            if self.is_fp_type(a_type):
                self.push_d0()
            elif (a_type is not None and a_type.is_struct() and not a_type.is_pointer() and not self.is_array_type(a_type)):
                struct_size = a_type.struct_def.size_bytes(self.target)
                if self._is_struct_by_reg_value(arg):
                    # gen_expr already put bytes in x0[/x1]
                    if struct_size > 8:
                        # push x1 first (high), then x0 (low) so pop order is: x0 low, x1 high
                        self.emit("    str x1, [sp, #-16]!")
                    self.push_x0()
                else:
                    # gen_expr returned address; load bytes
                    if struct_size <= 4:
                        self.emit("    ldr w0, [x0]")
                        self.push_x0()
                    elif struct_size <= 8:
                        self.emit("    ldr x0, [x0]")
                        self.push_x0()
                    elif struct_size <= 16:
                        self.emit("    mov x9, x0")
                        self.emit("    ldr x0, [x9]")
                        rem = struct_size - 8
                        self.emit("    ldr w1, [x9, #8]" if rem <= 4 else "    ldr x1, [x9, #8]")
                        self.emit("    str x1, [sp, #-16]!")  # push high bytes
                        self.push_x0()                        # push low bytes
                    else:
                        self.push_x0()  # pass address for large structs
            else:
                self.push_x0()

        if stack_varargs:
            stack_count = len(expr.args) - fixed_arg_count
            stack_bytes = (stack_count * 8 + 15) & ~15
            self.emit("    mov x10, sp")
            self.emit(f"    sub sp, sp, #{stack_bytes}")
            # Copy variadic args to stack slots [sp+0], [sp+8], ...
            for index in range(len(expr.args) - 1, fixed_arg_count - 1, -1):
                offset = (len(expr.args) - 1 - index) * 16
                self.emit(f"    ldr x9, [x10, #{offset}]")
                self.emit(f"    str x9, [sp, #{(index - fixed_arg_count) * 8}]")
            # Load fixed args into registers
            for index in range(fixed_arg_count - 1, -1, -1):
                offset = (len(expr.args) - 1 - index) * 16
                a_type = arg_types[index] if index < len(arg_types) else None
                if self.is_fp_type(a_type):
                    self.emit(f"    ldr d{index}, [x10, #{offset}]")
                else:
                    self.emit(f"    ldr {self.ARG_REGS_64[index]}, [x10, #{offset}]")
        else:
            # Non-variadic: pop args in reverse into x0-x7 / d0-d7.
            # reg_assigns is a list of tuples ('fp', idx), ('int', idx), or ('struct2', idx)
            int_idx = 0
            fp_idx = 0
            reg_assigns = []
            for a_type in arg_types:
                if self.is_fp_type(a_type):
                    reg_assigns.append(('fp', fp_idx))
                    fp_idx += 1
                elif (a_type is not None and a_type.is_struct() and not a_type.is_pointer()
                      and not self.is_array_type(a_type)
                      and a_type.struct_def.size_bytes(self.target) > 8):
                    # 9-16 byte struct occupies 2 x-registers
                    reg_assigns.append(('struct2', int_idx))
                    int_idx += 2
                else:
                    reg_assigns.append(('int', int_idx))
                    int_idx += 1
            for index in range(len(expr.args) - 1, -1, -1):
                kind, idx = reg_assigns[index]
                if kind == 'fp':
                    self.pop_d0(f"d{idx}")
                elif kind == 'struct2':
                    # low bytes in x{idx}, high bytes in x{idx+1}
                    self.pop_reg(self.ARG_REGS_64[idx])         # pop low (x0 first)
                    self.pop_reg(self.ARG_REGS_64[idx + 1])     # pop high (x1)
                else:
                    self.pop_reg(self.ARG_REGS_64[idx])

        if direct_name is not None:
            self.emit(f"    bl {self.mangle(direct_name)}")
        else:
            self.pop_reg("x16")
            self.emit("    blr x16")
        if stack_bytes:
            self.emit(f"    add sp, sp, #{stack_bytes + temp_arg_bytes}")

    def _gen_va_start(self, expr: FuncCall):
        """arm64 Apple Darwin va_start: ap = (char*)(x29 + 16)
        x29 = frame pointer (set after stp x29/x30), so x29+16 is where caller stored variadic args.
        """
        if not expr.args:
            return
        ap_arg = expr.args[0]
        # Compute address of first variadic arg: x29 + 16
        self.emit("    add x0, x29, #16")
        # Store into ap (which is a char* local)
        self.gen_lvalue_addr(ap_arg)
        self.emit("    mov x1, x0")         # x1 = &ap
        self.emit("    add x0, x29, #16")   # x0 = first variadic arg address
        self.emit("    str x0, [x1]")       # *(&ap) = address

    def _gen_va_copy(self, expr: FuncCall):
        """va_copy(dest, src): dest = src (both are char*)."""
        self.gen_lvalue_addr(expr.args[1])  # x0 = &src
        self.emit("    ldr x1, [x0]")       # x1 = src value
        self.gen_lvalue_addr(expr.args[0])  # x0 = &dest
        self.emit("    str x1, [x0]")       # *dest = src value

    def _gen_builtin_va_arg(self, expr: BuiltinVaArg):
        """arm64 Apple Darwin va_arg: load from *ap and advance ap by 8."""
        self.gen_expr(expr.ap)              # x0 = ap value (char* pointer)
        self.emit("    mov x8, x0")         # x8 = current ap
        self.emit("    add x9, x8, #8")     # x9 = ap + 8
        self.gen_lvalue_addr(expr.ap)       # x0 = &ap
        self.emit("    str x9, [x0]")       # *(&ap) = ap + 8
        target_type = expr.target_type
        size = target_type.size_bytes(self.target) if target_type else 8
        if self.is_fp_type(target_type):
            if target_type is not None and target_type.base == "float":
                self.emit("    ldr s0, [x8]")
                self.emit("    fcvt d0, s0")
            else:
                self.emit("    ldr d0, [x8]")
        elif size <= 1:
            self.emit("    ldrb w0, [x8]")
        elif size <= 2:
            self.emit("    ldrh w0, [x8]")
        elif size <= 4:
            self.emit("    ldr w0, [x8]")
        else:
            self.emit("    ldr x0, [x8]")
