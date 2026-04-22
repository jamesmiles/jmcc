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
    StatementExpr,
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
        self.all_static_locals: Dict[str, str] = {}  # persists across functions: name -> label
        self.all_static_local_types: Dict[str, object] = {}  # persists across functions: name -> TypeSpec
        self.globals: Dict[str, GlobalVarDecl] = {}
        self.functions: Dict[str, FuncDecl] = {}
        self.string_literals: Dict[str, str] = {}
        self.wide_string_literals: Dict[str, str] = {}  # wide (wchar_t) string pool
        self.stack_size = 0
        self.return_label: Optional[str] = None
        self.current_func: Optional[FuncDecl] = None
        self.func_is_variadic: bool = False
        self.break_labels: List[str] = []
        self.continue_labels: List[str] = []
        self.float_literals: Dict[tuple, str] = {}  # (bits, size) -> label
        self.vla_ptr_locals: set = set()  # locals whose slot holds a VLA base pointer
        self.pending_compound_lits: list = []  # (label, type_spec, init, line, col) deferred global compound literals

    def error(self, msg, line=0, col=0):
        raise CodeGenError(msg, line=line, col=col)

    def emit(self, line: str):
        self.output.append(line)

    # ── large-immediate helpers ───────────────────────────────────────────────

    def emit_large_imm(self, reg: str, n: int):
        """Load an arbitrary non-negative integer into reg using movz/movk."""
        n = int(n)
        chunks = [(n >> s) & 0xFFFF for s in (0, 16, 32, 48)]
        first = True
        for shift, val in zip((0, 16, 32, 48), chunks):
            if not first and val == 0:
                continue
            suffix = f", lsl #{shift}" if shift else ""
            if first:
                self.emit(f"    movz {reg}, #{val}{suffix}")
                first = False
            else:
                self.emit(f"    movk {reg}, #{val}{suffix}")

    def emit_sp_sub(self, n: int):
        """sub sp, sp, #n — split into <=4095 chunks (arm64 imm12 constraint)."""
        while n > 0:
            chunk = min(n, 4095)
            self.emit(f"    sub sp, sp, #{chunk}")
            n -= chunk

    def emit_sp_add(self, n: int):
        """add sp, sp, #n — split into <=4095 chunks (arm64 imm12 constraint)."""
        while n > 0:
            chunk = min(n, 4095)
            self.emit(f"    add sp, sp, #{chunk}")
            n -= chunk

    def emit_sub_reg_x29(self, reg: str, n: int):
        """sub reg, x29, #n — use scratch x9 for n > 4095."""
        if n <= 4095:
            self.emit(f"    sub {reg}, x29, #{n}")
        else:
            self.emit_large_imm("x9", n)
            self.emit(f"    sub {reg}, x29, x9")

    def emit_add_reg_imm(self, reg: str, n: int):
        """add reg, reg, #n — use scratch x9 for n > 4095."""
        if n <= 4095:
            self.emit(f"    add {reg}, {reg}, #{n}")
        else:
            self.emit_large_imm("x9", n)
            self.emit(f"    add {reg}, {reg}, x9")

    def emit_stur_zero(self, size_bytes: int, fp_neg_off: int):
        """Store zero at [x29, #-fp_neg_off]. Uses str+sub x9 for out-of-range offsets."""
        off = -fp_neg_off
        if -256 <= off <= 255:
            if size_bytes >= 8:
                self.emit(f"    stur xzr, [x29, #{off}]")
            elif size_bytes >= 4:
                self.emit(f"    stur wzr, [x29, #{off}]")
            else:
                self.emit(f"    sturb wzr, [x29, #{off}]")
        else:
            self.emit_sub_reg_x29("x9", fp_neg_off)
            if size_bytes >= 8:
                self.emit("    str xzr, [x9]")
            elif size_bytes >= 4:
                self.emit("    str wzr, [x9]")
            else:
                self.emit("    strb wzr, [x9]")

    def label(self, name: str):
        self.emit(f"{name}:")

    def new_label(self, prefix="L") -> str:
        self.label_count += 1
        return f"L{prefix}{self.label_count}"

    def mangle(self, name: str) -> str:
        # On macOS arm64, stdin/stdout/stderr are exposed as __stdinp/__stdoutp/__stderrp
        _MACOS_STDIO = {"stdin": "__stdinp", "stdout": "__stdoutp", "stderr": "__stderrp"}
        name = _MACOS_STDIO.get(name, name)
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

    def wide_string_label(self, value: str) -> str:
        if value not in self.wide_string_literals:
            self.wide_string_literals[value] = self.new_label("wstr")
        return self.wide_string_literals[value]

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
        if type_spec is not None and self.is_int128(type_spec):
            return 16
        return 8

    def get_var_type(self, name: str):
        if name in self.local_types:
            return self.local_types[name]
        if name in self.globals:
            return self.globals[name].type_spec
        if name in self.all_static_local_types:
            return self.all_static_local_types[name]
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
                "float": 4,
                "long": 8,
                "long long": 8,
                "double": 8,
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
        """Return True if type_spec contains any runtime (VLA) array dimension.
        None dims (unsized/flexible arrays) are not VLA dims."""
        if not self.is_array_type(type_spec):
            return False
        for dim in (type_spec.array_sizes or []):
            if dim is None:
                continue  # unsized array, not a VLA
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
            is_func_ptr=type_spec.is_func_ptr,
            func_ptr_native_depth=type_spec.func_ptr_native_depth,
        )

    def emit_symbol_addr(self, symbol: str, reg: str = "x0"):
        self.emit(f"    adrp {reg}, {symbol}@PAGE")
        self.emit(f"    add {reg}, {reg}, {symbol}@PAGEOFF")

    def emit_extern_func_addr(self, symbol: str, reg: str = "x0"):
        """Load address of an external function via GOT on macOS arm64."""
        self.emit(f"    adrp {reg}, {symbol}@GOTPAGE")
        self.emit(f"    ldr {reg}, [{reg}, {symbol}@GOTPAGEOFF]")

    def is_int128(self, type_spec) -> bool:
        return type_spec is not None and type_spec.base == "__int128" and not type_spec.is_pointer()

    def is_wide_scalar(self, type_spec) -> bool:
        return (type_spec is not None and not type_spec.is_pointer() and
                not self.is_array_type(type_spec) and type_spec.size_bytes(self.target) > 4
                and not self.is_int128(type_spec)
                and type_spec.base not in self._FP_BASES)

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
            # Compute max index accounting for designator_index and range designators
            max_idx = -1
            cur_idx = 0
            for item in init.items:
                if item.designator_index is not None:
                    cur_idx = item.designator_index
                end_idx = item.designator_end if item.designator_end is not None else cur_idx
                if end_idx > max_idx:
                    max_idx = end_idx
                cur_idx = end_idx + 1
            type_spec.array_sizes[0] = IntLiteral(value=max_idx + 1)
        elif isinstance(init, StringLiteral) and type_spec.base == "char":
            type_spec.array_sizes[0] = IntLiteral(value=len(init.value) + 1)
        elif isinstance(init, StringLiteral) and init.wide:
            # wchar_t[] = L"...": element count is len+1 (null terminator)
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
                func_decl = self.functions[expr.name]
                return TypeSpec(base=func_decl.return_type.base,
                                pointer_depth=func_decl.return_type.pointer_depth + 1,
                                is_unsigned=func_decl.return_type.is_unsigned)
            return None
        if isinstance(expr, IntLiteral):
            suffix_up = (expr.suffix or "").upper()
            is_u = "U" in suffix_up
            if "LL" in suffix_up:
                return TypeSpec(base="long long", is_unsigned=is_u)
            if "L" in suffix_up:
                return TypeSpec(base="long", is_unsigned=is_u)
            if self.literal_is_wide(expr):
                return TypeSpec(base="long long", is_unsigned=is_u)
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
                # ptr_array (e.g. int*[]): elements are pointers; dereference yields the element type
                if operand_type.is_ptr_array:
                    return self.element_type(operand_type)
                new_pd = max(operand_type.pointer_depth - 1, 0)
                # T(*)[n]: dereferencing pointer-to-array gives T[n], keep array_sizes
                if operand_type.pointer_depth > 0 and not operand_type.is_ptr_array and operand_type.array_sizes:
                    return self.clone_type(operand_type, pointer_depth=new_pd)
                return self.clone_type(operand_type, pointer_depth=new_pd, array_sizes=None)
            if expr.op in {"-", "~", "++", "--"} and operand_type is not None:
                # Integer promotion: char/short (signed or unsigned) → int
                if operand_type.base in {"char", "short"} and not operand_type.is_pointer():
                    return TypeSpec(base="int")
                return operand_type
            return TypeSpec(base="int")
        if isinstance(expr, BinaryOp):
            left_type = self.get_expr_type(expr.left)
            right_type = self.get_expr_type(expr.right)
            if expr.op in {"==", "!=", "<", "<=", ">", ">=", "&&", "||"}:
                return TypeSpec(base="int")
            if expr.op in {"<<", ">>"}:
                # C standard: result type is that of the promoted left operand
                # Integer promotion: char/short (signed or unsigned) → int
                if left_type is None:
                    return TypeSpec(base="int")
                _NARROW = {"char", "short"}
                if left_type.base in _NARROW:
                    return TypeSpec(base="int")
                return left_type
            if expr.op in {"+", "-"}:
                # ptr - ptr → ptrdiff_t (long = 64-bit signed on arm64)
                if (expr.op == "-" and left_type is not None and left_type.is_pointer()
                        and right_type is not None and right_type.is_pointer()):
                    return TypeSpec(base="long")
                if left_type is not None and left_type.is_pointer():
                    return left_type
                if right_type is not None and right_type.is_pointer():
                    return right_type
            # Propagate __int128 type
            if self.is_int128(left_type):
                return left_type
            if self.is_int128(right_type):
                return right_type
            if self.is_fp_type(left_type):
                return left_type
            if self.is_fp_type(right_type):
                return right_type
            # Usual arithmetic conversions: return the wider integer type
            return self._arith_result_type(left_type, right_type)
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
            # C usual arithmetic conversions: if either branch is fp, result is fp
            t_true = self.get_expr_type(expr.true_expr)
            t_false = self.get_expr_type(expr.false_expr)
            if self.is_fp_type(t_true):
                return t_true
            if self.is_fp_type(t_false):
                return t_false
            return t_true if t_true is not None else t_false
        if isinstance(expr, BuiltinVaArg):
            return expr.target_type
        if isinstance(expr, FuncCall):
            if isinstance(expr.name, Identifier):
                fn = expr.name.name
                if fn in ("__builtin_bswap64",):
                    return TypeSpec(base="long long", is_unsigned=True)
                if fn in ("__builtin_bswap32",):
                    return TypeSpec(base="int", is_unsigned=True)
                if fn in ("__builtin_bswap16",):
                    return TypeSpec(base="short", is_unsigned=True)
                func_decl = self.functions.get(fn)
                if func_decl is not None and func_decl.return_type is not None:
                    return func_decl.return_type
                # Indirect call via function pointer variable.
                # Parser may represent double (*term)() as double* (is_func_ptr=False),
                # so also handle the case where the variable is any pointer type.
                var_type = self.get_var_type(fn)
                if var_type is not None and (var_type.is_func_ptr or var_type.is_func_type):
                    return TypeSpec(base=var_type.base, is_unsigned=var_type.is_unsigned)
                if var_type is not None and var_type.is_pointer():
                    return TypeSpec(base=var_type.base, is_unsigned=var_type.is_unsigned)
            else:
                # Callee is an expression (e.g., function pointer returned by another call)
                callee_type = self.get_expr_type(expr.name)
                if callee_type is not None and (callee_type.is_func_ptr or callee_type.is_func_type):
                    return TypeSpec(
                        base=callee_type.base,
                        pointer_depth=max(callee_type.pointer_depth - 1, 0),
                        is_unsigned=callee_type.is_unsigned,
                        struct_def=callee_type.struct_def,
                    )
                if callee_type is not None and callee_type.pointer_depth > 0:
                    return TypeSpec(
                        base=callee_type.base,
                        pointer_depth=callee_type.pointer_depth - 1,
                        is_unsigned=callee_type.is_unsigned,
                        struct_def=callee_type.struct_def,
                    )
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
        self.typedef_map = {
            decl.name: decl
            for decl in program.declarations
            if isinstance(decl, TypedefDecl)
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

        # Emit deferred compound literals (from global &(type){init} initializers)
        for lbl, ts, init, line, col in self.pending_compound_lits:
            self.emit_global_decl(lbl, ts, init, line, col, exported=False)

        if self.string_literals:
            self.emit("")
            self.emit("    .data")
            for value, label in self.string_literals.items():
                self.emit("    .p2align 2")
                self.label(label)
                self.emit(f'    .asciz "{self.escape_string(value)}"')

        if self.wide_string_literals:
            self.emit("")
            self.emit("    .data")
            for value, label in self.wide_string_literals.items():
                self.emit("    .p2align 2")
                self.label(label)
                for cp in [ord(c) for c in value] + [0]:
                    self.emit(f"    .long {cp}")

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
            import struct as _struct
            size = type_spec.size_bytes(self.target)
            # If the target type is float/double, convert integer value to float bits
            if type_spec is not None and type_spec.base in ("float", "double") and not type_spec.is_pointer():
                if type_spec.base == "float":
                    bits = _struct.unpack('<I', _struct.pack('<f', float(init.value)))[0]
                    self.emit(f"    .long {bits}")
                else:
                    bits = _struct.unpack('<Q', _struct.pack('<d', float(init.value)))[0]
                    self.emit(f"    .quad {bits}")
                return
            if size <= 1:
                self.emit(f"    .byte {init.value & 0xff}")
            elif size <= 2:
                self.emit(f"    .short {init.value & 0xffff}")
            elif size <= 4:
                self.emit(f"    .long {init.value & 0xffffffff}")
            elif size <= 8:
                self.emit(f"    .quad {init.value & 0xffffffffffffffff}")
            else:
                # __int128: emit lo quad, then hi quad
                lo = init.value & 0xffffffffffffffff
                hi = (init.value >> 64) & 0xffffffffffffffff
                self.emit(f"    .quad {lo}")
                self.emit(f"    .quad {hi}")
            return

        if isinstance(init, StringLiteral) and type_spec is not None and type_spec.is_array() and type_spec.base == "char":
            self.emit(f'    .asciz "{self.escape_string(init.value)}"')
            return

        # wchar_t[] = L"...": emit each codepoint as .long (4 bytes)
        if isinstance(init, StringLiteral) and init.wide and type_spec is not None and type_spec.is_array():
            self.emit("    .p2align 2")
            for cp in [ord(c) for c in init.value] + [0]:
                self.emit(f"    .long {cp}")
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

    def _type_scalar_count(self, type_spec) -> int:
        """Count how many flat scalar initializer slots are needed for this type."""
        if self.is_array_type(type_spec):
            elem = self.element_type(type_spec)
            if type_spec.array_sizes and type_spec.array_sizes[0] is not None:
                dim = type_spec.array_sizes[0]
                if isinstance(dim, IntLiteral):
                    n = dim.value
                else:
                    n = self._global_const_int(dim)
                    if n is None:
                        return 1
            else:
                return 1
            return n * self._type_scalar_count(elem)
        elif type_spec.is_struct() and not type_spec.is_pointer() and type_spec.struct_def is not None:
            return sum(self._type_scalar_count(m.type_spec) for m in type_spec.struct_def.members)
        else:
            return 1

    def _adaptive_flat_count(self, member_type, flat_values: list, cursor: int) -> int:
        """Count how many flat items are consumed to initialize member_type.
        Handles string literals filling char arrays as 1 item, and recursively
        handles structs whose sub-members may include char arrays."""
        if cursor >= len(flat_values):
            return 0
        current = flat_values[cursor]
        # Braced or compound literal → always 1 item (covers the whole member)
        if (isinstance(current, InitList)
                or (isinstance(current, CastExpr) and isinstance(current.operand, InitList))):
            return 1
        # String literal for a char/u8 array → 1 item
        if (isinstance(current, StringLiteral)
                and self.is_array_type(member_type)
                and not member_type.is_pointer()):
            return 1
        # Array of scalars → each element takes _adaptive_flat_count items
        if self.is_array_type(member_type):
            elem = self.element_type(member_type)
            dim_spec = member_type.array_sizes[0] if member_type.array_sizes else None
            if dim_spec is not None:
                if isinstance(dim_spec, IntLiteral):
                    dim = dim_spec.value
                else:
                    dim = self._global_const_int(dim_spec) or 1
            else:
                dim = 1
            total = 0
            for _ in range(dim):
                total += self._adaptive_flat_count(elem, flat_values, cursor + total)
            return total
        # Struct → recurse into sub-members
        if (member_type.is_struct() and not member_type.is_pointer()
                and member_type.struct_def is not None):
            # If the current flat value is a struct-typed expression (not a scalar),
            # it represents the entire struct as one initializer item (e.g. 'ls' → struct S)
            if not isinstance(current, (IntLiteral, CharLiteral, FloatLiteral, StringLiteral)):
                expr_type = self.get_expr_type(current)
                if expr_type is not None and expr_type.is_struct() and not expr_type.is_pointer():
                    return 1
            total = 0
            for m in member_type.struct_def.members:
                total += self._adaptive_flat_count(m.type_spec, flat_values, cursor + total)
            return total
        # Scalar → 1 item
        return 1

    def _restructure_flat_init(self, type_spec, init, line: int, col: int):
        """Convert a flat InitList into properly nested InitList for a struct type.
        C allows struct arrays with no inner braces — values fill members in order.
        Brace-enclosed items ({...}) or compound literals are treated as consuming the
        entire corresponding member."""
        from jmcc.ast_nodes import InitItem as _II
        struct_def = type_spec.struct_def
        all_members = struct_def.members
        flat_values = [item.value for item in init.items]
        flat_cursor = 0
        new_items = []
        for member in all_members:
            if flat_cursor >= len(flat_values):
                break
            current = flat_values[flat_cursor]
            # A brace-enclosed or compound literal item consumes the whole member
            is_braced = (isinstance(current, InitList)
                         or (isinstance(current, CastExpr) and isinstance(current.operand, InitList)))
            if is_braced:
                new_items.append(_II(value=current))
                flat_cursor += 1
                continue
            count = self._adaptive_flat_count(member.type_spec, flat_values, flat_cursor)
            if count == 1:
                new_items.append(_II(value=flat_values[flat_cursor]))
                flat_cursor += 1
            else:
                sub_vals = flat_values[flat_cursor:flat_cursor + count]
                flat_cursor += count
                sub_init = InitList(items=[_II(value=v) for v in sub_vals], line=line, col=col)
                new_items.append(_II(value=sub_init))
        return InitList(items=new_items, line=line, col=col)

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

        # Detect flat init for array-of-structs (no inner braces per element).
        is_struct_elem = (elem_type.is_struct() and not elem_type.is_pointer()
                          and elem_type.struct_def is not None)
        # A CastExpr(InitList) is a compound literal — treat as a full element initializer, not scalar.
        _first_val = init.items[0].value if init.items else None
        _first_is_struct_init = (isinstance(_first_val, InitList)
                                 or (isinstance(_first_val, CastExpr) and isinstance(_first_val.operand, InitList)))
        has_flat_struct = (is_struct_elem and init.items
                           and not _first_is_struct_init
                           and len(init.items) > len(elem_type.struct_def.members))

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

        if has_flat_struct:
            # Flat init for array of structs: group scalars into per-element InitLists.
            from jmcc.ast_nodes import InitItem
            scalars_per = self._type_scalar_count(elem_type)
            flat_values = [item.value for item in init.items]
            # For implicit-size arrays (PT cases[] = {...}), count was set to len(init.items).
            # Recompute to the actual number of struct elements.
            if scalars_per > 0:
                count = len(flat_values) // scalars_per
            flat_cursor = 0
            for _ in range(count):
                if flat_cursor >= len(flat_values):
                    self.emit_global_value(elem_type, None, line, col)
                else:
                    sub_vals = flat_values[flat_cursor:flat_cursor + scalars_per]
                    flat_cursor += scalars_per
                    elem_init = InitList(items=[InitItem(value=v) for v in sub_vals], line=line, col=col)
                    self.emit_global_value(elem_type, elem_init, line, col)
            return

        # Build index-to-value map respecting designator_index and range designators
        init_map: dict = {}
        cur_idx = 0
        for item in init.items:
            if item.designator_index is not None:
                cur_idx = item.designator_index
            if item.designator_end is not None:
                for i in range(cur_idx, item.designator_end + 1):
                    init_map[i] = item.value
                cur_idx = item.designator_end + 1
            else:
                init_map[cur_idx] = item.value
                cur_idx += 1

        for index in range(count):
            item = init_map.get(index)
            self.emit_global_value(elem_type, item, line, col)

    def emit_global_struct_init(self, type_spec, value: 'InitList', line: int, col: int):
        struct_def = type_spec.struct_def
        total = struct_def.size_bytes(self.target)

        # For unions: emit only the first (or only initialized) member, then zero-pad to union size.
        if struct_def.is_union:
            # Find first named member (or first member if all anonymous)
            first_member = next((m for m in struct_def.members if m.name != ""), None)
            if first_member is None:
                first_member = struct_def.members[0] if struct_def.members else None
            # Check if any items use designators matching direct union members
            named_member_indices = {m.name: m for m in struct_def.members if m.name}
            # Check if designators refer to fields of an anonymous struct/union member
            designators_used = [item.designator for item in value.items if item.designator is not None]
            anon_member_match = None
            if designators_used and not any(d in named_member_indices for d in designators_used):
                # Check anonymous members' fields
                for m in struct_def.members:
                    if m.name == "" and m.type_spec.is_struct() and m.type_spec.struct_def is not None:
                        anon_fields = {f.name for f in m.type_spec.struct_def.members if f.name}
                        if all(d in anon_fields for d in designators_used):
                            anon_member_match = m
                            break
            if anon_member_match is not None:
                # Forward items as InitList for the anonymous struct
                self.emit_global_value(anon_member_match.type_spec, value, line, col)
                emitted = self.total_size(anon_member_match.type_spec)
                if total > emitted:
                    self.emit(f"    .zero {total - emitted}")
                return
            has_direct_designator = any(item.designator in named_member_indices for item in value.items if item.designator is not None)
            if has_direct_designator:
                # Named designators for top-level union members — find the last designated member
                target_member = None
                target_val = None
                for item in value.items:
                    if item.designator in named_member_indices:
                        target_member = named_member_indices[item.designator]
                        target_val = item.value
                if target_member is not None and target_val is not None:
                    self.emit_global_value(target_member.type_spec, target_val, line, col)
                    emitted = self.total_size(target_member.type_spec)
                else:
                    emitted = 0
            elif first_member is not None and value.items:
                # Use all items as the init for the first member (handles flat scalars for array/struct)
                if len(value.items) == 1:
                    first_val = value.items[0].value
                else:
                    from jmcc.ast_nodes import InitItem
                    first_val = InitList(items=list(value.items), line=line, col=col)
                self.emit_global_value(first_member.type_spec, first_val, line, col)
                emitted = self.total_size(first_member.type_spec)
            else:
                emitted = 0
            if total > emitted:
                self.emit(f"    .zero {total - emitted}")
            return

        current_offset = 0
        # Include ALL members (including anonymous union/struct with name=="")
        all_members = struct_def.members

        # Restructure flat (brace-elided) initializer if more items than members
        if len(value.items) > len(all_members):
            value = self._restructure_flat_init(type_spec, value, line, col)

        # Build index-based init_values list (handles anon unions positionally)
        init_values = [None] * len(all_members)
        # Named-members list for designator lookup (named members only, in order)
        named_member_indices = {m.name: j for j, m in enumerate(all_members) if m.name}
        positional_idx = 0
        for item in value.items:
            if item.designator is not None:
                j = named_member_indices.get(item.designator)
                if j is not None:
                    init_values[j] = item.value
                    positional_idx = j + 1
            else:
                # Skip positions already filled by designated initializers
                while positional_idx < len(all_members) and init_values[positional_idx] is not None:
                    positional_idx += 1
                if positional_idx < len(all_members):
                    init_values[positional_idx] = item.value
                    positional_idx += 1

        layout, _ = struct_def._layout_members(self.target)
        for i, member in enumerate(all_members):
            member_off = layout[i][0] if i < len(layout) else current_offset
            if member_off > current_offset:
                self.emit(f"    .zero {member_off - current_offset}")
                current_offset = member_off
            member_type = member.type_spec
            member_value = init_values[i]
            # Anonymous union/struct: emit as nested struct init
            if member.name == "" and member_type.is_struct() and not member_type.is_pointer() and member_type.struct_def is not None:
                size = member_type.struct_def.size_bytes(self.target)
                if member_value is None:
                    self.emit(f"    .zero {size}")
                elif isinstance(member_value, InitList):
                    self.emit_global_struct_init(member_type, member_value, line, col)
                else:
                    # Scalar value initializes first member of the anon union/struct
                    from jmcc.ast_nodes import InitItem as _InitItem, InitList as _InitList
                    dummy = _InitList(items=[_InitItem(value=member_value)], line=line, col=col)
                    self.emit_global_struct_init(member_type, dummy, line, col)
                current_offset += size
                continue
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
                    if not isinstance(member_value, InitList):
                        # Scalar initializes the first element of the array (brace elision)
                        from jmcc.ast_nodes import InitItem as _II
                        member_value = InitList(items=[_II(value=member_value)], line=line, col=col)
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
                # Convert to float/double bits if member is float/double type
                import struct as _struct
                if member_type.base in ("float", "double") and not member_type.is_pointer():
                    if member_type.base == "float":
                        bits = _struct.unpack('<I', _struct.pack('<f', float(intval)))[0]
                        self.emit(f"    .long {bits}")
                    else:
                        bits = _struct.unpack('<Q', _struct.pack('<d', float(intval)))[0]
                        self.emit(f"    .quad {bits}")
                elif size <= 1:
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
            elif (member_type.is_struct() and not member_type.is_pointer()
                  and isinstance(member_value, CastExpr) and isinstance(member_value.operand, InitList)):
                # Compound literal used to initialize a struct member: (struct S){...}
                self.emit_global_struct_init(member_type, member_value.operand, line, col)
                current_offset += member_type.struct_def.size_bytes(self.target)
            elif (member_type.is_struct() and not member_type.is_pointer()):
                # Brace elision: scalar/string used to init a struct — wrap in InitList
                from jmcc.ast_nodes import InitItem as _II
                dummy = InitList(items=[_II(value=member_value)], line=line, col=col)
                self.emit_global_struct_init(member_type, dummy, line, col)
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
                elif isinstance(member_value, FloatLiteral) or (
                        member_type.base in ("float", "double") and not member_type.is_pointer()
                        and self._global_const_float(member_value) is not None):
                    # Float/double member initializer (FloatLiteral or constant float expression)
                    import struct as _struct
                    if isinstance(member_value, FloatLiteral):
                        fval = member_value.value
                    else:
                        fval = self._global_const_float(member_value)
                    use_float = isinstance(member_value, FloatLiteral) and member_value.is_single
                    use_float = use_float or (not isinstance(member_value, FloatLiteral) and member_type.base == "float")
                    if member_type.base == "float" or (isinstance(member_value, FloatLiteral) and member_value.is_single):
                        bits = _struct.unpack('<I', _struct.pack('<f', fval))[0]
                        self.emit(f"    .long {bits}")
                    else:
                        bits = _struct.unpack('<Q', _struct.pack('<d', fval))[0]
                        self.emit(f"    .quad {bits}")
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
            # Handle {"string"}: char array initialized with a braced string literal
            if (type_spec.base == "char" and isinstance(value, InitList)
                    and len(value.items) == 1
                    and isinstance(value.items[0].value, StringLiteral)):
                value = value.items[0].value
                raw = value.value.encode("utf-8") + b"\0"
                limit = self.total_size(type_spec)
                raw = raw[:limit] + b"\0" * max(0, limit - len(raw))
                for byte in raw:
                    self.emit(f"    .byte {byte}")
                return
            # wchar_t[] = L"...": emit each codepoint as .long (4 bytes) + null terminator
            if isinstance(value, StringLiteral) and value.wide:
                codepoints = [ord(c) for c in value.value] + [0]
                for cp in codepoints:
                    self.emit(f"    .long {cp}")
                return
            if isinstance(value, InitList):
                self.emit_global_array_init(type_spec, value, line, col)
                return
        if type_spec is not None and type_spec.is_struct() and not type_spec.is_pointer():
            if value is None:
                self.emit(f"    .zero {self.total_size(type_spec)}")
                return
            # Unwrap compound literal: (struct S){...} → InitList
            if isinstance(value, CastExpr) and isinstance(value.operand, InitList):
                value = value.operand
            if not isinstance(value, InitList):
                # Implicit single-member struct init: wrap scalar in an InitList
                from jmcc.ast_nodes import InitItem
                value = InitList(items=[InitItem(value=value)], line=line, col=col)
            # Restructure flat (brace-elided) initializer if needed
            if (type_spec.struct_def is not None
                    and len(value.items) > len(type_spec.struct_def.members)):
                value = self._restructure_flat_init(type_spec, value, line, col)
            self.emit_global_struct_init(type_spec, value, line, col)
            return
        if value is None:
            self.emit(f"    .zero {self.total_size(type_spec)}")
            return
        # Brace elision: {scalar} for a scalar type — unwrap to the first element
        if isinstance(value, InitList) and type_spec is not None and not self.is_array_type(type_spec) and not (type_spec.is_struct() and not type_spec.is_pointer()):
            value = value.items[0].value if value.items else None
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
        # Compound literal: &(type){ init } — emit struct/array data as a synthetic global
        if isinstance(value, UnaryOp) and value.op == "&" and isinstance(value.operand, CastExpr) and isinstance(value.operand.operand, InitList):
            lit_type = value.operand.target_type
            lit_init = value.operand.operand
            lbl = self.new_label("__clit")
            self.pending_compound_lits.append((lbl, lit_type, lit_init, line, col))
            self.emit(f"    .quad {lbl}")
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
            # If target type is float/double, convert integer value to float bits
            import struct as _struct
            if type_spec is not None and type_spec.base in ("float", "double") and not type_spec.is_pointer():
                if type_spec.base == "float":
                    bits = _struct.unpack('<I', _struct.pack('<f', float(intval)))[0]
                    self.emit(f"    .long {bits}")
                else:
                    bits = _struct.unpack('<Q', _struct.pack('<d', float(intval)))[0]
                    self.emit(f"    .quad {bits}")
                return
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
        # Try constant float expression for float/double globals (e.g. -0.5f, -0.867*65536.0)
        if type_spec is not None and type_spec.base in ("float", "double") and not type_spec.is_pointer():
            fval = self._global_const_float(value)
            if fval is not None:
                import struct
                if type_spec.base == "float":
                    bits = struct.unpack('<I', struct.pack('<f', fval))[0]
                    self.emit(f"    .long {bits}")
                else:
                    bits = struct.unpack('<Q', struct.pack('<d', fval))[0]
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
        # Try constant float expression for integer globals (e.g. (.2*FRACUNIT) → truncate to int)
        if type_spec is not None and type_spec.base not in ("float", "double") and not type_spec.is_pointer():
            fval = self._global_const_float(value)
            if fval is not None:
                intval = int(fval)
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

    def collect_locals_expr(self, expr):
        """Scan an expression for nested StatementExpr bodies and collect their locals."""
        if expr is None:
            return
        if isinstance(expr, StatementExpr):
            for stmt in expr.body.stmts:
                self.collect_locals_stmt(stmt)
        elif hasattr(expr, '__dict__'):
            for val in expr.__dict__.values():
                if isinstance(val, list):
                    for item in val:
                        if hasattr(item, 'line'):
                            self.collect_locals_expr(item)
                elif hasattr(val, 'line'):
                    self.collect_locals_expr(val)

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
                self.all_static_locals[stmt.name] = self.static_locals[stmt.name]
                self.all_static_local_types[stmt.name] = stmt.type_spec
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
            if isinstance(stmt, ExprStmt) and stmt.expr is not None:
                self.collect_locals_expr(stmt.expr)
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
        self._dyn_sp_offset = 0  # accumulated permanent sp decrements during body codegen
        self._sw_stack_depth = 0  # net software-stack depth (push/pop balance)
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
                    self.emit_sub_reg_x29("x0", self.locals[name])
            elif type_spec is not None and type_spec.is_struct() and not type_spec.is_pointer():
                self.emit_sub_reg_x29("x0", self.locals[name])
            elif self.is_int128(type_spec):
                self.emit_local_ldp("x0", "x1", self.locals[name])
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
            elif self.is_int128(type_spec):
                self.emit("    ldp x0, x1, [x9]")
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
            elif self.is_int128(type_spec):
                self.emit("    ldp x0, x1, [x9]")
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
        # __int128: store x0 (lo) and x1 (hi) via stp
        if self.is_int128(type_spec):
            if name in self.locals:
                self.emit_local_stp("x0", "x1", self.locals[name])
                return
            if name in self.static_locals:
                self.emit_symbol_addr(self.static_locals[name], "x9")
                self.emit("    stp x0, x1, [x9]")
                return
            if name in self.globals:
                mangled = self.mangle(name)
                g = self.globals[name]
                if g.type_spec is not None and g.type_spec.is_extern:
                    self.emit(f"    adrp x9, {mangled}@GOTPAGE")
                    self.emit(f"    ldr x9, [x9, {mangled}@GOTPAGEOFF]")
                else:
                    self.emit_symbol_addr(mangled, "x9")
                self.emit("    stp x0, x1, [x9]")
                return
            self.error(f"undefined variable '{name}'", line, col)
            return
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
        if type_spec is not None and type_spec.base == "_Bool" and not is_fp and not type_spec.is_pointer():
            # _Bool stores 0 or 1 — normalize the value before storing.
            # Use src_reg (e.g. w1, w2) not hardcoded w0 so that the right
            # incoming register is normalised when storing non-first parameters.
            self.emit(f"    cmp {src_reg}, #0")
            self.emit(f"    cset {src_reg}, ne")
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
        self._sw_stack_depth += 16
        self.emit("    str x0, [sp, #-16]!")

    def pop_reg(self, reg: str):
        self._sw_stack_depth -= 16
        self.emit(f"    ldr {reg}, [sp], #16")

    def push_d0(self):
        self._sw_stack_depth += 16
        self.emit("    str d0, [sp, #-16]!")

    def pop_d0(self, reg: str = "d1"):
        self._sw_stack_depth -= 16
        self.emit(f"    ldr {reg}, [sp], #16")

    def push_s0(self):
        self._sw_stack_depth += 16
        self.emit("    str s0, [sp, #-16]!")

    def pop_s0(self, reg: str = "s1"):
        self._sw_stack_depth -= 16
        self.emit(f"    ldr {reg}, [sp], #16")

    def push_i128(self):
        """Push x0 (lo) / x1 (hi) as a 128-bit value onto the stack."""
        self._sw_stack_depth += 16
        self.emit("    stp x0, x1, [sp, #-16]!")

    def pop_i128(self, lo: str = "x2", hi: str = "x3"):
        """Pop a 128-bit value from the stack into lo/hi registers."""
        self._sw_stack_depth -= 16
        self.emit(f"    ldp {lo}, {hi}, [sp], #16")

    def emit_local_ldp(self, lo: str, hi: str, offset: int):
        """Load a 128-bit local at [x29, -offset] into lo/hi regs.  offset must be 8-aligned."""
        if offset <= 512:
            self.emit(f"    ldp {lo}, {hi}, [x29, #-{offset}]")
        else:
            self.emit_sub_reg_x29("x9", offset)
            self.emit(f"    ldp {lo}, {hi}, [x9]")

    def emit_local_stp(self, lo: str, hi: str, offset: int):
        """Store a 128-bit local from lo/hi regs into [x29, -offset].  offset must be 8-aligned."""
        if offset <= 512:
            self.emit(f"    stp {lo}, {hi}, [x29, #-{offset}]")
        else:
            self.emit_sub_reg_x29("x9", offset)
            self.emit(f"    stp {lo}, {hi}, [x9]")

    def widen_to_i128(self, type_spec):
        """Widen the value in x0 (or w0) to 128-bit (x0=lo, x1=hi) based on type_spec."""
        if type_spec is None:
            self.emit("    mov x1, xzr")
            return
        if type_spec.is_pointer() or type_spec.is_unsigned:
            sb = type_spec.size_bytes(self.target) if not type_spec.is_pointer() else 8
            if sb <= 4:
                self.emit("    uxtw x0, w0")
            # for 64-bit unsigned: x0 already contains the value
            self.emit("    mov x1, xzr")
        else:
            sb = type_spec.size_bytes(self.target)
            if sb == 1:
                self.emit("    sxtb x0, w0")
            elif sb == 2:
                self.emit("    sxth x0, w0")
            elif sb <= 4:
                self.emit("    sxtw x0, w0")
            # for 64-bit: x0 already contains the value
            self.emit("    asr x1, x0, #63")

    def emit_local_load(self, instr: str, reg: str, offset: int):
        """Emit load from [x29, #-offset], using x9 as scratch for offsets > 255."""
        if offset <= 255:
            self.emit(f"    {instr} {reg}, [x29, #-{offset}]")
        else:
            self.emit_sub_reg_x29("x9", offset)
            scaled = instr.replace("ldur", "ldr")
            self.emit(f"    {scaled} {reg}, [x9]")

    def emit_local_store(self, instr: str, reg: str, offset: int):
        """Emit store to [x29, #-offset], using x9 as scratch for offsets > 255."""
        if offset <= 255:
            self.emit(f"    {instr} {reg}, [x29, #-{offset}]")
        else:
            self.emit_sub_reg_x29("x9", offset)
            scaled = instr.replace("stur", "str")
            self.emit(f"    {scaled} {reg}, [x9]")

    _FP_BASES = frozenset({"float", "double", "long double"})

    def _sizeof_ts(self, ts) -> Optional[int]:
        """Return sizeof(ts) accounting for array dimensions."""
        if ts is None:
            return None
        base = ts.size_bytes(self.target)
        if ts.array_sizes:
            total = base
            for sz_expr in ts.array_sizes:
                n = self._global_const_int(sz_expr)
                if n is None:
                    return None
                total *= n
            return total
        return base

    def _global_const_int(self, value) -> Optional[int]:
        """Try to evaluate value as a compile-time constant integer. Returns None if not possible."""
        if isinstance(value, IntLiteral):
            return value.value
        if isinstance(value, CharLiteral):
            return ord(value.value)
        if isinstance(value, CastExpr):
            inner = self._global_const_int(value.operand)
            if inner is not None:
                return inner
            # Float-to-int constant folding: (int)(-0.867 * 65536.0) etc.
            fval = self._global_const_float(value.operand)
            if fval is not None:
                return int(fval)
            return None
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
                if op == "&&": return int(bool(l) and bool(r))
                if op == "||": return int(bool(l) or bool(r))
                if op == "==": return int(l == r)
                if op == "!=": return int(l != r)
                if op == "<": return int(l < r)
                if op == ">": return int(l > r)
                if op == "<=": return int(l <= r)
                if op == ">=": return int(l >= r)
        if isinstance(value, TernaryOp):
            cond = self._global_const_int(value.condition)
            if cond is not None:
                branch = value.true_expr if cond else value.false_expr
                return self._global_const_int(branch)
        if isinstance(value, SizeofExpr):
            if value.is_type:
                ts = value.operand
                if isinstance(ts, TypeSpec):
                    return self._sizeof_ts(ts)
            else:
                operand = value.operand
                ts = self.get_expr_type(operand)
                if ts is not None:
                    return self._sizeof_ts(ts)
        if isinstance(value, AlignofExpr):
            if value.is_type:
                ts = value.operand
                if isinstance(ts, TypeSpec):
                    if ts.is_struct() and ts.struct_def is not None:
                        return ts.struct_def.alignment(self.target)
                    return min(ts.size_bytes(self.target), self.target.layout.max_scalar_align)
        return None

    def _global_const_float(self, value) -> Optional[float]:
        """Try to evaluate value as a compile-time constant float. Returns None if not possible."""
        if isinstance(value, FloatLiteral):
            return value.value
        if isinstance(value, IntLiteral):
            return float(value.value)
        if isinstance(value, CharLiteral):
            return float(ord(value.value))
        if isinstance(value, CastExpr):
            return self._global_const_float(value.operand)
        if isinstance(value, UnaryOp):
            if value.op == "-":
                inner = self._global_const_float(value.operand)
                return -inner if inner is not None else None
            if value.op == "+":
                return self._global_const_float(value.operand)
        if isinstance(value, BinaryOp):
            l = self._global_const_float(value.left)
            r = self._global_const_float(value.right)
            if l is not None and r is not None:
                if value.op == "+": return l + r
                if value.op == "-": return l - r
                if value.op == "*": return l * r
                if value.op == "/" and r != 0.0: return l / r
                if value.op == "<<": return float(int(l) << int(r))
                if value.op == ">>": return float(int(l) >> int(r))
                if value.op == "&": return float(int(l) & int(r))
                if value.op == "|": return float(int(l) | int(r))
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
                if name in self.all_static_locals:
                    return self.all_static_locals[name]
                if name in self.functions:
                    return self.mangle(name)
            elif isinstance(operand, MemberAccess) and isinstance(operand.obj, Identifier):
                # &global_var.member — emit as label+offset relocation
                obj_name = operand.obj.name
                if obj_name in self.globals or obj_name in self.static_locals or obj_name in self.all_static_locals:
                    mangled = (self.static_locals.get(obj_name)
                               or self.all_static_locals.get(obj_name)
                               or self.mangle(obj_name))
                    src = self.globals.get(obj_name) or self.static_local_decls.get(
                        self.static_locals.get(obj_name) or self.all_static_locals.get(obj_name, ""))
                    struct_def = src.type_spec.struct_def if src and src.type_spec else None
                    if struct_def is not None:
                        off = struct_def.member_offset(operand.member, self.target)
                        if off is not None:
                            return mangled if off == 0 else f"{mangled}+{off}"
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
                            member_off = struct_def.member_offset(arr.member, self.target) or 0
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
            if value.name in self.all_static_locals:
                return self.all_static_locals[value.name]
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
        if self.is_int128(expr_type):
            # __int128 truthy: lo|hi != 0
            self.emit("    orr x0, x0, x1")
            self.emit("    cmp x0, #0")
            self.emit("    cset w0, ne")
            return
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
            self.emit_sp_sub(self.stack_size)

        int_idx = 0
        fp_idx = 0
        for param in func.params:
            if self.is_fp_type(param.type_spec):
                self.store_var(param.name, src_reg=f"d{fp_idx}", line=func.line, col=func.col)
                fp_idx += 1
            elif self.is_int128(param.type_spec):
                dest_offset = self.locals.get(param.name, 0)
                self.emit_local_stp(f"x{int_idx}", f"x{int_idx + 1}", dest_offset)
                int_idx += 2
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
                    # > 16 bytes: caller passes a hidden pointer in x{int_idx}.
                    # Copy struct_size bytes from the pointer to our local stack space.
                    for off in range(0, struct_size, 8):
                        remaining = struct_size - off
                        if remaining >= 8:
                            self.emit(f"    ldr x10, [x{int_idx}, #{off}]")
                            self.emit_local_store("stur", "x10", dest_offset - off)
                        else:
                            self.emit(f"    ldr w10, [x{int_idx}, #{off}]")
                            self.emit_local_store("stur", "w10", dest_offset - off)
                int_idx += 1
            else:
                if int_idx < 8:
                    arg_reg = self.ARG_REGS_64[int_idx] if (self.is_pointer_type(param.type_spec) or self.is_wide_scalar(param.type_spec)) else self.ARG_REGS_32[int_idx]
                    self.store_var(param.name, src_reg=arg_reg, line=func.line, col=func.col)
                else:
                    # Stack param: at [x29 + 16 + 8*(int_idx - 8)]
                    stack_off = 16 + 8 * (int_idx - 8)
                    dest_offset = self.locals.get(param.name, 0)
                    self.emit(f"    ldr x9, [x29, #{stack_off}]")
                    self.emit_local_store("stur", "x9", dest_offset)
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
            if ret_type is not None and self.is_int128(ret_type):
                # Value is already in x0/x1; widen if source is narrower
                expr_type = self.get_expr_type(stmt.value)
                if not self.is_int128(expr_type):
                    self.widen_to_i128(expr_type)
            elif ret_type is not None and ret_type.is_struct() and not ret_type.is_pointer():
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
            elif ret_type is not None and self.is_fp_type(ret_type):
                expr_type = self.get_expr_type(stmt.value)
                if not self.is_fp_type(expr_type):
                    # Integer expression returned from a double/float function: coerce to fp
                    if expr_type is not None and expr_type.is_unsigned:
                        self.emit("    ucvtf d0, x0" if self.is_wide_scalar(expr_type) else "    ucvtf d0, w0")
                    else:
                        self.emit("    scvtf d0, x0" if self.is_wide_scalar(expr_type) else "    scvtf d0, w0")
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
        # Update local type to reflect the declaration in the current scope.
        # The pre-pass (collect_locals_stmt) reuses one slot per name when the same name
        # appears in exclusive scopes (e.g. `if` vs `else if`), but always records the
        # FIRST type encountered.  Fix that by refreshing the type at code-gen time so that
        # type-resolution queries (`get_var_type`) see the right type while generating this block.
        if decl.type_spec is not None and decl.name in self.local_types:
            self.local_types[decl.name] = decl.type_spec
        if decl.type_spec is not None and self.is_array_type(decl.type_spec) and isinstance(decl.init, StringLiteral) and decl.type_spec.base == "char":
            # char a[] = "string" — copy bytes to stack
            offset = self.locals[decl.name]
            self.emit_sub_reg_x29("x9", offset)
            for i, ch in enumerate(decl.init.value):
                code = ord(ch)
                if code >= 0xF700:
                    code -= 0xF700
                self.emit(f"    movz w0, #{code}")
                self.emit(f"    strb w0, [x9, #{i}]")
            self.emit(f"    strb wzr, [x9, #{len(decl.init.value)}]")
            return
        if decl.type_spec is not None and self.is_array_type(decl.type_spec) and isinstance(decl.init, StringLiteral) and decl.init.wide:
            # wchar_t a[] = L"string" — copy 4-byte codepoints to stack
            offset = self.locals[decl.name]
            self.emit_sub_reg_x29("x9", offset)
            for i, ch in enumerate(decl.init.value):
                cp = ord(ch)
                self.emit_int_constant(cp, "w0")
                self.emit(f"    str w0, [x9, #{i * 4}]")
            self.emit(f"    str wzr, [x9, #{len(decl.init.value) * 4}]")
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
                    self.emit_sub_reg_x29("x0", self.locals[decl.name])
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
            if self.is_int128(decl.type_spec):
                self.emit("    mov x1, xzr")
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
            # Widen to __int128 if needed
            elif self.is_int128(decl.type_spec):
                val_type = self.get_expr_type(decl.init)
                if not self.is_int128(val_type):
                    self.widen_to_i128(val_type)
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
        elem_type = self.element_type(decl.type_spec)
        elem_size = self.total_size(elem_type)
        # Zero-initialize the entire array first if the init list may be shorter
        # than the total element count (C requires implicit zero-fill for omitted elements).
        total_bytes = self.total_size(decl.type_spec)
        explicit_count = len(decl.init.items) if decl.init else 0
        total_elem_count = self._array_dim_count(decl.type_spec)
        if explicit_count < total_elem_count:
            # C requires implicit zero-fill for omitted elements.
            base_offset = self.locals[decl.name]
            if total_bytes <= 512:
                # Small arrays: unrolled inline stores (8/4/1 bytes at a time)
                filled = 0
                while filled + 8 <= total_bytes:
                    self.emit_stur_zero(8, base_offset - filled)
                    filled += 8
                while filled + 4 <= total_bytes:
                    self.emit_stur_zero(4, base_offset - filled)
                    filled += 4
                while filled < total_bytes:
                    self.emit_stur_zero(1, base_offset - filled)
                    filled += 1
            else:
                # Large arrays: use a loop to zero (stp xzr, xzr = 16 bytes/iter)
                lbl_loop = self.new_label("zero_arr_loop")
                lbl_end  = self.new_label("zero_arr_end")
                self.emit_sub_reg_x29("x9", base_offset)
                self.emit_large_imm("x10", total_bytes)
                self.emit(f"{lbl_loop}:")
                self.emit(f"    cbz x10, {lbl_end}")
                # Use stp when 16+ bytes remain, str when 8+, strb otherwise
                self.emit(f"    cmp x10, #16")
                lbl_lt16 = self.new_label("zero_lt16")
                self.emit(f"    b.lt {lbl_lt16}")
                self.emit(f"    stp xzr, xzr, [x9], #16")
                self.emit(f"    sub x10, x10, #16")
                self.emit(f"    b {lbl_loop}")
                self.emit(f"{lbl_lt16}:")
                self.emit(f"    cmp x10, #8")
                lbl_lt8 = self.new_label("zero_lt8")
                self.emit(f"    b.lt {lbl_lt8}")
                self.emit(f"    str xzr, [x9], #8")
                self.emit(f"    sub x10, x10, #8")
                self.emit(f"    b {lbl_loop}")
                self.emit(f"{lbl_lt8}:")
                self.emit(f"    strb wzr, [x9], #1")
                self.emit(f"    sub x10, x10, #1")
                self.emit(f"    b {lbl_loop}")
                self.emit(f"{lbl_end}:")
        # Build index-to-value map respecting designator_index and range designators
        init_map: dict = {}
        cur_idx = 0
        for item in decl.init.items:
            if item.designator_index is not None:
                cur_idx = item.designator_index
            if item.designator_end is not None:
                # Range designator [start ... end] = val
                for i in range(cur_idx, item.designator_end + 1):
                    init_map[i] = item.value
                cur_idx = item.designator_end + 1
            else:
                init_map[cur_idx] = item.value
                cur_idx += 1

        for index in range(total_elem_count):
            value = init_map.get(index)
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
                # Recompute x9 here since gen_expr is not called, but be explicit about base
                self.emit_sub_reg_x29("x9", self.locals[decl.name])
                for i in range(self.total_size(elem_type)):
                    b = str_bytes[i] if i < len(str_bytes) else 0
                    self.emit(f"    movz w0, #{b}")
                    self.emit(f"    strb w0, [x9, #{offset + i}]")
                continue
            self.gen_expr(value)
            # If storing into float/double but value was an integer, convert
            if self.is_fp_type(elem_type):
                val_type = self.get_expr_type(value)
                if val_type is not None and not self.is_fp_type(val_type):
                    if val_type.is_unsigned:
                        self.emit("    ucvtf d0, x0" if self.is_wide_scalar(val_type) else "    ucvtf d0, w0")
                    else:
                        self.emit("    scvtf d0, x0" if self.is_wide_scalar(val_type) else "    scvtf d0, w0")
            # Recompute x9 after gen_expr since gen_expr may clobber x9 (e.g. float literals, globals)
            neg_off = self.locals[decl.name] - offset
            self.emit_sub_reg_x29("x9", neg_off)
            if self.is_fp_type(elem_type):
                if elem_type is not None and elem_type.base == "float":
                    self.emit("    fcvt s0, d0")
                    self.emit("    str s0, [x9]")
                else:
                    self.emit("    str d0, [x9]")
            elif elem_type is not None and self.is_pointer_type(elem_type):
                self.emit("    str x0, [x9]")
            elif self.is_byte_type(elem_type):
                self.emit("    strb w0, [x9]")
            elif elem_type is not None and elem_type.base == "short" and not elem_type.is_pointer():
                self.emit("    strh w0, [x9]")
            else:
                self.emit("    str w0, [x9]")

    def _resolve_designator_path(self, type_spec, path: list):
        """Walk a designator path (e.g. ['a', 'j']) through nested struct types.
        Returns (byte_offset, leaf_type_spec) from the base of type_spec, or None on error."""
        struct_def = type_spec.struct_def if type_spec is not None else None
        if struct_def is None:
            return None
        offset = 0
        current_type = type_spec
        for name in path:
            sd = current_type.struct_def if current_type is not None else None
            if sd is None:
                return None
            found = None
            for m in sd.members:
                if m.name == name:
                    found = m
                    break
            if found is None:
                return None
            member_off = sd.member_offset(name, self.target) or 0
            offset += member_off
            current_type = found.type_spec
        return (offset, current_type)

    def gen_struct_init_at_addr(self, type_spec, init: 'InitList', x29_neg_offset: int):
        """Write struct init list items to [x29 - x29_neg_offset + member_off] for each member.
        Uses x29-relative stores so gen_expr clobbering scratch regs is safe."""
        struct_def = type_spec.struct_def
        if struct_def is None:
            return
        members = [m for m in struct_def.members if m.name != ""]
        # Apply flat (brace-elided) init restructuring when more items than members
        if len(init.items) > len(members):
            init = self._restructure_flat_init(type_spec, init, init.line, init.col)
        # Zero-initialize the struct region to ensure un-filled members/tails are zero
        total_bytes = struct_def.size_bytes(self.target)
        byte_off = 0
        while byte_off + 8 <= total_bytes:
            self.emit_stur_zero(8, x29_neg_offset - byte_off)
            byte_off += 8
        while byte_off + 4 <= total_bytes:
            self.emit_stur_zero(4, x29_neg_offset - byte_off)
            byte_off += 4
        while byte_off < total_bytes:
            self.emit_stur_zero(1, x29_neg_offset - byte_off)
            byte_off += 1
        for i, item in enumerate(init.items):
            if item.value is None:
                continue
            # Resolve which member this item targets
            if item.designator_path is not None and len(item.designator_path) > 0:
                result = self._resolve_designator_path(type_spec, item.designator_path)
                if result is None:
                    continue
                path_off, leaf_type = result
                self.gen_expr(item.value)
                final_neg = x29_neg_offset - path_off
                self.emit_sub_reg_x29("x9", final_neg)
                size = leaf_type.size_bytes(self.target) if leaf_type is not None else 4
                if size <= 1:
                    self.emit("    strb w0, [x9]")
                elif size <= 2:
                    self.emit("    strh w0, [x9]")
                elif size <= 4:
                    self.emit("    str w0, [x9]")
                else:
                    self.emit("    str x0, [x9]")
                continue
            if item.designator is not None:
                idx = next((j for j, m in enumerate(members) if m.name == item.designator), None)
                if idx is None:
                    continue
                member = members[idx]
            elif i < len(members):
                member = members[i]
            else:
                break
            member_off = struct_def.member_offset(member.name, self.target) or 0
            member_type = member.type_spec
            # Unwrap compound literals
            init_val = item.value
            if isinstance(init_val, CastExpr) and isinstance(init_val.operand, InitList):
                init_val = init_val.operand
            if member_type is not None and member_type.is_struct() and not member_type.is_pointer() and isinstance(init_val, InitList):
                self.gen_struct_init_at_addr(member_type, init_val, x29_neg_offset - member_off)
                continue
            # Struct-valued expression (identifier, deref, cast) → memcpy
            if (member_type is not None and member_type.is_struct() and not member_type.is_pointer()
                    and not isinstance(init_val, InitList)):
                member_size = member_type.struct_def.size_bytes(self.target) if member_type.struct_def else member_type.size_bytes(self.target)
                self.gen_expr(init_val)           # x0 = source address
                final_neg = x29_neg_offset - member_off
                self.emit_sub_reg_x29("x9", final_neg)  # x9 = dest address
                self.emit("    mov x1, x0")
                self.emit("    mov x0, x9")
                self.emit(f"    mov x2, #{member_size}")
                self.emit("    bl _memcpy")
                continue
            if self.is_array_type(member_type) and isinstance(item.value, InitList):
                elem_type = self.element_type(member_type)
                elem_size = self.total_size(elem_type)
                for elem_idx, elem_item in enumerate(item.value.items):
                    if elem_item.value is None:
                        continue
                    self.gen_expr(elem_item.value)
                    elem_off = member_off + elem_idx * elem_size
                    final_neg = x29_neg_offset - elem_off
                    self.emit_sub_reg_x29("x9", final_neg)
                    if elem_size <= 1:
                        self.emit("    strb w0, [x9]")
                    elif elem_size <= 2:
                        self.emit("    strh w0, [x9]")
                    elif elem_size <= 4:
                        self.emit("    str w0, [x9]")
                    else:
                        self.emit("    str x0, [x9]")
                continue
            # Handle char array member initialized with a string literal
            if (self.is_array_type(member_type) and member_type is not None
                    and member_type.base == "char" and isinstance(item.value, StringLiteral)):
                s = item.value.value
                self.gen_expr(item.value)          # x0 = pointer to string literal
                final_neg = x29_neg_offset - member_off
                self.emit_sub_reg_x29("x9", final_neg)  # x9 = member address
                self.emit("    mov x1, x0")
                self.emit("    mov x0, x9")
                self.emit(f"    mov x2, #{len(s) + 1}")
                self.emit("    bl _memcpy")
                continue
            self.gen_expr(item.value)
            # If storing into float/double but value was an integer, convert
            if self.is_fp_type(member_type):
                val_type = self.get_expr_type(item.value)
                if val_type is not None and not self.is_fp_type(val_type):
                    if val_type.is_unsigned:
                        self.emit("    ucvtf d0, x0" if self.is_wide_scalar(val_type) else "    ucvtf d0, w0")
                    else:
                        self.emit("    scvtf d0, x0" if self.is_wide_scalar(val_type) else "    scvtf d0, w0")
            # Compute address: x29 - x29_neg_offset + member_off
            final_neg = x29_neg_offset - member_off
            self.emit_sub_reg_x29("x9", final_neg)
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
        members = [m for m in struct_def.members if m.name != ""]
        init = decl.init
        # Apply flat (brace-elided) init restructuring when more items than members
        if len(init.items) > len(members):
            init = self._restructure_flat_init(decl.type_spec, init, init.line, init.col)
        # Zero-initialize the whole struct to ensure un-initialized members and
        # char-array tails (after string copy) are properly zeroed.
        total_bytes = struct_def.size_bytes(self.target)
        fp_neg_base = self.locals[decl.name]
        byte_off = 0
        while byte_off + 8 <= total_bytes:
            self.emit_stur_zero(8, fp_neg_base - byte_off)
            byte_off += 8
        while byte_off + 4 <= total_bytes:
            self.emit_stur_zero(4, fp_neg_base - byte_off)
            byte_off += 4
        while byte_off < total_bytes:
            self.emit_stur_zero(1, fp_neg_base - byte_off)
            byte_off += 1
        for i, item in enumerate(init.items):
            if item.value is None:
                continue
            # Resolve which member this item targets (designator-path or positional)
            if item.designator_path is not None and len(item.designator_path) > 0:
                result = self._resolve_designator_path(decl.type_spec, item.designator_path)
                if result is None:
                    continue
                path_off, leaf_type = result
                self.gen_expr(item.value)
                neg_off = self.locals[decl.name] - path_off
                self.emit_sub_reg_x29("x9", neg_off)
                size = leaf_type.size_bytes(self.target) if leaf_type is not None else 4
                if size <= 1:
                    self.emit("    strb w0, [x9]")
                elif size <= 2:
                    self.emit("    strh w0, [x9]")
                elif size <= 4:
                    self.emit("    str w0, [x9]")
                else:
                    self.emit("    str x0, [x9]")
                continue
            if item.designator is not None:
                idx = next((j for j, m in enumerate(members) if m.name == item.designator), None)
                if idx is None:
                    continue
                member = members[idx]
            elif i < len(members):
                member = members[i]
            else:
                break
            member_off = struct_def.member_offset(member.name, self.target) or 0
            member_type = member.type_spec
            # Handle char array member initialized with a string literal (e.g. char name[100] = "hello")
            if (self.is_array_type(member_type) and member_type is not None
                    and member_type.base == "char" and isinstance(item.value, StringLiteral)):
                s = item.value.value
                self.gen_expr(item.value)          # x0 = pointer to string literal
                neg_off = self.locals[decl.name] - member_off
                self.emit_sub_reg_x29("x9", neg_off)   # x9 = member address
                self.emit("    mov x1, x0")            # x1 = src
                self.emit("    mov x0, x9")            # x0 = dest
                self.emit(f"    mov x2, #{len(s) + 1}")
                self.emit("    bl _memcpy")
                continue
            # Handle nested struct initialiser (e.g. struct S m = {1, 2, {3, 4}})
            # Also handles compound literal: struct S m = (struct S){1, 2, {3, 4}}
            init_val = item.value
            if isinstance(init_val, CastExpr) and isinstance(init_val.operand, InitList):
                init_val = init_val.operand
            if (member_type is not None and member_type.is_struct() and not member_type.is_pointer()
                    and isinstance(init_val, InitList)):
                x29_neg = self.locals[decl.name] - member_off
                self.gen_struct_init_at_addr(member_type, init_val, x29_neg)
                continue
            # Struct-valued expression (identifier, deref, cast) → memcpy
            if (member_type is not None and member_type.is_struct() and not member_type.is_pointer()
                    and not isinstance(init_val, InitList)):
                member_size = member_type.struct_def.size_bytes(self.target) if member_type.struct_def else member_type.size_bytes(self.target)
                self.gen_expr(init_val)            # x0 = source address
                x29_neg = self.locals[decl.name] - member_off
                self.emit_sub_reg_x29("x9", x29_neg)  # x9 = dest address
                self.emit("    mov x1, x0")
                self.emit("    mov x0, x9")
                self.emit(f"    mov x2, #{member_size}")
                self.emit("    bl _memcpy")
                continue
            # Handle nested array initialiser (e.g. short data[8] = {0, 0, ...})
            if self.is_array_type(member_type) and isinstance(item.value, InitList):
                elem_type = self.element_type(member_type)
                elem_size = elem_type.size_bytes(self.target)
                # Build index-to-value map respecting designator_index and range designators
                elem_map: dict = {}
                cur_eidx = 0
                for ei in item.value.items:
                    if ei.designator_index is not None:
                        cur_eidx = ei.designator_index
                    if ei.designator_end is not None:
                        for k in range(cur_eidx, ei.designator_end + 1):
                            elem_map[k] = ei.value
                        cur_eidx = ei.designator_end + 1
                    else:
                        elem_map[cur_eidx] = ei.value
                        cur_eidx += 1
                total_count = self._array_dim_count(member_type)
                for elem_idx in range(total_count):
                    elem_val = elem_map.get(elem_idx)
                    if elem_val is None:
                        continue
                    self.gen_expr(elem_val)
                    elem_off = member_off + elem_idx * elem_size
                    neg_off = self.locals[decl.name] - elem_off
                    self.emit_sub_reg_x29("x9", neg_off)
                    if elem_size <= 1:
                        self.emit("    strb w0, [x9]")
                    elif elem_size <= 2:
                        self.emit("    strh w0, [x9]")
                    elif elem_size <= 4:
                        self.emit("    str w0, [x9]")
                    else:
                        self.emit("    str x0, [x9]")
                continue
            self.gen_expr(item.value)
            # If storing into float/double but value was an integer, convert
            if self.is_fp_type(member_type):
                val_type = self.get_expr_type(item.value)
                if val_type is not None and not self.is_fp_type(val_type):
                    if val_type.is_unsigned:
                        self.emit("    ucvtf d0, x0" if self.is_wide_scalar(val_type) else "    ucvtf d0, w0")
                    else:
                        self.emit("    scvtf d0, x0" if self.is_wide_scalar(val_type) else "    scvtf d0, w0")
            # Recompute x9 after gen_expr since gen_expr may clobber x9 (e.g. float literals, globals)
            neg_off = self.locals[decl.name] - member_off
            self.emit_sub_reg_x29("x9", neg_off)
            if self.is_fp_type(member_type):
                if member_type.base == "float":
                    self.emit("    fcvt s0, d0")
                    self.emit("    str s0, [x9]")
                else:
                    self.emit("    str d0, [x9]")
            elif self.is_pointer_type(member_type) or self.is_wide_scalar(member_type):
                self.emit("    str x0, [x9]")
            elif member_type.size_bytes(self.target) <= 1:
                self.emit("    strb w0, [x9]")
            elif member_type.size_bytes(self.target) <= 2:
                self.emit("    strh w0, [x9]")
            else:
                self.emit("    str w0, [x9]")

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
            case_val = self._global_const_int(value)
            if case_val is None:
                self.error("arm64-apple-darwin switch requires constant integer case labels", case_stmt.line, case_stmt.col)
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
        elif isinstance(expr, StatementExpr):
            saved_locals = dict(self.locals)
            saved_local_types = dict(self.local_types)
            for stmt in expr.body.stmts:
                self.gen_stmt(stmt)
            # Result of the last ExprStmt is already in x0
            self.locals = saved_locals
            self.local_types = saved_local_types
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

            if self.is_int128(target_type):
                # __int128 compound assignment: load current, push, gen rhs, pop, apply op
                if isinstance(expr.target, Identifier):
                    self.load_var(expr.target.name, expr.line, expr.col)
                    self.push_i128()
                    self.gen_expr(expr.value)
                    rhs_type = self.get_expr_type(expr.value)
                    if not self.is_int128(rhs_type):
                        self.widen_to_i128(rhs_type)
                    # Now x0/x1 = rhs; pop lhs into x2/x3
                    self.pop_i128("x2", "x3")
                    self._apply_i128_op(op, target_type)
                    self.store_var(expr.target.name, line=expr.line, col=expr.col)
                else:
                    self.gen_expr(expr.target)
                    self.push_i128()
                    self.gen_expr(expr.value)
                    rhs_type = self.get_expr_type(expr.value)
                    if not self.is_int128(rhs_type):
                        self.widen_to_i128(rhs_type)
                    self.pop_i128("x2", "x3")
                    self._apply_i128_op(op, target_type)
                    # store result back via address
                    self.push_i128()
                    self.gen_lvalue_addr(expr.target)
                    self.emit("    ldr x2, [sp], #16")
                    self._sw_stack_depth -= 16
                    self.emit("    ldr x3, [sp], #16")
                    self._sw_stack_depth -= 16
                    self.emit("    stp x2, x3, [x0]")
                    self.emit("    mov x0, x2")
                    self.emit("    mov x1, x3")
                return

            if self.is_fp_type(target_type):
                # FP compound assignment — load current, compute, store
                val_type = self.get_expr_type(expr.value)
                both_float = (target_type is not None and target_type.base == "float" and
                              val_type is not None and val_type.base == "float")
                if isinstance(expr.target, Identifier):
                    self.load_var(expr.target.name, expr.line, expr.col)
                else:
                    self.gen_expr(expr.target)
                if both_float:
                    self.emit("    fcvt s0, d0")
                    self.push_s0()
                    self.gen_expr(expr.value)
                    if not self.is_fp_type(val_type):
                        self.emit("    scvtf s0, x0" if self.is_wide_scalar(val_type) else "    scvtf s0, w0")
                    else:
                        self.emit("    fcvt s0, d0")
                    self.pop_s0("s1")
                    if op == "+":
                        self.emit("    fadd s0, s1, s0")
                    elif op == "-":
                        self.emit("    fsub s0, s1, s0")
                    elif op == "*":
                        self.emit("    fmul s0, s1, s0")
                    elif op == "/":
                        self.emit("    fdiv s0, s1, s0")
                    else:
                        self.error(f"compound assignment '{expr.op}' is not supported for FP on arm64-apple-darwin", expr.line, expr.col)
                    self.emit("    fcvt d0, s0")
                else:
                    self.push_d0()
                    self.gen_expr(expr.value)
                    if not self.is_fp_type(val_type):
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
                if target_type is not None and target_type.is_pointer():
                    scale = self.element_size(target_type)
                    self.emit("    sxtw x0, w0")
                    if scale != 1:
                        self.emit(f"    mov x2, #{scale}")
                        self.emit("    mul x0, x0, x2")
                    self.emit("    add x0, x1, x0")
                else:
                    self.emit("    add x0, x1, x0" if wide else "    add w0, w1, w0")
            elif op == "-":
                if target_type is not None and target_type.is_pointer():
                    scale = self.element_size(target_type)
                    self.emit("    sxtw x0, w0")
                    if scale != 1:
                        self.emit(f"    mov x2, #{scale}")
                        self.emit("    mul x0, x0, x2")
                    self.emit("    sub x0, x1, x0")
                else:
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
                        # Set x0 = &local so chained assignment can use it as a source ptr
                        self.emit_sub_reg_x29("x0", dest_offset)
                    else:
                        # Non-local: store struct bytes via str (not memcpy which needs a ptr src)
                        self.emit("    mov x10, x1")  # save high bytes
                        self.push_x0()                # save low bytes
                        self.gen_lvalue_addr(expr.target)  # x0 = &target
                        self.pop_reg("x1")             # x1 = low bytes
                        if struct_size <= 4:
                            self.emit("    str w1, [x0]")
                        elif struct_size <= 8:
                            self.emit("    str x1, [x0]")
                        else:
                            self.emit("    str x1, [x0]")
                            rem = struct_size - 8
                            if rem <= 4:
                                self.emit("    str w10, [x0, #8]")
                            else:
                                self.emit("    str x10, [x0, #8]")
                        # x0 = &target still; good for chained assignment
                else:
                    self.push_x0()
                    self.gen_lvalue_addr(expr.target)
                    self.pop_reg("x1")
                    self.emit(f"    mov x2, #{struct_size}")
                    self.emit("    bl _memcpy")
                    # After memcpy, x0 = dest (first arg, returned by memcpy). ✓
                return
            if self.is_int128(target_type):
                val_type = self.get_expr_type(expr.value)
                if not self.is_int128(val_type):
                    self.widen_to_i128(val_type)
                self.store_var(expr.target.name, line=expr.line, col=expr.col)
                return
            if self.is_fp_type(target_type):
                val_type = self.get_expr_type(expr.value)
                if not self.is_fp_type(val_type):
                    if val_type is not None and val_type.is_unsigned:
                        self.emit("    ucvtf d0, x0" if self.is_wide_scalar(val_type) else "    ucvtf d0, w0")
                    else:
                        self.emit("    scvtf d0, x0" if self.is_wide_scalar(val_type) else "    scvtf d0, w0")
            elif (self.is_wide_scalar(target_type) and not target_type.is_unsigned
                    and not self.is_pointer_type(target_type)):
                # Sign-extend narrow int into wide (long/long long) variable — same as gen_var_decl
                val_type = self.get_expr_type(expr.value)
                if val_type is None or not (self.is_wide_scalar(val_type) or val_type.is_pointer()
                                            or self.is_fp_type(val_type)):
                    expr_size = val_type.size_bytes(self.target) if val_type is not None else 4
                    if expr_size <= 1:
                        self.emit("    sxtb w0, w0")
                    elif expr_size <= 2:
                        self.emit("    sxth w0, w0")
                    self.emit("    sxtw x0, w0")
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
        is_i128_op = self.is_int128(left_type) or self.is_int128(right_type)

        if is_i128_op:
            self._gen_i128_binary_op(expr, left_type, right_type)
            return

        if is_fp_op:
            # Use single-precision (s) registers when both operands are float to
            # preserve float semantics (not double precision).
            both_float = (left_type is not None and left_type.base == "float" and
                          right_type is not None and right_type.base == "float")
            fp_cond = {
                "==": "eq", "!=": "ne",
                "<": "mi", "<=": "ls",
                ">": "gt", ">=": "ge",
            }
            if both_float:
                # Left operand → s0
                self.gen_expr(expr.left)
                if not self.is_fp_type(left_type):
                    self.emit("    scvtf s0, x0" if self.is_wide_scalar(left_type) else "    scvtf s0, w0")
                else:
                    self.emit("    fcvt s0, d0")  # exact: d0 was (double)float_val
                self.push_s0()
                # Right operand → s0
                self.gen_expr(expr.right)
                if not self.is_fp_type(right_type):
                    self.emit("    scvtf s0, x0" if self.is_wide_scalar(right_type) else "    scvtf s0, w0")
                else:
                    self.emit("    fcvt s0, d0")
                self.pop_s0("s1")  # s1 = left float value
                if expr.op in fp_cond:
                    self.emit("    fcmp s1, s0")
                    self.emit(f"    cset w0, {fp_cond[expr.op]}")
                elif expr.op == "+":
                    self.emit("    fadd s0, s1, s0")
                    self.emit("    fcvt d0, s0")
                elif expr.op == "-":
                    self.emit("    fsub s0, s1, s0")
                    self.emit("    fcvt d0, s0")
                elif expr.op == "*":
                    self.emit("    fmul s0, s1, s0")
                    self.emit("    fcvt d0, s0")
                elif expr.op == "/":
                    self.emit("    fdiv s0, s1, s0")
                    self.emit("    fcvt d0, s0")
                else:
                    self.error(f"binary operator '{expr.op}' is not supported for floating-point on arm64-apple-darwin", expr.line, expr.col)
            else:
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
            if not self.is_wide_scalar(right_type):
                self.emit("    sxtw x0, w0")
            if scale != 1:
                self.emit(f"    mov x2, #{scale}")
                self.emit("    mul x0, x0, x2")
            self.emit("    add x0, x1, x0")
        elif expr.op == "+" and right_ptr and not left_ptr:
            scale = self.element_size(right_type)
            if not self.is_wide_scalar(left_type):
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
            if not self.is_wide_scalar(right_type):
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

    def _apply_i128_op(self, op: str, type_spec=None):
        """Apply a binary op to x2/x3 (left) and x0/x1 (right), result in x0/x1."""
        is_unsigned = type_spec is not None and type_spec.is_unsigned
        if op == "+":
            self.emit("    adds x0, x2, x0")
            self.emit("    adc x1, x3, x1")
        elif op == "-":
            self.emit("    subs x0, x2, x0")
            self.emit("    sbc x1, x3, x1")
        elif op == "*":
            # 128x128→128 inline multiply
            self.emit("    mul x4, x2, x0")       # lo = lo_l * lo_r (low 64)
            self.emit("    umulh x5, x2, x0")     # hi carry from lo*lo
            self.emit("    mul x6, x3, x0")       # hi_l * lo_r (low 64 only)
            self.emit("    mul x7, x2, x1")       # lo_l * hi_r (low 64 only)
            self.emit("    add x1, x5, x6")
            self.emit("    add x1, x1, x7")
            self.emit("    mov x0, x4")
        elif op == "&":
            self.emit("    and x0, x2, x0")
            self.emit("    and x1, x3, x1")
        elif op == "|":
            self.emit("    orr x0, x2, x0")
            self.emit("    orr x1, x3, x1")
        elif op == "^":
            self.emit("    eor x0, x2, x0")
            self.emit("    eor x1, x3, x1")
        elif op in {"/", "%"}:
            # left=x2/x3, right=x0/x1 → swap to call runtime helper
            self.emit("    mov x4, x0")
            self.emit("    mov x5, x1")
            self.emit("    mov x0, x2")
            self.emit("    mov x1, x3")
            self.emit("    mov x2, x4")
            self.emit("    mov x3, x5")
            fn = ("___udivti3" if is_unsigned else "___divti3") if op == "/" else ("___umodti3" if is_unsigned else "___modti3")
            self.emit(f"    bl {fn}")
        elif op in {"<<", ">>"}:
            # left=x2/x3, right=x0/x1; shift count in x0 (lo)
            lo_label = self.new_label("i128_shift_small")
            done_label = self.new_label("i128_shift_done")
            noop_label = self.new_label("i128_shift_noop")
            self.emit("    and x4, x0, #127")
            self.emit(f"    cbz x4, {noop_label}")
            self.emit("    cmp x4, #64")
            if op == "<<":
                self.emit(f"    b.lt {lo_label}")
                self.emit("    sub x5, x4, #64")
                self.emit("    lsl x1, x2, x5")
                self.emit("    mov x0, xzr")
                self.emit(f"    b {done_label}")
                self.label(lo_label)
                self.emit("    neg x5, x4")
                self.emit("    lsl x1, x3, x4")
                self.emit("    lsr x6, x2, x5")
                self.emit("    orr x1, x1, x6")
                self.emit("    lsl x0, x2, x4")
            else:
                self.emit(f"    b.lt {lo_label}")
                self.emit("    sub x5, x4, #64")
                if is_unsigned:
                    self.emit("    lsr x0, x3, x5")
                    self.emit("    mov x1, xzr")
                else:
                    self.emit("    asr x0, x3, x5")
                    self.emit("    asr x1, x3, #63")
                self.emit(f"    b {done_label}")
                self.label(lo_label)
                self.emit("    neg x5, x4")
                self.emit("    lsr x0, x2, x4")
                self.emit("    lsl x6, x3, x5")
                self.emit("    orr x0, x0, x6")
                if is_unsigned:
                    self.emit("    lsr x1, x3, x4")
                else:
                    self.emit("    asr x1, x3, x4")
            self.emit(f"    b {done_label}")
            self.label(noop_label)
            self.emit("    mov x0, x2")
            self.emit("    mov x1, x3")
            self.label(done_label)

    def _gen_i128_binary_op(self, expr: BinaryOp, left_type, right_type):
        """Generate code for a binary operation where at least one operand is __int128."""
        is_unsigned = ((left_type is not None and left_type.is_unsigned) or
                       (right_type is not None and right_type.is_unsigned))
        op = expr.op
        # Evaluate left, widen if needed, push
        self.gen_expr(expr.left)
        if not self.is_int128(left_type):
            self.widen_to_i128(left_type)
        self.push_i128()
        # Evaluate right, widen if needed; right now in x0/x1
        self.gen_expr(expr.right)
        if not self.is_int128(right_type):
            self.widen_to_i128(right_type)
        # Pop left into x2/x3; right is already x0/x1
        self.pop_i128("x2", "x3")

        if op in {"==", "!=", "<", ">", "<=", ">="}:
            # Comparison: left=x2/x3, right=x0/x1
            if op == "==":
                self.emit("    cmp x2, x0")
                self.emit("    ccmp x3, x1, #0, eq")
                self.emit("    cset w0, eq")
            elif op == "!=":
                self.emit("    cmp x2, x0")
                self.emit("    ccmp x3, x1, #0, eq")
                self.emit("    cset w0, ne")
            elif op == "<":
                if is_unsigned:
                    self.emit("    cmp x2, x0")
                    self.emit("    sbcs xzr, x3, x1")
                    self.emit("    cset w0, lo")
                else:
                    self.emit("    cmp x2, x0")
                    self.emit("    sbcs xzr, x3, x1")
                    self.emit("    cset w0, lt")
            elif op == ">":
                if is_unsigned:
                    self.emit("    cmp x0, x2")
                    self.emit("    sbcs xzr, x1, x3")
                    self.emit("    cset w0, lo")
                else:
                    self.emit("    cmp x0, x2")
                    self.emit("    sbcs xzr, x1, x3")
                    self.emit("    cset w0, lt")
            elif op == "<=":
                if is_unsigned:
                    self.emit("    cmp x0, x2")
                    self.emit("    sbcs xzr, x1, x3")
                    self.emit("    cset w0, hs")
                else:
                    self.emit("    cmp x0, x2")
                    self.emit("    sbcs xzr, x1, x3")
                    self.emit("    cset w0, ge")
            elif op == ">=":
                if is_unsigned:
                    self.emit("    cmp x2, x0")
                    self.emit("    sbcs xzr, x3, x1")
                    self.emit("    cset w0, hs")
                else:
                    self.emit("    cmp x2, x0")
                    self.emit("    sbcs xzr, x3, x1")
                    self.emit("    cset w0, ge")
            return

        if op in {"+", "-", "*", "&", "|", "^"}:
            self._apply_i128_op(op)
            return

        if op in {"/", "%"}:
            # Use runtime helpers: ___divti3, ___modti3, ___udivti3, ___umodti3
            # ABI: first arg x0/x1, second arg x2/x3 -> but we have left=x2/x3, right=x0/x1
            # Swap: right -> x2/x3, left -> x0/x1
            self.emit("    mov x4, x0")   # right lo temp
            self.emit("    mov x5, x1")   # right hi temp
            self.emit("    mov x0, x2")   # left lo -> x0
            self.emit("    mov x1, x3")   # left hi -> x1
            self.emit("    mov x2, x4")   # right lo -> x2
            self.emit("    mov x3, x5")   # right hi -> x3
            if op == "/":
                fn = "___udivti3" if is_unsigned else "___divti3"
            else:
                fn = "___umodti3" if is_unsigned else "___modti3"
            self.emit(f"    bl {fn}")
            # result in x0/x1
            return

        if op in {"<<", ">>"}:
            # After pop_i128("x2","x3"): left lo=x2, left hi=x3, right lo=x0 (shift count)
            # Save shift count in x4; use x5/x6 as temporaries
            lo_label = self.new_label("i128_shift_small")
            done_label = self.new_label("i128_shift_done")
            noop_label = self.new_label("i128_shift_noop")
            self.emit("    and x4, x0, #127")      # x4 = clamped shift count
            self.emit(f"    cbz x4, {noop_label}")
            self.emit("    cmp x4, #64")
            if op == "<<":
                self.emit(f"    b.lt {lo_label}")
                # n >= 64: hi = lo << (n-64), lo = 0
                self.emit("    sub x5, x4, #64")
                self.emit("    lsl x1, x2, x5")
                self.emit("    mov x0, xzr")
                self.emit(f"    b {done_label}")
                self.label(lo_label)
                # 1 <= n < 64: lo <<= n, hi = (hi<<n)|(lo>>(64-n))
                self.emit("    neg x5, x4")       # x5 = 64-n (via neg: -n mod 64 = 64-n)
                self.emit("    lsl x1, x3, x4")
                self.emit("    lsr x6, x2, x5")
                self.emit("    orr x1, x1, x6")
                self.emit("    lsl x0, x2, x4")
                self.emit(f"    b {done_label}")
            else:
                self.emit(f"    b.lt {lo_label}")
                # n >= 64
                self.emit("    sub x5, x4, #64")
                if is_unsigned:
                    self.emit("    lsr x0, x3, x5")
                    self.emit("    mov x1, xzr")
                else:
                    self.emit("    asr x0, x3, x5")
                    self.emit("    asr x1, x3, #63")
                self.emit(f"    b {done_label}")
                self.label(lo_label)
                # 1 <= n < 64
                self.emit("    neg x5, x4")       # x5 = 64-n
                self.emit("    lsr x0, x2, x4")   # lo >>= n (always logical)
                self.emit("    lsl x6, x3, x5")
                self.emit("    orr x0, x0, x6")
                if is_unsigned:
                    self.emit("    lsr x1, x3, x4")
                else:
                    self.emit("    asr x1, x3, x4")
                self.emit(f"    b {done_label}")
            self.label(noop_label)
            self.emit("    mov x0, x2")
            self.emit("    mov x1, x3")
            self.label(done_label)
            return

        self.error(f"__int128 binary operator '{op}' is not yet supported on arm64-apple-darwin", expr.line, expr.col)

    def gen_unary_op(self, expr: UnaryOp):
        if expr.op in {"++", "--"}:
            if isinstance(expr.operand, Identifier):
                name = expr.operand.name
                type_spec = self.get_var_type(name)
                if self.is_int128(type_spec):
                    # __int128 increment/decrement
                    self.load_var(name, expr.line, expr.col)
                    if expr.prefix:
                        if expr.op == "++":
                            self.emit("    adds x0, x0, #1")
                            self.emit("    adc x1, x1, xzr")
                        else:
                            self.emit("    subs x0, x0, #1")
                            self.emit("    sbc x1, x1, xzr")
                        self.store_var(name, line=expr.line, col=expr.col)
                    else:
                        # post: save original, compute new, store, return original
                        self.push_i128()
                        if expr.op == "++":
                            self.emit("    adds x0, x0, #1")
                            self.emit("    adc x1, x1, xzr")
                        else:
                            self.emit("    subs x0, x0, #1")
                            self.emit("    sbc x1, x1, xzr")
                        self.store_var(name, line=expr.line, col=expr.col)
                        self.pop_i128("x0", "x1")
                    return
                is_pointer = self.is_pointer_type(type_spec)
                is_fp = self.is_fp_type(type_spec)
                delta = self.element_size(type_spec) if is_pointer else 1
                self.load_var(name, expr.line, expr.col)
                if is_fp:
                    # fp ++ / -- : d0 has current value; use fadd/fsub with 1.0
                    import struct
                    bits = struct.unpack('<Q', struct.pack('<d', 1.0))[0]
                    lbl = self.float_literal_label(bits, 8)
                    fp_op = "fadd" if expr.op == "++" else "fsub"
                    if expr.prefix:
                        self.emit(f"    adrp x9, {lbl}@PAGE")
                        self.emit(f"    ldr d1, [x9, {lbl}@PAGEOFF]")
                        self.emit(f"    {fp_op} d0, d0, d1")
                        self.store_var(name, src_reg="d0", line=expr.line, col=expr.col)
                    else:
                        # post: save old d0, compute new, store, result = old
                        self.push_d0()      # push old d0
                        self.emit(f"    adrp x9, {lbl}@PAGE")
                        self.emit(f"    ldr d1, [x9, {lbl}@PAGEOFF]")
                        self.emit(f"    {fp_op} d0, d0, d1")
                        self.store_var(name, src_reg="d0", line=expr.line, col=expr.col)
                        self.pop_d0("d0")   # restore old value as result
                elif expr.prefix:
                    op = "add" if expr.op == "++" else "sub"
                    is_byte = self.is_byte_type(type_spec)
                    is_short = type_spec is not None and type_spec.base == "short" and not type_spec.is_pointer()
                    if is_pointer:
                        self.emit(f"    {op} x0, x0, #{delta}")
                        self.store_var(name, src_reg="x0", line=expr.line, col=expr.col)
                    elif is_byte:
                        self.emit(f"    {op} w0, w0, #1")
                        self.emit("    and w0, w0, #0xFF")
                        self.store_var(name, src_reg="w0", line=expr.line, col=expr.col)
                    elif is_short:
                        self.emit(f"    {op} w0, w0, #1")
                        self.emit("    and w0, w0, #0xFFFF")
                        self.store_var(name, src_reg="w0", line=expr.line, col=expr.col)
                    elif self.is_wide_scalar(type_spec):
                        self.emit(f"    {op} x0, x0, #1")
                        self.store_var(name, src_reg="x0", line=expr.line, col=expr.col)
                    else:
                        self.emit(f"    {op} w0, w0, #1")
                        self.store_var(name, src_reg="w0", line=expr.line, col=expr.col)
                else:
                    op = "add" if expr.op == "++" else "sub"
                    is_wide = self.is_wide_scalar(type_spec)
                    if is_pointer or is_wide:
                        self.emit("    mov x1, x0")
                        self.emit(f"    {op} x1, x1, #{delta}")
                        self.store_var(name, src_reg="x1", line=expr.line, col=expr.col)
                    else:
                        self.emit("    mov w1, w0")
                        self.emit(f"    {op} w1, w1, #1")
                        self.store_var(name, src_reg="w1", line=expr.line, col=expr.col)
                return
            # Non-Identifier target: MemberAccess, ArrayAccess, pointer deref
            # Compute address ONCE to avoid double evaluation of side effects (e.g. *s++)
            target_type = self.get_expr_type(expr.operand)
            is_pointer = self.is_pointer_type(target_type)
            delta = self.element_size(target_type) if is_pointer else 1
            wide = is_pointer or self.is_wide_scalar(target_type)
            is_byte = self.is_byte_type(target_type)
            is_short = target_type is not None and target_type.base == "short" and not target_type.is_pointer()
            op = "add" if expr.op == "++" else "sub"
            self.gen_lvalue_addr(expr.operand)  # x0 = address (side effects evaluated once)
            self.emit("    mov x9, x0")          # x9 = saved address
            if expr.prefix:
                if is_pointer or wide:
                    self.emit("    ldr x0, [x9]")
                    self.emit(f"    {op} x0, x0, #{delta}")
                    self.emit("    str x0, [x9]")
                elif is_byte:
                    self.emit("    ldrb w0, [x9]")
                    self.emit(f"    {op} w0, w0, #1")
                    self.emit("    and w0, w0, #0xFF")
                    self.emit("    strb w0, [x9]")
                elif is_short:
                    self.emit("    ldrh w0, [x9]")
                    self.emit(f"    {op} w0, w0, #1")
                    self.emit("    and w0, w0, #0xFFFF")
                    self.emit("    strh w0, [x9]")
                else:
                    self.emit("    ldr w0, [x9]")
                    self.emit(f"    {op} w0, w0, #1")
                    self.emit("    str w0, [x9]")
            else:
                # Post: load original, save it, compute new value, store, return original
                if is_pointer or wide:
                    self.emit("    ldr x0, [x9]")
                    self.push_x0()
                    self.emit(f"    {op} x0, x0, #{delta}")
                    self.emit("    str x0, [x9]")
                elif is_byte:
                    self.emit("    ldrb w0, [x9]")
                    self.push_x0()
                    self.emit(f"    {op} w0, w0, #1")
                    self.emit("    and w0, w0, #0xFF")
                    self.emit("    strb w0, [x9]")
                elif is_short:
                    self.emit("    ldrh w0, [x9]")
                    self.push_x0()
                    self.emit(f"    {op} w0, w0, #1")
                    self.emit("    and w0, w0, #0xFFFF")
                    self.emit("    strh w0, [x9]")
                else:
                    self.emit("    ldr w0, [x9]")
                    self.push_x0()
                    self.emit(f"    {op} w0, w0, #1")
                    self.emit("    str w0, [x9]")
                self.pop_reg("x0")  # return original value
            return

        # Address-of: just compute the lvalue address, no need to evaluate the operand first.
        if expr.op == "&":
            self.gen_lvalue_addr(expr.operand)
            return

        self.gen_expr(expr.operand)
        operand_type = self.get_expr_type(expr.operand)
        wide = self.is_wide_scalar(operand_type) or self.is_wide_scalar(self.get_expr_type(expr))

        if self.is_int128(operand_type):
            if expr.op == "-":
                self.emit("    subs x0, xzr, x0")
                self.emit("    sbc x1, xzr, x1")
            elif expr.op == "!":
                self.emit("    orr x0, x0, x1")
                self.emit("    cmp x0, #0")
                self.emit("    cset w0, eq")
            elif expr.op == "~":
                self.emit("    mvn x0, x0")
                self.emit("    mvn x1, x1")
            elif expr.op == "&":
                self.gen_lvalue_addr(expr.operand)
            else:
                self.error(f"unary '{expr.op}' not supported for __int128 on arm64-apple-darwin", expr.line, expr.col)
            return

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
            # Dereferencing a function pointer is a no-op in C (gives function designator)
            if (operand_type is not None and (
                    (operand_type.func_ptr_native_depth > 0 and
                     operand_type.pointer_depth == operand_type.func_ptr_native_depth)
                    or operand_type.is_func_ptr)):
                return
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
            elif operand_type is not None and self.is_fp_type(self.element_type(operand_type)):
                elem = self.element_type(operand_type)
                if elem.base == "float":
                    self.emit("    ldr s0, [x0]")
                    self.emit("    fcvt d0, s0")
                else:
                    self.emit("    ldr d0, [x0]")
            else:
                self.emit("    ldr w0, [x0]")
        else:
            self.error(f"unary operator '{expr.op}' is not yet supported on arm64-apple-darwin", expr.line, expr.col)

    def gen_ternary(self, expr: TernaryOp):
        false_label = self.new_label("ternfalse")
        end_label = self.new_label("ternend")
        self.gen_condition(expr.condition)
        self.emit(f"    cbz w0, {false_label}")
        true_type = self.get_expr_type(expr.true_expr)
        false_type = self.get_expr_type(expr.false_expr)
        need_fp = self.is_fp_type(true_type) or self.is_fp_type(false_type)
        self.gen_expr(expr.true_expr)
        if need_fp and not self.is_fp_type(true_type):
            if true_type is not None and true_type.is_unsigned:
                self.emit("    ucvtf d0, x0" if self.is_wide_scalar(true_type) else "    ucvtf d0, w0")
            else:
                self.emit("    scvtf d0, x0" if self.is_wide_scalar(true_type) else "    scvtf d0, w0")
        self.emit(f"    b {end_label}")
        self.label(false_label)
        self.gen_expr(expr.false_expr)
        if need_fp and not self.is_fp_type(false_type):
            if false_type is not None and false_type.is_unsigned:
                self.emit("    ucvtf d0, x0" if self.is_wide_scalar(false_type) else "    ucvtf d0, w0")
            else:
                self.emit("    scvtf d0, x0" if self.is_wide_scalar(false_type) else "    scvtf d0, w0")
        self.label(end_label)

    def gen_lvalue_addr(self, expr: Expr):
        if isinstance(expr, Identifier):
            if expr.name in self.locals:
                if expr.name in self.vla_ptr_locals:
                    self.emit_local_load("ldur", "x0", self.locals[expr.name])
                else:
                    self.emit_sub_reg_x29("x0", self.locals[expr.name])
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
        elif isinstance(expr, CastExpr) and isinstance(expr.operand, InitList):
            # Compound literal used as lvalue (e.g. &(S){...}).
            # Allocate stack space, initialize, return address. sp is NOT restored.
            target = expr.target_type
            if target is not None:
                size = self.total_size(target)
                alloc = (size + 15) & ~15
                # Compute the x29-relative negative base BEFORE emitting the sub, then add alloc.
                # x29_neg_base stays constant — use emit_sub_reg_x29 to recover the address
                # after any gen_expr call, even if gen_expr permanently lowers sp via nested
                # compound literals.  Also include _sw_stack_depth: any unbalanced software-stack
                # pushes (e.g. preceding call arguments) shift sp relative to x29.
                x29_neg_base = self.stack_size + self._sw_stack_depth + self._dyn_sp_offset + alloc
                self.emit(f"    sub sp, sp, #{alloc}")
                self._dyn_sp_offset += alloc
                if target.is_struct() and not target.is_pointer():
                    struct_def = target.struct_def
                    if struct_def is not None:
                        # Zero-initialize (sp-relative is fine here — no gen_expr yet)
                        byte_off = 0
                        while byte_off + 8 <= size:
                            self.emit(f"    str xzr, [sp, #{byte_off}]")
                            byte_off += 8
                        while byte_off + 4 <= size:
                            self.emit(f"    str wzr, [sp, #{byte_off}]")
                            byte_off += 4
                        while byte_off < size:
                            self.emit(f"    strb wzr, [sp, #{byte_off}]")
                            byte_off += 1
                        for i, item in enumerate(expr.operand.items):
                            if i >= len(struct_def.members) or item.value is None:
                                break
                            member = struct_def.members[i]
                            moff = struct_def.member_offset(member.name, self.target) or 0
                            mtype = member.type_spec
                            self.gen_expr(item.value)
                            # Recompute compound literal base via x29 (immune to sp changes)
                            self.emit_sub_reg_x29("x9", x29_neg_base)
                            msz = self.total_size(mtype) if mtype else 4
                            if self.is_fp_type(mtype):
                                self.emit(f"    str {'s0' if mtype and mtype.base == 'float' else 'd0'}, [x9, #{moff}]")
                            elif msz <= 1:
                                self.emit(f"    strb w0, [x9, #{moff}]")
                            elif msz <= 2:
                                self.emit(f"    strh w0, [x9, #{moff}]")
                            elif msz <= 4:
                                self.emit(f"    str w0, [x9, #{moff}]")
                            else:
                                self.emit(f"    str x0, [x9, #{moff}]")
                self.emit_sub_reg_x29("x0", x29_neg_base)
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
        typedef_map = getattr(self, 'typedef_map', {})
        # Resolve typedef for assoc: if assoc.base is a typedef name and pointer_depth=0,
        # replace assoc with the resolved TypeSpec (preserving any extra * from assoc).
        if assoc.base in typedef_map and typedef_map[assoc.base].type_spec is not None:
            resolved = typedef_map[assoc.base].type_spec
            # For function pointer typedefs used as bare names (pointer_depth=0 in assoc),
            # compare directly to the resolved type (which carries the pointer depth).
            if assoc.pointer_depth == 0:
                assoc = resolved
            else:
                # Extra indirection applied on top of a typedef.
                from copy import copy
                assoc = copy(resolved)
                assoc.pointer_depth += assoc.pointer_depth

        ctrl_const = controlling.is_const if controlling.pointer_depth > 0 else False
        if controlling.pointer_depth != assoc.pointer_depth:
            return False
        if controlling.is_unsigned != assoc.is_unsigned:
            return False
        if controlling.base != assoc.base:
            return False
        if ctrl_const != assoc.is_const:
            return False
        # If the association specifies an array type (e.g. int[4]), the controlling
        # expression must also be an array with the same dimensions.
        ctrl_arr = controlling.array_sizes
        assoc_arr = assoc.array_sizes
        if assoc_arr is not None and ctrl_arr is None:
            return False
        if ctrl_arr is not None and assoc_arr is None:
            return False
        return True

    def _arith_result_type(self, left_type, right_type):
        """Return the result type for integer arithmetic using C usual arithmetic conversions."""
        _RANK = {"char": 0, "short": 1, "int": 2, "long": 3, "long long": 4, "__int128": 5}
        if left_type is None and right_type is None:
            return TypeSpec(base="int")
        if left_type is None:
            return right_type
        if right_type is None:
            return left_type
        lr = _RANK.get(left_type.base, 2)
        rr = _RANK.get(right_type.base, 2)
        return left_type if lr >= rr else right_type

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
            self._sw_stack_depth += 16
            self.emit("    str x1, [sp, #-16]!")  # push base
            self._sw_stack_depth += 16
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
        elif self.is_fp_type(result_type):
            if result_type.base == "float":
                self.emit("    ldr s0, [x0]")
                self.emit("    fcvt d0, s0")
            else:
                self.emit("    ldr d0, [x0]")
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
        elif not expr.arrow and isinstance(expr.obj, FuncCall):
            # FuncCall: large-struct convention — x0 = address of struct.
            # Small structs (≤16 bytes) are handled inline in gen_member_access;
            # any non-inline case (e.g., lvalue of small struct from func) spills here.
            obj_sz = struct_type.struct_def.size_bytes(self.target) if struct_type.struct_def else 0
            self.gen_expr(expr.obj)
            if obj_sz <= 8:
                # x0 = bytes; spill to temp stack slot and use its address
                self.emit("    str x0, [sp, #-16]!")
                self.emit("    mov x0, sp")
            elif obj_sz <= 16:
                self.emit("    str x1, [sp, #-8]")
                self.emit("    str x0, [sp, #-16]!")
                self.emit("    mov x0, sp")
            # else: x0 already = address of struct (large-struct convention)
        else:
            self.gen_lvalue_addr(expr.obj)

        offset = struct_type.struct_def.member_offset(expr.member, self.target)
        if offset is None:
            self.error(f"unknown member '{expr.member}'", expr.line, expr.col)
        self.emit_add_reg_imm("x0", offset)

    def gen_member_access(self, expr: MemberAccess):
        # Special case: FuncCall returning a small struct (≤16 bytes).
        # Our convention: struct bytes are in x0 (≤8 bytes) or x0/x1 (9-16 bytes).
        # Don't spill to the stack (would corrupt staging area); extract directly from registers.
        if not expr.arrow and isinstance(expr.obj, FuncCall) and self._is_struct_by_reg_value(expr.obj):
            obj_type = self.get_expr_type(expr.obj)
            if obj_type is not None and obj_type.is_struct() and not obj_type.is_pointer():
                self.gen_expr(expr.obj)  # x0 (and x1 for >8 bytes) = struct bytes
                sdef = obj_type.struct_def
                member_type = self.get_expr_type(expr)
                offset = sdef.member_offset(expr.member, self.target)
                if offset is None:
                    self.error(f"unknown member '{expr.member}'", expr.line, expr.col)
                # If member is in the high half (offset ≥ 8), move x1 → x0
                if offset >= 8:
                    self.emit("    mov x0, x1")
                    bit_off = (offset - 8) * 8
                else:
                    bit_off = offset * 8
                if bit_off > 0:
                    self.emit(f"    lsr x0, x0, #{bit_off}")
                # Emit the appropriate type conversion
                if self.is_fp_type(member_type):
                    if member_type is not None and member_type.base == "float":
                        self.emit("    fmov s0, w0")
                        self.emit("    fcvt d0, s0")
                    else:  # double or long double (= double on macOS ARM64)
                        self.emit("    fmov d0, x0")
                elif member_type is not None and member_type.is_struct() and not member_type.is_pointer():
                    pass  # struct sub-member stays in x0 as bytes
                elif self.is_wide_scalar(member_type):
                    pass  # x0 already has 64-bit value
                elif self.is_byte_type(member_type):
                    self.emit("    and w0, w0, #0xff")
                elif member_type is not None and member_type.base == "short":
                    self.emit("    and w0, w0, #0xffff")
                # else: 32-bit value already in w0
                return

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

        # Compound literal with unsized array type: (T[]){...} — size from initializer count.
        if (not expr.is_type and self.is_array_type(type_spec)
                and any(d is None for d in (type_spec.array_sizes or []))
                and isinstance(expr.operand, CastExpr)
                and isinstance(expr.operand.operand, InitList)):
            n = len(expr.operand.operand.items)
            return max(1, type_spec.size_bytes(self.target) * n)

        return self.total_size(type_spec)

    def gen_sizeof(self, expr: SizeofExpr):
        # For VLA types (runtime-sized), emit runtime size computation.
        if expr.is_type:
            type_spec = expr.operand
        else:
            type_spec = self.get_expr_type(expr.operand)
        if type_spec is not None and self._has_vla_dim(type_spec):
            self._emit_runtime_size(type_spec)
            self.emit("    mov w0, w0")  # truncate to 32-bit result
        else:
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
                # For unsized array compound literals (struct T[]){...}, total_size returns
                # only one element's size; compute the real size from the InitList count.
                if self.is_array_type(target):
                    elem_type_pre = self.element_type(target)
                    elem_sz_pre = self.total_size(elem_type_pre)
                    n_items = len(expr.operand.items)
                    computed = elem_sz_pre * n_items
                    if computed > size:
                        size = computed
                alloc = (size + 15) & ~15
                # Track x29-relative base so x9 can be recomputed after any gen_expr
                # call (gen_expr may clobber x9 e.g. via adrp x9, _global@PAGE).
                x29_neg_base = self.stack_size + self._sw_stack_depth + self._dyn_sp_offset + alloc
                # Allocate temp space on stack dynamically
                self.emit(f"    sub sp, sp, #{alloc}")
                self._dyn_sp_offset += alloc
                self.emit(f"    mov x9, sp")
                if target.is_struct() and not target.is_pointer() and not self.is_array_type(target):
                    struct_def = target.struct_def
                    if struct_def is not None:
                        # Zero-initialize the whole struct so un-filled members are 0.
                        byte_off = 0
                        while byte_off + 8 <= size:
                            self.emit(f"    str xzr, [x9, #{byte_off}]")
                            byte_off += 8
                        while byte_off + 4 <= size:
                            self.emit(f"    str wzr, [x9, #{byte_off}]")
                            byte_off += 4
                        while byte_off < size:
                            self.emit(f"    strb wzr, [x9, #{byte_off}]")
                            byte_off += 1
                        for i, item in enumerate(expr.operand.items):
                            if i >= len(struct_def.members):
                                break
                            member = struct_def.members[i]
                            moff = struct_def.member_offset(member.name, self.target) or 0
                            mtype = member.type_spec
                            # Nested struct init: (struct S){1, 2, {3, 4}} where {3,4} is sub-array
                            if mtype is not None and self.is_array_type(mtype) and isinstance(item.value, InitList):
                                elem_type = self.element_type(mtype)
                                elem_sz = self.total_size(elem_type)
                                for ei, eitem in enumerate(item.value.items):
                                    if eitem.value is None:
                                        continue
                                    self.gen_expr(eitem.value)
                                    self.emit_sub_reg_x29("x9", x29_neg_base)
                                    eoff = moff + ei * elem_sz
                                    if elem_sz <= 1:
                                        self.emit(f"    strb w0, [x9, #{eoff}]")
                                    elif elem_sz <= 2:
                                        self.emit(f"    strh w0, [x9, #{eoff}]")
                                    elif elem_sz <= 4:
                                        self.emit(f"    str w0, [x9, #{eoff}]")
                                    else:
                                        self.emit(f"    str x0, [x9, #{eoff}]")
                                continue
                            if mtype is not None and mtype.is_struct() and not mtype.is_pointer() and isinstance(item.value, InitList):
                                sub_def = mtype.struct_def
                                if sub_def is not None:
                                    for si, sitem in enumerate(item.value.items):
                                        if si >= len(sub_def.members) or sitem.value is None:
                                            break
                                        smember = sub_def.members[si]
                                        soff = moff + (sub_def.member_offset(smember.name, self.target) or 0)
                                        self.gen_expr(sitem.value)
                                        self.emit_sub_reg_x29("x9", x29_neg_base)
                                        ssz = self.total_size(smember.type_spec) if smember.type_spec else 4
                                        if ssz <= 1:
                                            self.emit(f"    strb w0, [x9, #{soff}]")
                                        elif ssz <= 2:
                                            self.emit(f"    strh w0, [x9, #{soff}]")
                                        elif ssz <= 4:
                                            self.emit(f"    str w0, [x9, #{soff}]")
                                        else:
                                            self.emit(f"    str x0, [x9, #{soff}]")
                                continue
                            self.gen_expr(item.value)
                            self.emit_sub_reg_x29("x9", x29_neg_base)
                            msz = self.total_size(mtype) if mtype else 4
                            if msz <= 1:
                                self.emit(f"    strb w0, [x9, #{moff}]")
                            elif msz <= 2:
                                self.emit(f"    strh w0, [x9, #{moff}]")
                            elif msz <= 4:
                                self.emit(f"    str w0, [x9, #{moff}]")
                            else:
                                self.emit(f"    str x0, [x9, #{moff}]")
                    # Return struct by value if ≤ 16 bytes (recompute x9 first)
                    self.emit_sub_reg_x29("x9", x29_neg_base)
                    if size <= 8:
                        self.emit("    ldr x0, [x9]")
                    elif size <= 16:
                        self.emit("    ldr x0, [x9]")
                        self.emit("    ldr x1, [x9, #8]")
                    self.emit(f"    add sp, sp, #{alloc}")
                    self._dyn_sp_offset -= alloc
                    return
                elif self.is_array_type(target):
                    # For array compound literals, return address.
                    # Zero-initialise the whole region first.
                    byte_off = 0
                    while byte_off + 8 <= size:
                        self.emit_sub_reg_x29("x9", x29_neg_base - byte_off)
                        self.emit(f"    str xzr, [x9]")
                        byte_off += 8
                    elem_type = self.element_type(target)
                    elem_sz = self.total_size(elem_type)
                    is_struct_elem = (elem_type is not None and elem_type.is_struct()
                                      and not elem_type.is_pointer())
                    for i, item in enumerate(expr.operand.items):
                        if item.value is None:
                            continue
                        # x29-relative offset for this element's base
                        elem_neg = x29_neg_base - i * elem_sz
                        val = item.value
                        if is_struct_elem:
                            # Unwrap compound literal to its InitList if needed
                            init_val = (val.operand if isinstance(val, CastExpr) and isinstance(val.operand, InitList) else val)
                            if isinstance(init_val, InitList):
                                self.gen_struct_init_at_addr(elem_type, init_val, elem_neg)
                                continue
                            # Struct returned by address — memcpy into slot
                            self.gen_expr(val)
                            self.emit_sub_reg_x29("x9", elem_neg)
                            self.emit("    mov x1, x0")
                            self.emit("    mov x0, x9")
                            self.emit(f"    mov x2, #{elem_sz}")
                            self.emit("    bl _memcpy")
                        else:
                            self.gen_expr(val)
                            self.emit_sub_reg_x29("x9", x29_neg_base)
                            off = i * elem_sz
                            if elem_sz <= 1:
                                self.emit(f"    strb w0, [x9, #{off}]")
                            elif elem_sz <= 2:
                                self.emit(f"    strh w0, [x9, #{off}]")
                            elif elem_sz <= 4:
                                self.emit(f"    str w0, [x9, #{off}]")
                            else:
                                self.emit(f"    str x0, [x9, #{off}]")
                    self.emit_sub_reg_x29("x0", x29_neg_base)
                    # sp is NOT restored — array pointer stays valid on stack.
                    # _dyn_sp_offset already updated above.
                    return
                else:
                    self.emit(f"    add sp, sp, #{alloc}")
                    self._dyn_sp_offset -= alloc
            # Fallback: evaluate first element
            if expr.operand.items:
                self.gen_expr(expr.operand.items[0].value)
            return
        self.gen_expr(expr.operand)
        target = expr.target_type
        if target is None:
            return
        # Struct-to-struct cast: operand address already in x0, no conversion needed
        if target.is_struct() and not target.is_pointer():
            return
        source = self.get_expr_type(expr.operand)
        src_fp = self.is_fp_type(source)
        tgt_fp = self.is_fp_type(target)
        # Cast to __int128: widen if source is not already __int128
        if self.is_int128(target):
            if not self.is_int128(source):
                self.widen_to_i128(source)
            return
        # Cast from __int128: truncate to target (just use x0 lo, mask/sign if needed)
        if self.is_int128(source):
            if tgt_fp:
                if target.is_unsigned:
                    self.emit("    ucvtf d0, x0")
                else:
                    self.emit("    scvtf d0, x0")
                return
            # Truncate: target size from x0 (lo half)
            sz = target.size_bytes(self.target)
            if sz <= 1:
                if target.is_unsigned:
                    self.emit("    and w0, w0, #0xff")
                else:
                    self.emit("    sxtb w0, w0")
            elif sz <= 2:
                if target.is_unsigned:
                    self.emit("    and w0, w0, #0xffff")
                else:
                    self.emit("    sxth w0, w0")
            elif sz <= 4:
                self.emit("    mov w0, w0")
            # 8-byte: x0 already holds lo, no-op
            return
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
        if expr.wide:
            label = self.wide_string_label(expr.value)
        else:
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

            if fn in ("__builtin_popcount", "__builtin_popcountl", "__builtin_popcountll"):
                self.gen_expr(expr.args[0])
                if fn == "__builtin_popcount":
                    self.emit("    fmov s0, w0")
                else:
                    self.emit("    fmov d0, x0")
                self.emit("    cnt v0.8b, v0.8b")
                self.emit("    addv b0, v0.8b")
                self.emit("    umov w0, v0.b[0]")
                return

            if fn in ("__builtin_clz", "__builtin_clzl", "__builtin_clzll"):
                self.gen_expr(expr.args[0])
                if fn == "__builtin_clz":
                    self.emit("    clz w0, w0")
                else:
                    self.emit("    clz x0, x0")
                return

            if fn in ("__builtin_ctz", "__builtin_ctzl", "__builtin_ctzll"):
                self.gen_expr(expr.args[0])
                if fn == "__builtin_ctz":
                    self.emit("    rbit w0, w0")
                    self.emit("    clz w0, w0")
                else:
                    self.emit("    rbit x0, x0")
                    self.emit("    clz x0, x0")
                return

            if fn in ("__builtin_expect", "__builtin_expect_with_probability"):
                # __builtin_expect(expr, expected_val) - just evaluate the expr
                self.gen_expr(expr.args[0])
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
                            # 64-bit mul overflow: use smulh trick
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

        # A bare identifier that is not a local/global variable is treated as a direct external
        # call (implicit function declaration, K&R-style). If it IS a local/global variable, it's
        # a function pointer and we load it at runtime.
        if isinstance(expr.name, Identifier):
            name = expr.name.name
            if name in self.functions or (name not in self.locals and name not in self.globals):
                direct_name = name
            else:
                direct_name = None
        else:
            direct_name = None
        func_decl = self.functions.get(direct_name) if direct_name is not None else None
        fixed_arg_count = len(func_decl.params) if func_decl is not None else len(expr.args)
        # Apple arm64: variadic args go on the stack; fixed args go in x0-x7 / d0-d7
        stack_varargs = func_decl is not None and func_decl.is_variadic and len(expr.args) > fixed_arg_count

        # Fallback: recognize well-known variadic C functions called without a declaration
        # (K&R style or no #includes). Without this, args would go in registers instead of on
        # the stack, violating the Apple ARM64 variadic ABI.
        if not stack_varargs and direct_name is not None and func_decl is None:
            _KNOWN_VARIADICS = {
                'printf': 1, 'fprintf': 2, 'sprintf': 2, 'snprintf': 3,
                'scanf': 1, 'fscanf': 2, 'sscanf': 2, 'dprintf': 2,
                'asprintf': 2, 'wprintf': 1, 'fwprintf': 2, 'swprintf': 3,
                'vprintf': 2, 'vfprintf': 3, 'vsprintf': 3, 'vsnprintf': 4,
            }
            if direct_name in _KNOWN_VARIADICS:
                known_fixed = _KNOWN_VARIADICS[direct_name]
                if len(expr.args) > known_fixed:
                    fixed_arg_count = known_fixed
                    stack_varargs = True

        # For indirect (function pointer) calls, check if the callee TypeSpec has variadic info.
        if not stack_varargs and direct_name is None:
            callee_expr_for_type = expr.name
            while isinstance(callee_expr_for_type, UnaryOp) and callee_expr_for_type.op == "*":
                callee_expr_for_type = callee_expr_for_type.operand
            callee_ts = None
            if isinstance(callee_expr_for_type, Identifier):
                cname = callee_expr_for_type.name
                cdecl = self.locals.get(cname) or self.globals.get(cname)
                if cdecl is not None and hasattr(cdecl, 'type_spec'):
                    callee_ts = cdecl.type_spec
            if callee_ts is None:
                callee_ts = self.get_expr_type(callee_expr_for_type)
            if (callee_ts is not None and callee_ts.func_ptr_is_variadic
                    and callee_ts.func_ptr_param_count is not None):
                fixed_arg_count = callee_ts.func_ptr_param_count
                stack_varargs = len(expr.args) > fixed_arg_count

        # Only limit fixed args to 8; variadic extras go on the stack
        max_reg_args = fixed_arg_count if stack_varargs else len(expr.args)
        stack_bytes = 0
        temp_arg_bytes = len(expr.args) * 16

        # Save software-stack depth before any arg pushes so we can restore it after cleanup.
        # Paths that use raw `add sp, sp, #N` (stack_varargs, overflow) don't call pop_reg
        # and so don't automatically decrement _sw_stack_depth.
        _sw_depth_before = self._sw_stack_depth
        _dyn_off_before = self._dyn_sp_offset

        fp_staging_top = None
        if direct_name is None:
            # (*fp)(args) is equivalent to fp(args) in C: strip no-op dereferences of
            # function pointers (pointer_depth==1, no further dereference needed).
            # Also strip * wrapping a FuncCall result — calling a func that returns a
            # function pointer and immediately calling it: (*(*p)(...))(...)
            callee_expr = expr.name
            while (isinstance(callee_expr, UnaryOp) and callee_expr.op == "*"):
                inner_type = self.get_expr_type(callee_expr.operand)
                if (inner_type is not None and (inner_type.pointer_depth == 1 or inner_type.is_func_ptr)
                        or isinstance(callee_expr.operand, FuncCall)):
                    callee_expr = callee_expr.operand
                else:
                    break
            self.gen_expr(callee_expr)
            self.push_x0()
            fp_staging_top = self._sw_stack_depth + self._dyn_sp_offset

        # Evaluate all args, pushing them on the stack.
        # For struct ≤ 8 bytes: load the bytes (ldr x0/w0) before pushing.
        # For struct 9-16 bytes: push address + a sentinel so pop knows to use 2 regs.
        # FP args spill as d0.
        # arg_staging_tops[i] = sw_stack_depth + dyn_sp_offset right after pushing arg i.
        # This is used to compute correct offsets from x10 (= sp after all pushes) since
        # compound literal allocations between arg pushes make the staging non-contiguous.
        arg_staging_tops = []
        arg_types = []
        for i, arg in enumerate(expr.args):
            a_type = self.get_expr_type(arg)
            # Check if the declared param type requires __int128 widening
            param_type = (func_decl.params[i].type_spec
                          if func_decl is not None and i < len(func_decl.params)
                          else None)
            if param_type is not None and self.is_int128(param_type) and not self.is_int128(a_type):
                # Widen non-__int128 arg to __int128 for this parameter
                self.gen_expr(arg)
                self.widen_to_i128(a_type)
                self.push_i128()
                arg_types.append(param_type)
                arg_staging_tops.append(self._sw_stack_depth + self._dyn_sp_offset)
                continue
            arg_types.append(a_type)
            self.gen_expr(arg)
            # Coerce argument to match declared parameter type (e.g. int→double, double→int).
            if param_type is not None and a_type is not None:
                param_is_fp = self.is_fp_type(param_type) and not param_type.is_pointer()
                arg_is_fp = self.is_fp_type(a_type) and not a_type.is_pointer()
                if param_is_fp and not arg_is_fp:
                    # int/long → float/double: result is in x0/w0, convert to d0
                    if param_type.base == "float":
                        self.emit("    scvtf s0, x0")
                        self.emit("    fcvt d0, s0")
                    else:
                        self.emit("    scvtf d0, x0")
                    a_type = param_type
                elif not param_is_fp and arg_is_fp:
                    # float/double → int/long: result is in d0, convert to x0
                    size = param_type.size_bytes(self.target) if param_type else 8
                    if size <= 4:
                        self.emit("    fcvtzs w0, d0")
                    else:
                        self.emit("    fcvtzs x0, d0")
                    a_type = param_type
                elif (not param_is_fp and not arg_is_fp
                        and self.is_wide_scalar(param_type) and not param_type.is_unsigned
                        and not self.is_wide_scalar(a_type) and not a_type.is_pointer()
                        and not a_type.is_unsigned):
                    # signed int/short/char → long/long long: sign-extend to 64 bits
                    expr_size = a_type.size_bytes(self.target)
                    if expr_size <= 1:
                        self.emit("    sxtb w0, w0")
                    elif expr_size <= 2:
                        self.emit("    sxth w0, w0")
                    self.emit("    sxtw x0, w0")
                    a_type = param_type
            # Update arg_types with the post-coercion type (may differ from pre-coercion).
            arg_types[-1] = a_type
            if self.is_int128(a_type):
                self.push_i128()
            elif self.is_fp_type(a_type):
                self.push_d0()
            elif (a_type is not None and a_type.is_struct() and not a_type.is_pointer() and not self.is_array_type(a_type)):
                struct_size = a_type.struct_def.size_bytes(self.target)
                if self._is_struct_by_reg_value(arg):
                    # gen_expr already put bytes in x0[/x1]
                    if struct_size > 8:
                        # push x1 first (high), then x0 (low) so pop order is: x0 low, x1 high
                        self.emit("    str x1, [sp, #-16]!")
                        self._sw_stack_depth += 16
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
                        self._sw_stack_depth += 16
                        self.push_x0()                        # push low bytes
                    else:
                        self.push_x0()  # pass address for large structs
            else:
                self.push_x0()
            arg_staging_tops.append(self._sw_stack_depth + self._dyn_sp_offset)

        # Compute actual offsets from x10 (= sp after all arg pushes) to each arg.
        # This accounts for compound literal allocations between arg pushes making
        # the staging stack non-contiguous.
        final_sp_total = self._sw_stack_depth + self._dyn_sp_offset
        actual_staging_offs = [final_sp_total - t for t in arg_staging_tops]

        if not stack_varargs and max_reg_args > 8:
            # Non-variadic call with >8 args: args 0-7 go in x0-x7, args 8+ on the stack.
            n = len(expr.args)
            stack_count = n - 8
            nonvariadic_stack_bytes = (stack_count * 8 + 15) & ~15
            self.emit("    mov x10, sp")
            self.emit(f"    sub sp, sp, #{nonvariadic_stack_bytes}")
            # Copy extra args (indices 8..n-1) from software stack to hardware stack
            for i in range(8, n):
                sw_off = actual_staging_offs[i]
                hw_off = (i - 8) * 8
                self.emit(f"    ldr x9, [x10, #{sw_off}]")
                self.emit(f"    str x9, [sp, #{hw_off}]")
            # Load first 8 args from software stack into x0-x7 / d0-d7 (reverse order)
            for i in range(7, -1, -1):
                sw_off = actual_staging_offs[i]
                a_type = arg_types[i] if i < len(arg_types) else None
                if self.is_fp_type(a_type):
                    self.emit(f"    ldr d{i}, [x10, #{sw_off}]")
                else:
                    self.emit(f"    ldr {self.ARG_REGS_64[i]}, [x10, #{sw_off}]")
            if direct_name is not None:
                self.emit(f"    bl {self.mangle(direct_name)}")
            else:
                # Function pointer was pushed before all args: use fp_staging_top offset
                fp_off = final_sp_total - fp_staging_top
                self.emit(f"    ldr x16, [x10, #{fp_off}]")
                self.emit("    blr x16")
            extra = 16 if direct_name is None else 0
            self.emit(f"    add sp, sp, #{nonvariadic_stack_bytes + temp_arg_bytes + extra}")
            self._sw_stack_depth = _sw_depth_before
            self._dyn_sp_offset = _dyn_off_before
            return
        elif stack_varargs:
            stack_count = len(expr.args) - fixed_arg_count
            stack_bytes = (stack_count * 8 + 15) & ~15
            self.emit("    mov x10, sp")
            self.emit(f"    sub sp, sp, #{stack_bytes}")
            # Copy variadic args to stack slots [sp+0], [sp+8], ...
            # Use actual_staging_offs to handle non-contiguous staging (e.g. compound literals
            # allocated between arg pushes shift the earlier args further from x10).
            for index in range(len(expr.args) - 1, fixed_arg_count - 1, -1):
                offset = actual_staging_offs[index]
                self.emit(f"    ldr x9, [x10, #{offset}]")
                self.emit(f"    str x9, [sp, #{(index - fixed_arg_count) * 8}]")
            # Load fixed args into registers
            for index in range(fixed_arg_count - 1, -1, -1):
                offset = actual_staging_offs[index]
                a_type = arg_types[index] if index < len(arg_types) else None
                if self.is_fp_type(a_type):
                    self.emit(f"    ldr d{index}, [x10, #{offset}]")
                else:
                    self.emit(f"    ldr {self.ARG_REGS_64[index]}, [x10, #{offset}]")
        else:
            # Non-variadic: assign registers with hardware-stack spill when register count > 8.
            # reg_assigns entries: ('int'|'fp'|'i128'|'struct2', reg_idx)
            #                   or ('stack'|'fp_stack'|'struct2_stack', stack_slot_idx)
            int_idx = 0
            fp_idx = 0
            stack_slot = 0  # 8-byte hardware stack slots consumed by overflowed args
            reg_assigns = []
            staging_sizes = []  # bytes each arg occupies in software staging stack

            for a_type in arg_types:
                if self.is_int128(a_type):
                    if int_idx + 2 <= 8:
                        reg_assigns.append(('i128', int_idx))
                        int_idx += 2
                    else:
                        reg_assigns.append(('stack', stack_slot))
                        stack_slot += 2  # __int128 = 16 bytes on call stack = 2 slots
                    staging_sizes.append(32)  # pushed as two 16-byte staging entries
                elif self.is_fp_type(a_type):
                    if fp_idx < 8:
                        reg_assigns.append(('fp', fp_idx))
                        fp_idx += 1
                    else:
                        reg_assigns.append(('fp_stack', stack_slot))
                        stack_slot += 1
                    staging_sizes.append(16)
                elif (a_type is not None and a_type.is_struct() and not a_type.is_pointer()
                      and not self.is_array_type(a_type)
                      and 8 < a_type.struct_def.size_bytes(self.target) <= 16):
                    # 9-16 byte struct: 2 integer registers, or call stack when exhausted
                    if int_idx + 2 <= 8:
                        reg_assigns.append(('struct2', int_idx))
                        int_idx += 2
                    else:
                        reg_assigns.append(('struct2_stack', stack_slot))
                        stack_slot += 2  # 9-16 bytes on call stack = 2 slots
                    staging_sizes.append(32)  # pushed as two 16-byte staging entries
                else:
                    if int_idx < 8:
                        reg_assigns.append(('int', int_idx))
                        int_idx += 1
                    else:
                        reg_assigns.append(('stack', stack_slot))
                        stack_slot += 1
                    staging_sizes.append(16)

            if stack_slot > 0:
                # Some args overflow the 8-register limit; copy them to the hardware call stack.
                # Use ldr/str (not pop) so we can address the staging area from a saved sp.
                hw_stack_bytes = (stack_slot * 8 + 15) & ~15
                # Use actual_staging_offs for correct offsets when compound literals
                # were allocated between arg pushes (non-contiguous staging stack).
                # staging_offs[i] = actual offset from x10 (= sp) to arg i's low bytes.
                # For i128/struct2 args, high bytes are at staging_offs[i] + 16.
                staging_offs = actual_staging_offs
                total_staging = final_sp_total - (self._sw_stack_depth + self._dyn_sp_offset - final_sp_total + final_sp_total)
                # total bytes to pop = all sw bytes pushed during arg evaluation
                total_staging = final_sp_total - (self._sw_stack_depth + self._dyn_sp_offset - final_sp_total) if False else \
                    (actual_staging_offs[-1] + staging_sizes[-1]) if actual_staging_offs else 0
                # Compute as max extent of staging area from x10
                if actual_staging_offs and staging_sizes:
                    total_staging = max(actual_staging_offs[i] + staging_sizes[i]
                                        for i in range(len(actual_staging_offs)))
                else:
                    total_staging = 0
                self.emit("    mov x10, sp")
                self.emit(f"    sub sp, sp, #{hw_stack_bytes}")
                # Copy stack-spilled args from staging area to hardware call stack
                for index in range(len(expr.args)):
                    kind, idx = reg_assigns[index]
                    s_off = staging_offs[index]
                    if kind == 'stack':
                        self.emit(f"    ldr x9, [x10, #{s_off}]")
                        self.emit(f"    str x9, [sp, #{idx * 8}]")
                    elif kind == 'fp_stack':
                        self.emit(f"    ldr d8, [x10, #{s_off}]")
                        self.emit(f"    str d8, [sp, #{idx * 8}]")
                    elif kind == 'struct2_stack':
                        self.emit(f"    ldr x9, [x10, #{s_off}]")
                        self.emit(f"    str x9, [sp, #{idx * 8}]")
                        self.emit(f"    ldr x9, [x10, #{s_off + 16}]")
                        self.emit(f"    str x9, [sp, #{idx * 8 + 8}]")
                # Load register args from staging area into call registers
                for index in range(len(expr.args)):
                    kind, idx = reg_assigns[index]
                    s_off = staging_offs[index]
                    if kind == 'fp':
                        self.emit(f"    ldr d{idx}, [x10, #{s_off}]")
                    elif kind == 'i128':
                        self.emit(f"    ldr {self.ARG_REGS_64[idx]}, [x10, #{s_off}]")
                        self.emit(f"    ldr {self.ARG_REGS_64[idx + 1]}, [x10, #{s_off + 16}]")
                    elif kind == 'struct2':
                        self.emit(f"    ldr {self.ARG_REGS_64[idx]}, [x10, #{s_off}]")
                        self.emit(f"    ldr {self.ARG_REGS_64[idx + 1]}, [x10, #{s_off + 16}]")
                    elif kind == 'int':
                        self.emit(f"    ldr {self.ARG_REGS_64[idx]}, [x10, #{s_off}]")
                if direct_name is not None:
                    self.emit(f"    bl {self.mangle(direct_name)}")
                else:
                    fp_off = final_sp_total - fp_staging_top
                    self.emit(f"    ldr x16, [x10, #{fp_off}]")
                    self.emit("    blr x16")
                extra = 16 if direct_name is None else 0
                self.emit(f"    add sp, sp, #{hw_stack_bytes + total_staging + extra}")
                return

            # No overflow: pop args in reverse order into registers
            for index in range(len(expr.args) - 1, -1, -1):
                kind, idx = reg_assigns[index]
                if kind == 'fp':
                    self.pop_d0(f"d{idx}")
                elif kind == 'i128':
                    self.pop_i128(self.ARG_REGS_64[idx], self.ARG_REGS_64[idx + 1])
                elif kind == 'struct2':
                    # low bytes in x{idx}, high bytes in x{idx+1}
                    self.pop_reg(self.ARG_REGS_64[idx])         # pop low (x0 first)
                    self.pop_reg(self.ARG_REGS_64[idx + 1])     # pop high (x1)
                else:
                    self.pop_reg(self.ARG_REGS_64[idx])

        if direct_name is not None:
            self.emit(f"    bl {self.mangle(direct_name)}")
        elif stack_varargs:
            # For indirect variadic calls: the function pointer sits in the staging area.
            # Use fp_staging_top to compute correct offset from x10.
            fp_off = final_sp_total - fp_staging_top
            self.emit(f"    ldr x16, [x10, #{fp_off}]")
            self.emit("    blr x16")
        else:
            self.pop_reg("x16")
            self.emit("    blr x16")
        if stack_bytes:
            # For indirect variadic calls we didn't pop the function pointer; add its 16 bytes too.
            extra = 16 if (direct_name is None and stack_varargs) else 0
            self.emit(f"    add sp, sp, #{stack_bytes + temp_arg_bytes + extra}")
            # Restore sw_stack_depth: the raw add sp doesn't go through pop_reg, so it
            # doesn't auto-decrement _sw_stack_depth. Reset to pre-call depth so that
            # any outer call staging (e.g. printf(fmt, f(args))) computes correct offsets.
            self._sw_stack_depth = _sw_depth_before
            self._dyn_sp_offset = _dyn_off_before

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
