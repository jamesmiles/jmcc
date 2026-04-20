"""Minimal arm64 Apple Darwin code generator for hosted JMCC tests."""

from typing import Dict, List, Optional

from .ast_nodes import (
    ArrayAccess,
    Assignment,
    BinaryOp,
    Block,
    BreakStmt,
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
    GlobalVarDecl,
    GotoStmt,
    Identifier,
    IfStmt,
    IntLiteral,
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
        self.break_labels: List[str] = []
        self.continue_labels: List[str] = []

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

    def static_local_label(self, name: str) -> str:
        func_name = self.current_func.name if self.current_func is not None else "global"
        return f"Lstatic_{func_name}_{name}"

    def string_label(self, value: str) -> str:
        if value not in self.string_literals:
            self.string_literals[value] = self.new_label("str")
        return self.string_literals[value]

    def escape_string(self, value: str) -> str:
        return (
            value.replace("\\", "\\\\")
            .replace("\n", "\\n")
            .replace("\t", "\\t")
            .replace("\"", "\\\"")
        )

    def slot_size(self, type_spec) -> int:
        if type_spec is not None and self.is_array_type(type_spec):
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

    def is_pointer_type(self, type_spec) -> bool:
        return type_spec is not None and type_spec.is_pointer()

    def is_array_type(self, type_spec) -> bool:
        return type_spec is not None and (type_spec.is_array() or type_spec.is_ptr_array)

    def element_size(self, type_spec) -> int:
        if type_spec is None:
            return 4
        if type_spec.is_array():
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
        return max(1, size)

    def clone_type(self, type_spec, pointer_depth=None, array_sizes=...):
        if type_spec is None:
            return None
        return TypeSpec(
            base=type_spec.base,
            pointer_depth=type_spec.pointer_depth if pointer_depth is None else pointer_depth,
            is_unsigned=type_spec.is_unsigned,
            array_sizes=type_spec.array_sizes if array_sizes is ... else array_sizes,
            struct_def=type_spec.struct_def,
            enum_def=type_spec.enum_def,
        )

    def emit_symbol_addr(self, symbol: str, reg: str = "x0"):
        self.emit(f"    adrp {reg}, {symbol}@PAGE")
        self.emit(f"    add {reg}, {reg}, {symbol}@PAGEOFF")

    def is_wide_scalar(self, type_spec) -> bool:
        return type_spec is not None and not type_spec.is_pointer() and not self.is_array_type(type_spec) and type_spec.size_bytes(self.target) > 4

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
            return self.clone_type(type_spec, array_sizes=None)
        if type_spec.is_pointer():
            return self.clone_type(type_spec, pointer_depth=max(type_spec.pointer_depth - 1, 0), array_sizes=None)
        return None

    def get_expr_type(self, expr: Expr):
        if isinstance(expr, Identifier):
            var_type = self.get_var_type(expr.name)
            if var_type is not None:
                return var_type
            if expr.name in self.functions:
                return TypeSpec(base="void", pointer_depth=1)
            return None
        if isinstance(expr, IntLiteral):
            if self.literal_is_wide(expr):
                return TypeSpec(base="long long")
            return TypeSpec(base="int")
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
                return self.clone_type(operand_type, pointer_depth=max(operand_type.pointer_depth - 1, 0))
            if expr.op in {"-", "~"} and operand_type is not None:
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
            return left_type or right_type or TypeSpec(base="int")
        if isinstance(expr, SizeofExpr):
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
        return "\n".join(self.output) + "\n"

    def emit_global_decl(self, label: str, type_spec, init, line: int, col: int, exported: bool = True):
        self.emit("")
        self.emit("    .data")
        self.emit("    .p2align 2")
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

        if isinstance(init, InitList) and type_spec is not None and self.is_array_type(type_spec):
            self.emit_global_array_init(type_spec, init, line, col)
            return

        self.error(
            "arm64-apple-darwin backend does not yet support this global initializer",
            line,
            col,
        )

    def emit_global_array_init(self, type_spec, init: InitList, line: int, col: int):
        elem_type = self.element_type(type_spec)
        count = type_spec.array_sizes[0].value if type_spec.array_sizes and isinstance(type_spec.array_sizes[0], IntLiteral) else len(init.items)
        for index in range(count):
            item = init.items[index].value if index < len(init.items) else None
            self.emit_global_value(elem_type, item, line, col)

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
            data = bytearray(type_spec.struct_def.size_bytes(self.target))
            for member, item in zip(type_spec.struct_def.members, value.items):
                member_value = item.value
                offset = type_spec.struct_def.member_offset(member.name) or 0
                member_type = member.type_spec
                if self.is_array_type(member_type) and member_type.base == "char" and isinstance(member_value, StringLiteral):
                    raw = member_value.value.encode("utf-8") + b"\0"
                    limit = self.total_size(member_type)
                    raw = raw[:limit] + b"\0" * max(0, limit - len(raw))
                    data[offset:offset + limit] = raw[:limit]
                elif isinstance(member_value, (IntLiteral, CharLiteral)):
                    size = member_type.size_bytes(self.target)
                    intval = member_value.value if isinstance(member_value, IntLiteral) else ord(member_value.value)
                    data[offset:offset + size] = int(intval & ((1 << (size * 8)) - 1)).to_bytes(size, "little", signed=False)
                else:
                    self.error("arm64-apple-darwin backend does not yet support this struct global initializer", line, col)
            for byte in data:
                self.emit(f"    .byte {byte}")
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
        self.error("arm64-apple-darwin backend does not yet support this global initializer value", line, col)

    def alloc_slot(self, name: str, type_spec=None):
        if name in self.locals:
            return
        self.stack_size += self.slot_size(type_spec)
        self.locals[name] = self.stack_size
        self.local_types[name] = type_spec

    def collect_locals_stmt(self, stmt: Stmt):
        if isinstance(stmt, Block):
            for child in stmt.stmts:
                self.collect_locals_stmt(child)
        elif isinstance(stmt, VarDecl):
            self.infer_unsized_array(stmt.type_spec, stmt.init)
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
        elif isinstance(stmt, (ReturnStmt, ExprStmt, BreakStmt, ContinueStmt, GotoStmt, NullStmt)):
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
        self.stack_size = 0
        for param in func.params:
            self.alloc_slot(param.name, param.type_spec)
        self.collect_locals_stmt(func.body)
        self.stack_size = (self.stack_size + 15) & ~15

    def load_var(self, name: str, line=0, col=0):
        type_spec = self.get_var_type(name)
        if name in self.locals:
            if self.is_array_type(type_spec):
                self.emit(f"    sub x0, x29, #{self.locals[name]}")
            elif type_spec is not None and type_spec.is_struct() and not type_spec.is_pointer():
                self.emit(f"    sub x0, x29, #{self.locals[name]}")
            elif self.is_pointer_type(type_spec):
                self.emit(f"    ldur x0, [x29, #-{self.locals[name]}]")
            elif type_spec is not None and type_spec.base == "short":
                self.emit(f"    ldurh w0, [x29, #-{self.locals[name]}]" if type_spec.is_unsigned else f"    ldursh w0, [x29, #-{self.locals[name]}]")
            elif self.is_wide_scalar(type_spec):
                self.emit(f"    ldur x0, [x29, #-{self.locals[name]}]")
            else:
                self.emit(f"    ldur w0, [x29, #-{self.locals[name]}]")
            return
        if name in self.static_locals:
            label = self.static_locals[name]
            self.emit_symbol_addr(label, "x9")
            if self.is_array_type(type_spec) or (type_spec is not None and type_spec.is_struct() and not type_spec.is_pointer()):
                self.emit("    mov x0, x9")
            elif self.is_pointer_type(type_spec):
                self.emit("    ldr x0, [x9]")
            elif type_spec is not None and type_spec.base == "short":
                self.emit("    ldrh w0, [x9]" if type_spec.is_unsigned else "    ldrsh w0, [x9]")
            elif self.is_wide_scalar(type_spec):
                self.emit("    ldr x0, [x9]")
            elif type_spec is not None and type_spec.base == "char":
                self.emit("    ldrb w0, [x9]")
            else:
                self.emit("    ldr w0, [x9]")
            return
        if name in self.globals:
            mangled = self.mangle(name)
            self.emit_symbol_addr(mangled, "x9")
            if self.is_array_type(type_spec) or (type_spec is not None and type_spec.is_struct() and not type_spec.is_pointer()):
                self.emit("    mov x0, x9")
            elif self.is_pointer_type(type_spec):
                self.emit("    ldr x0, [x9]")
            elif type_spec is not None and type_spec.base == "short":
                self.emit("    ldrh w0, [x9]" if type_spec.is_unsigned else "    ldrsh w0, [x9]")
            elif self.is_wide_scalar(type_spec):
                self.emit("    ldr x0, [x9]")
            elif type_spec is not None and type_spec.base == "char":
                self.emit("    ldrb w0, [x9]")
            else:
                self.emit("    ldr w0, [x9]")
            return
        if name in self.functions:
            self.emit_symbol_addr(self.mangle(name))
            return
        self.error(f"undefined variable '{name}'", line, col)

    def store_var(self, name: str, src_reg=None, line=0, col=0):
        type_spec = self.get_var_type(name)
        if src_reg is None:
            src_reg = "x0" if self.is_pointer_type(type_spec) or self.is_wide_scalar(type_spec) else "w0"
        if name in self.locals:
            if type_spec is not None and type_spec.base == "char" and not type_spec.is_pointer():
                self.emit(f"    sturb {src_reg}, [x29, #-{self.locals[name]}]")
            elif type_spec is not None and type_spec.base == "short" and not type_spec.is_pointer():
                self.emit(f"    sturh {src_reg}, [x29, #-{self.locals[name]}]")
            else:
                self.emit(f"    stur {src_reg}, [x29, #-{self.locals[name]}]")
            return
        if name in self.static_locals:
            label = self.static_locals[name]
            self.emit_symbol_addr(label, "x9")
            if type_spec is not None and type_spec.base == "char" and not type_spec.is_pointer():
                self.emit(f"    strb {src_reg}, [x9]")
            elif type_spec is not None and type_spec.base == "short" and not type_spec.is_pointer():
                self.emit(f"    strh {src_reg}, [x9]")
            else:
                self.emit(f"    str {src_reg}, [x9]")
            return
        if name in self.globals:
            mangled = self.mangle(name)
            self.emit_symbol_addr(mangled, "x9")
            if type_spec is not None and type_spec.base == "char" and not type_spec.is_pointer():
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

    def gen_function(self, func: FuncDecl):
        if func.is_variadic:
            self.error("variadic functions are not yet supported on arm64-apple-darwin", func.line, func.col)
        if len(func.params) > len(self.ARG_REGS_32):
            self.error("more than 8 integer parameters are not yet supported on arm64-apple-darwin", func.line, func.col)

        self.current_func = func
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

        for index, param in enumerate(func.params):
            arg_reg = self.ARG_REGS_64[index] if self.is_pointer_type(param.type_spec) else self.ARG_REGS_32[index]
            self.store_var(param.name, src_reg=arg_reg, line=func.line, col=func.col)

        self.gen_block(func.body)
        self.emit("    mov w0, #0")
        self.label(self.return_label)
        if self.stack_size:
            self.emit(f"    add sp, sp, #{self.stack_size}")
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
        self.emit(f"    b {self.return_label}")

    def gen_var_decl(self, decl: VarDecl):
        if decl.type_spec is not None and decl.type_spec.is_static:
            return
        if decl.type_spec is not None and self.is_array_type(decl.type_spec) and isinstance(decl.init, InitList):
            self.gen_local_array_init(decl)
            return
        if decl.type_spec is not None and decl.init is None:
            if decl.type_spec.is_array() or (decl.type_spec.is_struct() and not decl.type_spec.is_pointer()):
                return
        if decl.init is None:
            self.emit("    mov w0, #0")
        else:
            self.gen_expr(decl.init)
        self.store_var(decl.name, line=decl.line, col=decl.col)

    def gen_local_array_init(self, decl: VarDecl):
        self.emit(f"    sub x9, x29, #{self.locals[decl.name]}")
        elem_type = self.element_type(decl.type_spec)
        elem_size = self.total_size(elem_type)
        for index, item in enumerate(decl.init.items):
            value = item.value
            if value is None:
                continue
            self.gen_expr(value)
            offset = index * elem_size
            if elem_type is not None and self.is_pointer_type(elem_type):
                self.emit(f"    str x0, [x9, #{offset}]")
            elif elem_type is not None and elem_type.base == "char" and not elem_type.is_pointer():
                self.emit(f"    strb w0, [x9, #{offset}]")
            elif elem_type is not None and elem_type.base == "short" and not elem_type.is_pointer():
                self.emit(f"    strh w0, [x9, #{offset}]")
            else:
                self.emit(f"    str w0, [x9, #{offset}]")

    def gen_if(self, stmt: IfStmt):
        else_label = self.new_label("else")
        end_label = self.new_label("ifend")
        self.gen_expr(stmt.condition)
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
        self.gen_expr(stmt.condition)
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
        self.gen_expr(stmt.condition)
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
            self.gen_expr(stmt.condition)
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
            if not isinstance(value, IntLiteral):
                self.error("arm64-apple-darwin switch currently requires integer literal case labels", case_stmt.line, case_stmt.col)
            self.emit(f"    cmp w10, #{value.value}")
            self.emit(f"    b.eq {label}")

        self.emit(f"    b {default_label or end_label}")
        self.gen_stmt(stmt.body)
        self.label(end_label)
        self.break_labels.pop()

    def gen_expr(self, expr: Expr):
        if isinstance(expr, IntLiteral):
            self.emit_int_constant(expr.value, "x0" if self.literal_is_wide(expr) else "w0")
        elif isinstance(expr, FloatLiteral):
            self.error("floating-point expressions are not yet supported on arm64-apple-darwin", expr.line, expr.col)
        elif isinstance(expr, Identifier):
            self.load_var(expr.name, expr.line, expr.col)
        elif isinstance(expr, CastExpr):
            self.gen_cast(expr)
        elif isinstance(expr, CommaExpr):
            self.gen_comma(expr)
        elif isinstance(expr, StringLiteral):
            self.gen_string_literal(expr)
        elif isinstance(expr, SizeofExpr):
            self.gen_sizeof(expr)
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
        elif isinstance(expr, FuncCall):
            self.gen_func_call(expr)
        else:
            self.error(
                f"arm64-apple-darwin backend does not yet support expression type {type(expr).__name__}",
                expr.line,
                expr.col,
            )

    def gen_assignment(self, expr: Assignment):
        if expr.op != "=":
            if not isinstance(expr.target, Identifier):
                self.error("compound assignments currently require identifier targets on arm64-apple-darwin", expr.line, expr.col)
            self.load_var(expr.target.name, expr.line, expr.col)
            self.push_x0()
            self.gen_expr(expr.value)
            self.pop_reg("x1")

            op = expr.op[:-1]
            if op == "+":
                self.emit("    add w0, w1, w0")
            elif op == "-":
                self.emit("    sub w0, w1, w0")
            elif op == "*":
                self.emit("    mul w0, w1, w0")
            elif op == "/":
                self.emit("    sdiv w0, w1, w0")
            elif op == "%":
                self.emit("    sdiv w2, w1, w0")
                self.emit("    msub w0, w2, w0, w1")
            elif op == "&":
                self.emit("    and w0, w1, w0")
            elif op == "|":
                self.emit("    orr w0, w1, w0")
            elif op == "^":
                self.emit("    eor w0, w1, w0")
            elif op == "<<":
                self.emit("    lslv w0, w1, w0")
            elif op == ">>":
                self.emit("    asrv w0, w1, w0")
            else:
                self.error(f"compound assignment '{expr.op}' is not yet supported on arm64-apple-darwin", expr.line, expr.col)

            self.store_var(expr.target.name, line=expr.line, col=expr.col)
            return

        self.gen_expr(expr.value)
        if isinstance(expr.target, Identifier):
            self.store_var(expr.target.name, line=expr.line, col=expr.col)
            return

        if isinstance(expr.target, (UnaryOp, ArrayAccess, MemberAccess)):
            self.push_x0()
            self.gen_lvalue_addr(expr.target)
            self.pop_reg("x1")
            target_type = self.get_expr_type(expr.target)
            if target_type is not None and target_type.is_pointer():
                self.emit("    str x1, [x0]")
                self.emit("    mov x0, x1")
            elif target_type is not None and target_type.base == "char" and not target_type.is_pointer():
                self.emit("    strb w1, [x0]")
                self.emit("    and w0, w1, #0xff")
            elif target_type is not None and target_type.base == "short" and not target_type.is_pointer():
                self.emit("    strh w1, [x0]")
                self.emit("    and w0, w1, #0xffff")
            elif self.is_wide_scalar(target_type):
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
            self.gen_expr(expr.left)
            self.emit(f"    cbz w0, {false_label}")
            self.gen_expr(expr.right)
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
            self.gen_expr(expr.left)
            self.emit(f"    cbnz w0, {true_label}")
            self.gen_expr(expr.right)
            self.emit(f"    cbnz w0, {true_label}")
            self.emit("    mov w0, #0")
            self.emit(f"    b {end_label}")
            self.label(true_label)
            self.emit("    mov w0, #1")
            self.label(end_label)
            return

        self.gen_expr(expr.left)
        self.push_x0()
        self.gen_expr(expr.right)
        self.pop_reg("x1")

        left_type = self.get_expr_type(expr.left)
        right_type = self.get_expr_type(expr.right)
        left_ptr = left_type is not None and left_type.is_pointer()
        right_ptr = right_type is not None and right_type.is_pointer()
        result_type = self.get_expr_type(expr)
        wide = self.is_wide_scalar(left_type) or self.is_wide_scalar(right_type) or self.is_wide_scalar(result_type)

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
            self.emit("    sdiv x0, x1, x0" if wide else "    sdiv w0, w1, w0")
        elif expr.op == "%":
            if wide:
                self.emit("    sdiv x2, x1, x0")
                self.emit("    msub x0, x2, x0, x1")
            else:
                self.emit("    sdiv w2, w1, w0")
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
            self.emit("    asrv x0, x1, x0" if wide else "    asrv w0, w1, w0")
        elif expr.op in {"==", "!=", "<", "<=", ">", ">="}:
            self.emit("    cmp x1, x0" if (left_ptr or right_ptr or wide) else "    cmp w1, w0")
            cond = {
                "==": "eq",
                "!=": "ne",
                "<": "lt",
                "<=": "le",
                ">": "gt",
                ">=": "ge",
            }[expr.op]
            self.emit(f"    cset w0, {cond}")
        else:
            self.error(f"binary operator '{expr.op}' is not yet supported on arm64-apple-darwin", expr.line, expr.col)

    def gen_unary_op(self, expr: UnaryOp):
        if expr.op in {"++", "--"}:
            if not isinstance(expr.operand, Identifier):
                self.error(f"unary operator '{expr.op}' currently requires an identifier operand on arm64-apple-darwin", expr.line, expr.col)

            name = expr.operand.name
            type_spec = self.get_var_type(name)
            is_pointer = self.is_pointer_type(type_spec)
            delta = self.element_size(type_spec) if is_pointer else 1
            self.load_var(name, expr.line, expr.col)

            if expr.prefix:
                if is_pointer:
                    op = "add" if expr.op == "++" else "sub"
                    self.emit(f"    {op} x0, x0, #{delta}")
                    self.store_var(name, src_reg="x0", line=expr.line, col=expr.col)
                else:
                    op = "add" if expr.op == "++" else "sub"
                    self.emit(f"    {op} w0, w0, #1")
                    self.store_var(name, src_reg="w0", line=expr.line, col=expr.col)
            else:
                if is_pointer:
                    self.emit("    mov x1, x0")
                    op = "add" if expr.op == "++" else "sub"
                    self.emit(f"    {op} x1, x1, #{delta}")
                    self.store_var(name, src_reg="x1", line=expr.line, col=expr.col)
                else:
                    self.emit("    mov w1, w0")
                    op = "add" if expr.op == "++" else "sub"
                    self.emit(f"    {op} w1, w1, #1")
                    self.store_var(name, src_reg="w1", line=expr.line, col=expr.col)
            return

        self.gen_expr(expr.operand)
        operand_type = self.get_expr_type(expr.operand)
        wide = self.is_wide_scalar(operand_type) or self.is_wide_scalar(self.get_expr_type(expr))

        if expr.op == "-":
            self.emit("    neg x0, x0" if wide else "    neg w0, w0")
        elif expr.op == "!":
            self.emit("    cmp x0, #0" if wide else "    cmp w0, #0")
            self.emit("    cset w0, eq")
        elif expr.op == "~":
            self.emit("    mvn x0, x0" if wide else "    mvn w0, w0")
        elif expr.op == "&":
            self.gen_lvalue_addr(expr.operand)
        elif expr.op == "*":
            if operand_type is not None and operand_type.base == "char" and operand_type.pointer_depth == 1:
                self.emit("    ldrb w0, [x0]")
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
        self.gen_expr(expr.condition)
        self.emit(f"    cbz w0, {false_label}")
        self.gen_expr(expr.true_expr)
        self.emit(f"    b {end_label}")
        self.label(false_label)
        self.gen_expr(expr.false_expr)
        self.label(end_label)

    def gen_lvalue_addr(self, expr: Expr):
        if isinstance(expr, Identifier):
            if expr.name in self.locals:
                self.emit(f"    sub x0, x29, #{self.locals[expr.name]}")
                return
            if expr.name in self.static_locals:
                self.emit_symbol_addr(self.static_locals[expr.name])
                return
            if expr.name in self.globals:
                self.emit_symbol_addr(self.mangle(expr.name))
                return
            if expr.name in self.functions:
                self.emit_symbol_addr(self.mangle(expr.name))
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
        self.error("expression is not an lvalue", expr.line, expr.col)

    def gen_array_addr(self, expr: ArrayAccess):
        if isinstance(expr.array, Identifier):
            array_type = self.get_var_type(expr.array.name)
            if self.is_array_type(array_type):
                self.gen_lvalue_addr(expr.array)
            else:
                self.gen_expr(expr.array)
        else:
            array_type = self.get_expr_type(expr.array)
            if self.is_array_type(array_type):
                self.gen_lvalue_addr(expr.array)
            else:
                self.gen_expr(expr.array)

        self.push_x0()
        self.gen_expr(expr.index)
        self.emit("    sxtw x0, w0")
        self.pop_reg("x1")

        elem_type = self.element_type(array_type)
        elem_size = self.total_size(elem_type)

        if elem_size != 1:
            self.emit(f"    mov x2, #{elem_size}")
            self.emit("    mul x0, x0, x2")
        self.emit("    add x0, x1, x0")

    def gen_array_access(self, expr: ArrayAccess):
        self.gen_array_addr(expr)
        result_type = self.get_expr_type(expr)
        if result_type is not None and result_type.base == "char" and not result_type.is_pointer():
            self.emit("    ldrb w0, [x0]")
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
        self.gen_member_addr(expr)
        member_type = self.get_expr_type(expr)
        if member_type is not None and member_type.is_struct() and not member_type.is_pointer():
            return
        if member_type is not None and self.is_array_type(member_type):
            return
        if member_type is not None and member_type.base == "char" and not member_type.is_pointer():
            self.emit("    ldrb w0, [x0]")
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

    def gen_cast(self, expr: CastExpr):
        self.gen_expr(expr.operand)
        target = expr.target_type
        if target is None:
            return
        source = self.get_expr_type(expr.operand)
        if target.is_pointer():
            return
        size = target.size_bytes(self.target)
        if size > 4:
            if source is not None and not source.is_pointer() and source.size_bytes(self.target) <= 4:
                self.emit("    uxtw x0, w0" if source.is_unsigned else "    sxtw x0, w0")
            return
        if size <= 1:
            self.emit("    and w0, w0, #0xff")
        elif size <= 2:
            self.emit("    and w0, w0, #0xffff")
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
        if len(expr.args) > len(self.ARG_REGS_64):
            self.error("more than 8 integer call arguments are not yet supported on arm64-apple-darwin", expr.line, expr.col)

        direct_name = expr.name.name if isinstance(expr.name, Identifier) and expr.name.name in self.functions else None
        func_decl = self.functions.get(direct_name) if direct_name is not None else None
        fixed_arg_count = len(func_decl.params) if func_decl is not None else len(expr.args)
        stack_varargs = func_decl is not None and func_decl.is_variadic and len(expr.args) > fixed_arg_count
        stack_bytes = 0
        temp_arg_bytes = len(expr.args) * 16

        if direct_name is None:
            self.gen_expr(expr.name)
            self.push_x0()

        for arg in expr.args:
            self.gen_expr(arg)
            self.push_x0()

        if stack_varargs:
            stack_count = len(expr.args) - fixed_arg_count
            stack_bytes = (stack_count * 8 + 15) & ~15
            self.emit("    mov x10, sp")
            self.emit(f"    sub sp, sp, #{stack_bytes}")
            for index in range(len(expr.args) - 1, fixed_arg_count - 1, -1):
                offset = (len(expr.args) - 1 - index) * 16
                self.emit(f"    ldr x9, [x10, #{offset}]")
                self.emit(f"    str x9, [sp, #{(index - fixed_arg_count) * 8}]")
            for index in range(fixed_arg_count - 1, -1, -1):
                offset = (len(expr.args) - 1 - index) * 16
                self.emit(f"    ldr {self.ARG_REGS_64[index]}, [x10, #{offset}]")
        else:
            for index in range(fixed_arg_count - 1, -1, -1):
                self.pop_reg(self.ARG_REGS_64[index])

        if direct_name is not None:
            self.emit(f"    bl {self.mangle(direct_name)}")
        else:
            self.pop_reg("x16")
            self.emit("    blr x16")
        if stack_bytes:
            self.emit(f"    add sp, sp, #{stack_bytes + temp_arg_bytes}")
