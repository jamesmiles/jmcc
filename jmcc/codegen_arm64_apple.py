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
    DoWhileStmt,
    Expr,
    ExprStmt,
    ForStmt,
    FuncCall,
    FuncDecl,
    GlobalVarDecl,
    GotoStmt,
    Identifier,
    IfStmt,
    IntLiteral,
    LabelStmt,
    NullStmt,
    Program,
    ReturnStmt,
    Stmt,
    SwitchStmt,
    TernaryOp,
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
        self.globals: Dict[str, GlobalVarDecl] = {}
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

    def slot_size(self, type_spec) -> int:
        if type_spec is not None and type_spec.is_array():
            size = type_spec.size_bytes(self.target)
            for dim in type_spec.array_sizes or []:
                if isinstance(dim, IntLiteral):
                    size *= dim.value
            return (size + 7) & ~7
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
        return type_spec is not None and type_spec.is_array()

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

    def generate(self, program: Program) -> str:
        self.globals = {
            decl.name: decl
            for decl in program.declarations
            if isinstance(decl, GlobalVarDecl)
        }

        self.emit("    .text")
        for decl in program.declarations:
            if isinstance(decl, FuncDecl) and decl.body is not None:
                self.gen_function(decl)
            elif not isinstance(decl, (FuncDecl, GlobalVarDecl)):
                self.error(
                    f"arm64-apple-darwin backend does not yet support top-level declaration type {type(decl).__name__}",
                    getattr(decl, "line", 0),
                    getattr(decl, "col", 0),
                )

        for decl in self.globals.values():
            if decl.init is not None and not isinstance(decl.init, IntLiteral):
                self.error(
                    "arm64-apple-darwin backend only supports integer literal global initializers",
                    decl.line,
                    decl.col,
                )

            self.emit("")
            self.emit("    .data")
            self.emit("    .p2align 2")
            self.emit(f"    .globl {self.mangle(decl.name)}")
            self.label(self.mangle(decl.name))
            self.emit(f"    .long {decl.init.value if decl.init is not None else 0}")
        return "\n".join(self.output) + "\n"

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
            elif self.is_pointer_type(type_spec):
                self.emit(f"    ldur x0, [x29, #-{self.locals[name]}]")
            else:
                self.emit(f"    ldur w0, [x29, #-{self.locals[name]}]")
            return
        if name in self.globals:
            mangled = self.mangle(name)
            self.emit(f"    adrp x9, {mangled}@PAGE")
            if self.is_pointer_type(type_spec):
                self.emit(f"    ldr x0, [x9, {mangled}@PAGEOFF]")
            else:
                self.emit(f"    ldr w0, [x9, {mangled}@PAGEOFF]")
            return
        self.error(f"undefined variable '{name}'", line, col)

    def store_var(self, name: str, src_reg=None, line=0, col=0):
        type_spec = self.get_var_type(name)
        if src_reg is None:
            src_reg = "x0" if self.is_pointer_type(type_spec) else "w0"
        if name in self.locals:
            self.emit(f"    stur {src_reg}, [x29, #-{self.locals[name]}]")
            return
        if name in self.globals:
            mangled = self.mangle(name)
            self.emit(f"    adrp x9, {mangled}@PAGE")
            self.emit(f"    str {src_reg}, [x9, {mangled}@PAGEOFF]")
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
        if decl.type_spec is not None and decl.type_spec.is_array() and decl.init is None:
            return
        if decl.init is None:
            self.emit("    mov w0, #0")
        else:
            self.gen_expr(decl.init)
        self.store_var(decl.name, line=decl.line, col=decl.col)

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
            self.emit(f"    mov w0, #{expr.value}")
        elif isinstance(expr, Identifier):
            self.load_var(expr.name, expr.line, expr.col)
        elif isinstance(expr, ArrayAccess):
            self.gen_array_access(expr)
        elif isinstance(expr, Assignment):
            self.gen_assignment(expr)
        elif isinstance(expr, BinaryOp):
            self.gen_binary_op(expr)
        elif isinstance(expr, UnaryOp):
            self.gen_unary_op(expr)
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
            self.error("only simple assignments are currently supported on arm64-apple-darwin", expr.line, expr.col)
        self.gen_expr(expr.value)
        if isinstance(expr.target, Identifier):
            self.store_var(expr.target.name, line=expr.line, col=expr.col)
            return

        if isinstance(expr.target, (UnaryOp, ArrayAccess)):
            self.push_x0()
            self.gen_lvalue_addr(expr.target)
            self.pop_reg("x1")
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

        if expr.op == "+":
            self.emit("    add w0, w1, w0")
        elif expr.op == "-":
            self.emit("    sub w0, w1, w0")
        elif expr.op == "*":
            self.emit("    mul w0, w1, w0")
        elif expr.op == "/":
            self.emit("    sdiv w0, w1, w0")
        elif expr.op == "%":
            self.emit("    sdiv w2, w1, w0")
            self.emit("    msub w0, w2, w0, w1")
        elif expr.op == "&":
            self.emit("    and w0, w1, w0")
        elif expr.op == "|":
            self.emit("    orr w0, w1, w0")
        elif expr.op == "^":
            self.emit("    eor w0, w1, w0")
        elif expr.op == "<<":
            self.emit("    lslv w0, w1, w0")
        elif expr.op == ">>":
            self.emit("    asrv w0, w1, w0")
        elif expr.op in {"==", "!=", "<", "<=", ">", ">="}:
            self.emit("    cmp w1, w0")
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
        self.gen_expr(expr.operand)

        if expr.op == "-":
            self.emit("    neg w0, w0")
        elif expr.op == "!":
            self.emit("    cmp w0, #0")
            self.emit("    cset w0, eq")
        elif expr.op == "~":
            self.emit("    mvn w0, w0")
        elif expr.op == "&":
            self.gen_lvalue_addr(expr.operand)
        elif expr.op == "*":
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
            if expr.name in self.globals:
                mangled = self.mangle(expr.name)
                self.emit(f"    adrp x0, {mangled}@PAGE")
                self.emit(f"    add x0, x0, {mangled}@PAGEOFF")
                return
            self.error(f"undefined variable '{expr.name}'", expr.line, expr.col)
        elif isinstance(expr, UnaryOp) and expr.op == "*":
            self.gen_expr(expr.operand)
            return
        elif isinstance(expr, ArrayAccess):
            self.gen_array_addr(expr)
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
            self.gen_expr(expr.array)

        self.push_x0()
        self.gen_expr(expr.index)
        self.emit("    sxtw x0, w0")
        self.pop_reg("x1")

        if isinstance(expr.array, Identifier):
            elem_size = self.element_size(self.get_var_type(expr.array.name))
        else:
            elem_size = 4

        if elem_size != 1:
            self.emit(f"    mov x2, #{elem_size}")
            self.emit("    mul x0, x0, x2")
        self.emit("    add x0, x1, x0")

    def gen_array_access(self, expr: ArrayAccess):
        self.gen_array_addr(expr)
        self.emit("    ldr w0, [x0]")

    def gen_func_call(self, expr: FuncCall):
        if not isinstance(expr.name, Identifier):
            self.error("only direct function calls are currently supported on arm64-apple-darwin", expr.line, expr.col)
        if len(expr.args) > len(self.ARG_REGS_64):
            self.error("more than 8 integer call arguments are not yet supported on arm64-apple-darwin", expr.line, expr.col)

        for arg in expr.args:
            self.gen_expr(arg)
            self.push_x0()

        for index in range(len(expr.args) - 1, -1, -1):
            self.pop_reg(self.ARG_REGS_64[index])

        self.emit(f"    bl {self.mangle(expr.name.name)}")
