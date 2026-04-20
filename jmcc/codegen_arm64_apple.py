"""Minimal arm64 Apple Darwin code generator for hosted JMCC tests."""

from typing import Dict, List, Optional

from .ast_nodes import (
    Assignment,
    BinaryOp,
    Block,
    Expr,
    ExprStmt,
    ForStmt,
    FuncCall,
    FuncDecl,
    Identifier,
    IfStmt,
    IntLiteral,
    Program,
    ReturnStmt,
    Stmt,
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
        self.stack_size = 0
        self.return_label: Optional[str] = None
        self.current_func: Optional[FuncDecl] = None

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

    def generate(self, program: Program) -> str:
        self.emit("    .text")
        for decl in program.declarations:
            if isinstance(decl, FuncDecl) and decl.body is not None:
                self.gen_function(decl)
            elif not isinstance(decl, FuncDecl):
                self.error(
                    f"arm64-apple-darwin backend does not yet support top-level declaration type {type(decl).__name__}",
                    getattr(decl, "line", 0),
                    getattr(decl, "col", 0),
                )
        return "\n".join(self.output) + "\n"

    def alloc_slot(self, name: str):
        if name in self.locals:
            return
        self.stack_size += 8
        self.locals[name] = self.stack_size

    def collect_locals_stmt(self, stmt: Stmt):
        if isinstance(stmt, Block):
            for child in stmt.stmts:
                self.collect_locals_stmt(child)
        elif isinstance(stmt, VarDecl):
            self.alloc_slot(stmt.name)
        elif isinstance(stmt, IfStmt):
            self.collect_locals_stmt(stmt.then_body)
            if stmt.else_body is not None:
                self.collect_locals_stmt(stmt.else_body)
        elif isinstance(stmt, WhileStmt):
            self.collect_locals_stmt(stmt.body)
        elif isinstance(stmt, ForStmt):
            if stmt.init is not None:
                self.collect_locals_stmt(stmt.init)
            self.collect_locals_stmt(stmt.body)
        elif isinstance(stmt, (ReturnStmt, ExprStmt)):
            return
        else:
            self.error(
                f"arm64-apple-darwin backend does not yet support statement type {type(stmt).__name__}",
                stmt.line,
                stmt.col,
            )

    def prepare_function(self, func: FuncDecl):
        self.locals = {}
        self.stack_size = 0
        for param in func.params:
            self.alloc_slot(param.name)
        self.collect_locals_stmt(func.body)
        self.stack_size = (self.stack_size + 15) & ~15

    def load_var(self, name: str, line=0, col=0):
        if name not in self.locals:
            self.error(f"undefined variable '{name}'", line, col)
        self.emit(f"    ldur w0, [x29, #-{self.locals[name]}]")

    def store_var(self, name: str, src_reg="w0", line=0, col=0):
        if name not in self.locals:
            self.error(f"undefined variable '{name}'", line, col)
        self.emit(f"    stur {src_reg}, [x29, #-{self.locals[name]}]")

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
            self.store_var(param.name, src_reg=self.ARG_REGS_32[index], line=func.line, col=func.col)

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
        elif isinstance(stmt, ForStmt):
            self.gen_for(stmt)
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
        self.label(start_label)
        self.gen_expr(stmt.condition)
        self.emit(f"    cbz w0, {end_label}")
        self.gen_stmt(stmt.body)
        self.emit(f"    b {start_label}")
        self.label(end_label)

    def gen_for(self, stmt: ForStmt):
        cond_label = self.new_label("for")
        update_label = self.new_label("forupd")
        end_label = self.new_label("forend")

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

    def gen_expr(self, expr: Expr):
        if isinstance(expr, IntLiteral):
            self.emit(f"    mov w0, #{expr.value}")
        elif isinstance(expr, Identifier):
            self.load_var(expr.name, expr.line, expr.col)
        elif isinstance(expr, Assignment):
            self.gen_assignment(expr)
        elif isinstance(expr, BinaryOp):
            self.gen_binary_op(expr)
        elif isinstance(expr, UnaryOp):
            self.gen_unary_op(expr)
        elif isinstance(expr, FuncCall):
            self.gen_func_call(expr)
        else:
            self.error(
                f"arm64-apple-darwin backend does not yet support expression type {type(expr).__name__}",
                expr.line,
                expr.col,
            )

    def gen_assignment(self, expr: Assignment):
        if expr.op != "=" or not isinstance(expr.target, Identifier):
            self.error("only simple identifier assignments are currently supported on arm64-apple-darwin", expr.line, expr.col)
        self.gen_expr(expr.value)
        self.store_var(expr.target.name, line=expr.line, col=expr.col)

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
        else:
            self.error(f"unary operator '{expr.op}' is not yet supported on arm64-apple-darwin", expr.line, expr.col)

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
