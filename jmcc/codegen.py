"""JMCC Code Generator - Emits x86-64 assembly (AT&T syntax) for Linux."""

from typing import List, Dict, Optional, Tuple
from .ast_nodes import *
from .errors import CodeGenError


class CodeGen:
    """Generates x86-64 assembly from an AST."""

    # System V AMD64 ABI: integer args in rdi, rsi, rdx, rcx, r8, r9
    ARG_REGS_64 = ["%rdi", "%rsi", "%rdx", "%rcx", "%r8", "%r9"]
    ARG_REGS_32 = ["%edi", "%esi", "%edx", "%ecx", "%r8d", "%r9d"]
    ARG_REGS_8 = ["%dil", "%sil", "%dl", "%cl", "%r8b", "%r9b"]

    def __init__(self):
        self.output: List[str] = []
        self.string_literals: List[Tuple[str, str]] = []  # (label, value)
        self.global_vars: Dict[str, GlobalVarDecl] = {}
        self.label_count = 0
        self.break_labels: List[str] = []  # stack of break target labels
        self.continue_labels: List[str] = []  # stack of continue target labels

        # Current function state
        self.locals: Dict[str, Tuple[int, TypeSpec]] = {}  # name -> (stack_offset, type)
        self.params: Dict[str, Tuple[int, TypeSpec]] = {}
        self.stack_offset = 0
        self.current_func: Optional[FuncDecl] = None

    def error(self, msg, line=0, col=0):
        raise CodeGenError(msg, line=line, col=col)

    def emit(self, line: str):
        self.output.append(line)

    def comment(self, text: str):
        self.emit(f"    # {text}")

    def label(self, name: str):
        self.emit(f"{name}:")

    def new_label(self, prefix="L") -> str:
        self.label_count += 1
        return f".{prefix}{self.label_count}"

    def generate(self, program: Program) -> str:
        self.emit("    .text")

        # First pass: collect globals and string literals
        for decl in program.declarations:
            if isinstance(decl, GlobalVarDecl):
                self.global_vars[decl.name] = decl
            elif isinstance(decl, FuncDecl) and decl.body is None:
                pass  # forward declaration

        # Generate functions
        for decl in program.declarations:
            if isinstance(decl, FuncDecl) and decl.body is not None:
                self.gen_function(decl)

        # Generate string literals
        if self.string_literals:
            self.emit("")
            self.emit("    .section .rodata")
            for lbl, val in self.string_literals:
                self.label(lbl)
                # Escape for assembly
                escaped = val.replace("\\", "\\\\").replace('"', '\\"')
                # Handle actual control characters
                asm_str = ""
                for ch in val:
                    if ch == '\n':
                        asm_str += "\\n"
                    elif ch == '\t':
                        asm_str += "\\t"
                    elif ch == '\r':
                        asm_str += "\\r"
                    elif ch == '\0':
                        asm_str += "\\0"
                    elif ch == '"':
                        asm_str += '\\"'
                    elif ch == '\\':
                        asm_str += "\\\\"
                    elif ord(ch) < 32 or ord(ch) > 126:
                        asm_str += f"\\{ord(ch):03o}"
                    else:
                        asm_str += ch
                self.emit(f'    .string "{asm_str}"')

        # Generate global variables
        if self.global_vars:
            for name, decl in self.global_vars.items():
                self.emit("")
                if decl.init and isinstance(decl.init, IntLiteral):
                    self.emit("    .data")
                    self.emit(f"    .globl {name}")
                    size = decl.type_spec.size_bytes()
                    if size == 8:
                        self.emit(f"    .align 8")
                    else:
                        self.emit(f"    .align 4")
                    self.label(name)
                    if size == 1:
                        self.emit(f"    .byte {decl.init.value}")
                    elif size == 2:
                        self.emit(f"    .word {decl.init.value}")
                    elif size == 4:
                        self.emit(f"    .long {decl.init.value}")
                    else:
                        self.emit(f"    .quad {decl.init.value}")
                else:
                    self.emit("    .bss")
                    self.emit(f"    .globl {name}")
                    size = decl.type_spec.size_bytes()
                    if decl.type_spec.is_array() and decl.type_spec.array_sizes:
                        first = decl.type_spec.array_sizes[0]
                        if isinstance(first, IntLiteral):
                            size *= first.value
                    # Alignment must be a power of 2, based on element type
                    align = min(decl.type_spec.size_bytes(), 8)
                    if align < 4:
                        align = 4
                    self.emit(f"    .align {align}")
                    self.label(name)
                    self.emit(f"    .zero {size}")

        return "\n".join(self.output) + "\n"

    def gen_function(self, func: FuncDecl):
        self.current_func = func
        self.locals = {}
        self.params = {}
        self.stack_offset = 0

        self.emit("")
        self.emit(f"    .globl {func.name}")
        self.emit(f"    .type {func.name}, @function")
        self.label(func.name)

        # Prologue
        self.emit("    pushq %rbp")
        self.emit("    movq %rsp, %rbp")

        # We'll patch the stack allocation later
        stack_alloc_idx = len(self.output)
        self.emit("    subq $PLACEHOLDER, %rsp")  # placeholder

        # Save parameters to stack
        for i, param in enumerate(func.params):
            size = param.type_spec.size_bytes()
            self.stack_offset -= 8  # align to 8 bytes
            self.params[param.name] = (self.stack_offset, param.type_spec)
            if i < 6:
                reg = self.ARG_REGS_64[i] if size == 8 else self.ARG_REGS_32[i]
                if size <= 4:
                    self.emit(f"    movl {self.ARG_REGS_32[i]}, {self.stack_offset}(%rbp)")
                else:
                    self.emit(f"    movq {self.ARG_REGS_64[i]}, {self.stack_offset}(%rbp)")
            else:
                # Parameter on stack: at 16 + (i-6)*8 (%rbp)
                stack_param_offset = 16 + (i - 6) * 8
                self.emit(f"    movq {stack_param_offset}(%rbp), %rax")
                self.emit(f"    movq %rax, {self.stack_offset}(%rbp)")

        # Generate body
        self.gen_block(func.body)

        # Default return 0 for main, or just ret for void functions
        if func.name == "main":
            self.emit("    movl $0, %eax")
        self.emit("    leave")
        self.emit("    ret")

        # Patch stack allocation (align to 16)
        total_stack = (-self.stack_offset + 15) & ~15
        if total_stack == 0:
            total_stack = 16  # minimum
        self.output[stack_alloc_idx] = f"    subq ${total_stack}, %rsp"

    def gen_block(self, block: Block):
        for stmt in block.stmts:
            self.gen_stmt(stmt)

    def gen_stmt(self, stmt: Stmt):
        if isinstance(stmt, ReturnStmt):
            self.gen_return(stmt)
        elif isinstance(stmt, ExprStmt):
            self.gen_expr(stmt.expr)
        elif isinstance(stmt, VarDecl):
            self.gen_var_decl(stmt)
        elif isinstance(stmt, Block):
            self.gen_block(stmt)
        elif isinstance(stmt, IfStmt):
            self.gen_if(stmt)
        elif isinstance(stmt, WhileStmt):
            self.gen_while(stmt)
        elif isinstance(stmt, DoWhileStmt):
            self.gen_do_while(stmt)
        elif isinstance(stmt, ForStmt):
            self.gen_for(stmt)
        elif isinstance(stmt, BreakStmt):
            if not self.break_labels:
                self.error("break outside loop/switch", stmt.line, stmt.col)
            self.emit(f"    jmp {self.break_labels[-1]}")
        elif isinstance(stmt, ContinueStmt):
            if not self.continue_labels:
                self.error("continue outside loop", stmt.line, stmt.col)
            self.emit(f"    jmp {self.continue_labels[-1]}")
        elif isinstance(stmt, SwitchStmt):
            self.gen_switch(stmt)
        elif isinstance(stmt, CaseStmt):
            # handled by gen_switch
            pass
        elif isinstance(stmt, GotoStmt):
            self.emit(f"    jmp .Luser_{stmt.label}")
        elif isinstance(stmt, LabelStmt):
            self.label(f".Luser_{stmt.label}")
            self.gen_stmt(stmt.stmt)
        elif isinstance(stmt, NullStmt):
            pass
        else:
            self.error(f"unhandled statement type: {type(stmt).__name__}", stmt.line, stmt.col)

    def gen_return(self, stmt: ReturnStmt):
        if stmt.value:
            self.gen_expr(stmt.value)
            # Result is in %rax/%eax already
        self.emit("    leave")
        self.emit("    ret")

    def gen_var_decl(self, decl: VarDecl):
        size = decl.type_spec.size_bytes()

        if decl.type_spec.is_array() and decl.type_spec.array_sizes:
            first = decl.type_spec.array_sizes[0]
            if isinstance(first, IntLiteral):
                elem_size = size
                if decl.type_spec.is_struct():
                    elem_size = decl.type_spec.struct_def.size_bytes()
                total = elem_size * first.value
            else:
                self.error("variable-length arrays not yet supported", decl.line, decl.col)
                return
            # Align to 8
            total = (total + 7) & ~7
            self.stack_offset -= total
            self.locals[decl.name] = (self.stack_offset, decl.type_spec)
        elif decl.type_spec.is_struct() and not decl.type_spec.is_pointer():
            # Struct: allocate full struct size on stack
            alloc = (size + 7) & ~7
            self.stack_offset -= alloc
            self.locals[decl.name] = (self.stack_offset, decl.type_spec)
        else:
            self.stack_offset -= 8  # always 8-byte aligned slots
            self.locals[decl.name] = (self.stack_offset, decl.type_spec)

        if decl.init:
            self.gen_expr(decl.init)
            offset = self.locals[decl.name][0]
            if size <= 4 and not decl.type_spec.is_pointer():
                self.emit(f"    movl %eax, {offset}(%rbp)")
            else:
                self.emit(f"    movq %rax, {offset}(%rbp)")

    def gen_if(self, stmt: IfStmt):
        else_label = self.new_label("else")
        end_label = self.new_label("endif")

        self.gen_expr(stmt.condition)
        self.emit("    cmpl $0, %eax")

        if stmt.else_body:
            self.emit(f"    je {else_label}")
            self.gen_stmt(stmt.then_body)
            self.emit(f"    jmp {end_label}")
            self.label(else_label)
            self.gen_stmt(stmt.else_body)
            self.label(end_label)
        else:
            self.emit(f"    je {end_label}")
            self.gen_stmt(stmt.then_body)
            self.label(end_label)

    def gen_while(self, stmt: WhileStmt):
        start_label = self.new_label("while")
        end_label = self.new_label("endwhile")

        self.break_labels.append(end_label)
        self.continue_labels.append(start_label)

        self.label(start_label)
        self.gen_expr(stmt.condition)
        self.emit("    cmpl $0, %eax")
        self.emit(f"    je {end_label}")
        self.gen_stmt(stmt.body)
        self.emit(f"    jmp {start_label}")
        self.label(end_label)

        self.break_labels.pop()
        self.continue_labels.pop()

    def gen_do_while(self, stmt: DoWhileStmt):
        start_label = self.new_label("dowhile")
        cond_label = self.new_label("docond")
        end_label = self.new_label("enddowhile")

        self.break_labels.append(end_label)
        self.continue_labels.append(cond_label)

        self.label(start_label)
        self.gen_stmt(stmt.body)
        self.label(cond_label)
        self.gen_expr(stmt.condition)
        self.emit("    cmpl $0, %eax")
        self.emit(f"    jne {start_label}")
        self.label(end_label)

        self.break_labels.pop()
        self.continue_labels.pop()

    def gen_for(self, stmt: ForStmt):
        cond_label = self.new_label("for")
        update_label = self.new_label("forupd")
        end_label = self.new_label("endfor")

        self.break_labels.append(end_label)
        self.continue_labels.append(update_label)

        if stmt.init:
            self.gen_stmt(stmt.init)

        self.label(cond_label)
        if stmt.condition:
            self.gen_expr(stmt.condition)
            self.emit("    cmpl $0, %eax")
            self.emit(f"    je {end_label}")

        self.gen_stmt(stmt.body)

        self.label(update_label)
        if stmt.update:
            self.gen_expr(stmt.update)
        self.emit(f"    jmp {cond_label}")
        self.label(end_label)

        self.break_labels.pop()
        self.continue_labels.pop()

    def gen_switch(self, stmt: SwitchStmt):
        end_label = self.new_label("endswitch")
        self.break_labels.append(end_label)

        # Evaluate switch expression
        self.gen_expr(stmt.expr)
        self.emit("    movl %eax, %r10d")  # save switch value

        # Collect cases from the body block
        if not isinstance(stmt.body, Block):
            self.error("switch body must be a block")

        cases = []
        default_label = None

        for s in stmt.body.stmts:
            if isinstance(s, CaseStmt):
                lbl = self.new_label("case")
                if s.is_default:
                    default_label = lbl
                else:
                    cases.append((s, lbl))
                s._label = lbl

        # Generate comparison jumps
        for case_stmt, lbl in cases:
            if isinstance(case_stmt.value, IntLiteral):
                self.emit(f"    cmpl ${case_stmt.value.value}, %r10d")
                self.emit(f"    je {lbl}")

        if default_label:
            self.emit(f"    jmp {default_label}")
        else:
            self.emit(f"    jmp {end_label}")

        # Generate case bodies
        for s in stmt.body.stmts:
            if isinstance(s, CaseStmt) and hasattr(s, '_label'):
                self.label(s._label)
                self.gen_stmt(s.stmt)
            else:
                self.gen_stmt(s)

        self.label(end_label)
        self.break_labels.pop()

    # ---- Expression generation ----
    # Result always in %rax (64-bit) or %eax (32-bit)

    def gen_expr(self, expr: Expr):
        if isinstance(expr, IntLiteral):
            if expr.value == 0:
                self.emit("    xorl %eax, %eax")
            elif -2147483648 <= expr.value <= 2147483647:
                self.emit(f"    movl ${expr.value}, %eax")
            else:
                self.emit(f"    movabsq ${expr.value}, %rax")

        elif isinstance(expr, CharLiteral):
            self.emit(f"    movl ${ord(expr.value)}, %eax")

        elif isinstance(expr, StringLiteral):
            lbl = self.new_label("str")
            self.string_literals.append((lbl, expr.value))
            self.emit(f"    leaq {lbl}(%rip), %rax")

        elif isinstance(expr, Identifier):
            self.gen_load_var(expr.name, expr.line, expr.col)

        elif isinstance(expr, BinaryOp):
            self.gen_binary_op(expr)

        elif isinstance(expr, UnaryOp):
            self.gen_unary_op(expr)

        elif isinstance(expr, Assignment):
            self.gen_assignment(expr)

        elif isinstance(expr, FuncCall):
            self.gen_func_call(expr)

        elif isinstance(expr, ArrayAccess):
            self.gen_array_access(expr)

        elif isinstance(expr, MemberAccess):
            self.gen_member_access(expr)

        elif isinstance(expr, TernaryOp):
            self.gen_ternary(expr)

        elif isinstance(expr, CastExpr):
            self.gen_expr(expr.operand)
            # TODO: actual type conversion

        elif isinstance(expr, SizeofExpr):
            if expr.is_type:
                size = expr.operand.size_bytes()
            else:
                # For expressions, we'd need type inference
                size = 4  # default to int
            self.emit(f"    movl ${size}, %eax")

        elif isinstance(expr, CommaExpr):
            for e in expr.exprs:
                self.gen_expr(e)

        else:
            self.error(f"unhandled expression type: {type(expr).__name__}", expr.line, expr.col)

    def get_var_location(self, name: str) -> Tuple[str, TypeSpec]:
        """Return (asm_location, type) for a variable."""
        if name in self.locals:
            offset, ts = self.locals[name]
            return f"{offset}(%rbp)", ts
        if name in self.params:
            offset, ts = self.params[name]
            return f"{offset}(%rbp)", ts
        if name in self.global_vars:
            decl = self.global_vars[name]
            return f"{name}(%rip)", decl.type_spec
        return None, None

    def gen_load_var(self, name: str, line=0, col=0):
        loc, ts = self.get_var_location(name)
        if loc is None:
            self.error(f"undeclared variable '{name}'", line, col)

        if ts and ts.is_array():
            # Array: load address
            if name in self.locals or name in self.params:
                offset = self.locals.get(name, self.params.get(name, (0, None)))[0]
                self.emit(f"    leaq {offset}(%rbp), %rax")
            else:
                self.emit(f"    leaq {name}(%rip), %rax")
        elif ts and (ts.is_pointer() or ts.size_bytes() == 8):
            self.emit(f"    movq {loc}, %rax")
        else:
            self.emit(f"    movl {loc}, %eax")

    def gen_lvalue_addr(self, expr: Expr):
        """Generate code that puts the address of an lvalue into %rax."""
        if isinstance(expr, Identifier):
            loc, ts = self.get_var_location(expr.name)
            if loc is None:
                self.error(f"undeclared variable '{expr.name}'", expr.line, expr.col)
            if expr.name in self.locals or expr.name in self.params:
                offset = (self.locals.get(expr.name) or self.params.get(expr.name))[0]
                self.emit(f"    leaq {offset}(%rbp), %rax")
            else:
                self.emit(f"    leaq {expr.name}(%rip), %rax")
        elif isinstance(expr, UnaryOp) and expr.op == "*":
            # *ptr as lvalue: address is the pointer value
            self.gen_expr(expr.operand)
        elif isinstance(expr, ArrayAccess):
            self.gen_array_addr(expr)
        elif isinstance(expr, MemberAccess):
            self.gen_member_addr(expr)
        else:
            self.error("expression is not an lvalue", expr.line, expr.col)

    def gen_array_addr(self, expr: ArrayAccess):
        """Generate address of array element into %rax."""
        # Get array base address
        if isinstance(expr.array, Identifier):
            loc, ts = self.get_var_location(expr.array.name)
            if ts and ts.is_array():
                # Array: base address
                if expr.array.name in self.locals or expr.array.name in self.params:
                    offset = (self.locals.get(expr.array.name) or self.params.get(expr.array.name))[0]
                    self.emit(f"    leaq {offset}(%rbp), %rax")
                else:
                    self.emit(f"    leaq {expr.array.name}(%rip), %rax")
            else:
                # Pointer: load pointer value
                self.gen_expr(expr.array)
        else:
            self.gen_expr(expr.array)

        self.emit("    pushq %rax")

        # Generate index
        self.gen_expr(expr.index)
        self.emit("    movslq %eax, %rax")

        # Element size (default to 4 for int, 8 for pointer, 1 for char)
        elem_size = 4  # default
        if isinstance(expr.array, Identifier):
            _, ts = self.get_var_location(expr.array.name)
            if ts:
                if ts.is_array() and ts.struct_def:
                    # Array of structs
                    elem_size = ts.struct_def.size_bytes()
                elif ts.is_array():
                    elem_ts = TypeSpec(base=ts.base, pointer_depth=ts.pointer_depth,
                                       is_unsigned=ts.is_unsigned)
                    elem_size = elem_ts.size_bytes()
                else:
                    elem_ts = TypeSpec(base=ts.base, pointer_depth=max(ts.pointer_depth - 1, 0),
                                       is_unsigned=ts.is_unsigned)
                    elem_size = elem_ts.size_bytes()

        if elem_size != 1:
            self.emit(f"    imulq ${elem_size}, %rax")

        self.emit("    popq %rcx")
        self.emit("    addq %rcx, %rax")

    def gen_array_access(self, expr: ArrayAccess):
        """Generate array access (load value)."""
        self.gen_array_addr(expr)

        # Determine element size for load
        elem_size = 4
        if isinstance(expr.array, Identifier):
            _, ts = self.get_var_location(expr.array.name)
            if ts:
                if ts.is_pointer() or (ts.is_array() and ts.pointer_depth > 0):
                    elem_size = 8
                elif ts.base == "char":
                    elem_size = 1

        if elem_size == 1:
            self.emit("    movsbl (%rax), %eax")
        elif elem_size == 8:
            self.emit("    movq (%rax), %rax")
        else:
            self.emit("    movl (%rax), %eax")

    def get_expr_type(self, expr: Expr) -> Optional[TypeSpec]:
        """Try to determine the type of an expression."""
        if isinstance(expr, Identifier):
            _, ts = self.get_var_location(expr.name)
            return ts
        if isinstance(expr, UnaryOp) and expr.op == "*":
            inner = self.get_expr_type(expr.operand)
            if inner and inner.is_pointer():
                return TypeSpec(base=inner.base, pointer_depth=inner.pointer_depth - 1,
                                struct_def=inner.struct_def, enum_def=inner.enum_def)
        if isinstance(expr, MemberAccess):
            obj_type = self.get_expr_type(expr.obj)
            if obj_type and expr.arrow:
                # obj is a pointer to struct
                if obj_type.struct_def:
                    return obj_type.struct_def.member_type(expr.member)
            elif obj_type and obj_type.struct_def:
                return obj_type.struct_def.member_type(expr.member)
        if isinstance(expr, ArrayAccess):
            arr_type = self.get_expr_type(expr.array)
            if arr_type:
                if arr_type.is_array() or arr_type.is_pointer():
                    return TypeSpec(base=arr_type.base, pointer_depth=max(arr_type.pointer_depth - 1, 0),
                                    struct_def=arr_type.struct_def)
        return None

    def gen_member_addr(self, expr: MemberAccess):
        """Generate address of a struct member into %rax."""
        if expr.arrow:
            # expr->member: obj is a pointer, load it
            self.gen_expr(expr.obj)
        else:
            # expr.member: obj is a struct, get its address
            self.gen_lvalue_addr(expr.obj)

        # Find the struct definition
        obj_type = self.get_expr_type(expr.obj)
        if obj_type is None:
            self.error(f"cannot determine type for member access", expr.line, expr.col)

        sdef = obj_type.struct_def
        if expr.arrow and obj_type.is_pointer():
            sdef = obj_type.struct_def
        if sdef is None:
            self.error(f"member access on non-struct type", expr.line, expr.col)

        offset = sdef.member_offset(expr.member)
        if offset is None:
            self.error(f"struct has no member '{expr.member}'", expr.line, expr.col)

        if offset != 0:
            self.emit(f"    addq ${offset}, %rax")

    def gen_member_access(self, expr: MemberAccess):
        """Generate code to load a struct member value into %rax/%eax."""
        self.gen_member_addr(expr)

        # Determine member type for load size
        obj_type = self.get_expr_type(expr.obj)
        sdef = obj_type.struct_def if obj_type else None
        mem_type = sdef.member_type(expr.member) if sdef else None

        if mem_type is None:
            self.emit("    movl (%rax), %eax")
        elif mem_type.is_pointer() or mem_type.size_bytes() == 8:
            self.emit("    movq (%rax), %rax")
        elif mem_type.base == "char" and not mem_type.is_pointer():
            self.emit("    movsbl (%rax), %eax")
        else:
            self.emit("    movl (%rax), %eax")

    def gen_binary_op(self, expr: BinaryOp):
        # Short-circuit for && and ||
        if expr.op == "&&":
            false_label = self.new_label("and_false")
            end_label = self.new_label("and_end")
            self.gen_expr(expr.left)
            self.emit("    cmpl $0, %eax")
            self.emit(f"    je {false_label}")
            self.gen_expr(expr.right)
            self.emit("    cmpl $0, %eax")
            self.emit(f"    je {false_label}")
            self.emit("    movl $1, %eax")
            self.emit(f"    jmp {end_label}")
            self.label(false_label)
            self.emit("    xorl %eax, %eax")
            self.label(end_label)
            return

        if expr.op == "||":
            true_label = self.new_label("or_true")
            end_label = self.new_label("or_end")
            self.gen_expr(expr.left)
            self.emit("    cmpl $0, %eax")
            self.emit(f"    jne {true_label}")
            self.gen_expr(expr.right)
            self.emit("    cmpl $0, %eax")
            self.emit(f"    jne {true_label}")
            self.emit("    xorl %eax, %eax")
            self.emit(f"    jmp {end_label}")
            self.label(true_label)
            self.emit("    movl $1, %eax")
            self.label(end_label)
            return

        # General binary: evaluate left, push, evaluate right, pop, operate
        self.gen_expr(expr.left)
        self.emit("    pushq %rax")
        self.gen_expr(expr.right)
        self.emit("    movl %eax, %ecx")  # right operand in ecx
        self.emit("    popq %rax")        # left operand in eax

        if expr.op == "+":
            self.emit("    addl %ecx, %eax")
        elif expr.op == "-":
            self.emit("    subl %ecx, %eax")
        elif expr.op == "*":
            self.emit("    imull %ecx, %eax")
        elif expr.op == "/":
            self.emit("    cdq")
            self.emit("    idivl %ecx")
        elif expr.op == "%":
            self.emit("    cdq")
            self.emit("    idivl %ecx")
            self.emit("    movl %edx, %eax")
        elif expr.op == "&":
            self.emit("    andl %ecx, %eax")
        elif expr.op == "|":
            self.emit("    orl %ecx, %eax")
        elif expr.op == "^":
            self.emit("    xorl %ecx, %eax")
        elif expr.op == "<<":
            self.emit("    shll %cl, %eax")
        elif expr.op == ">>":
            self.emit("    sarl %cl, %eax")
        elif expr.op in ("==", "!=", "<", ">", "<=", ">="):
            self.emit("    cmpl %ecx, %eax")
            cond_map = {
                "==": "sete", "!=": "setne",
                "<": "setl", ">": "setg",
                "<=": "setle", ">=": "setge",
            }
            self.emit(f"    {cond_map[expr.op]} %al")
            self.emit("    movzbl %al, %eax")
        else:
            self.error(f"unhandled binary operator '{expr.op}'", expr.line, expr.col)

    def gen_unary_op(self, expr: UnaryOp):
        if expr.op == "-":
            self.gen_expr(expr.operand)
            self.emit("    negl %eax")
        elif expr.op == "~":
            self.gen_expr(expr.operand)
            self.emit("    notl %eax")
        elif expr.op == "!":
            self.gen_expr(expr.operand)
            self.emit("    cmpl $0, %eax")
            self.emit("    sete %al")
            self.emit("    movzbl %al, %eax")
        elif expr.op == "&":
            # Address-of
            self.gen_lvalue_addr(expr.operand)
        elif expr.op == "*":
            # Dereference
            self.gen_expr(expr.operand)
            self.emit("    movl (%rax), %eax")
        elif expr.op == "++" and expr.prefix:
            self.gen_lvalue_addr(expr.operand)
            self.emit("    pushq %rax")
            self.emit("    movl (%rax), %eax")
            self.emit("    addl $1, %eax")
            self.emit("    popq %rcx")
            self.emit("    movl %eax, (%rcx)")
        elif expr.op == "--" and expr.prefix:
            self.gen_lvalue_addr(expr.operand)
            self.emit("    pushq %rax")
            self.emit("    movl (%rax), %eax")
            self.emit("    subl $1, %eax")
            self.emit("    popq %rcx")
            self.emit("    movl %eax, (%rcx)")
        elif expr.op == "++" and not expr.prefix:
            self.gen_lvalue_addr(expr.operand)
            self.emit("    pushq %rax")
            self.emit("    movl (%rax), %eax")
            self.emit("    movl %eax, %edx")  # save old value
            self.emit("    addl $1, %eax")
            self.emit("    popq %rcx")
            self.emit("    movl %eax, (%rcx)")
            self.emit("    movl %edx, %eax")  # return old value
        elif expr.op == "--" and not expr.prefix:
            self.gen_lvalue_addr(expr.operand)
            self.emit("    pushq %rax")
            self.emit("    movl (%rax), %eax")
            self.emit("    movl %eax, %edx")
            self.emit("    subl $1, %eax")
            self.emit("    popq %rcx")
            self.emit("    movl %eax, (%rcx)")
            self.emit("    movl %edx, %eax")
        else:
            self.error(f"unhandled unary operator '{expr.op}'", expr.line, expr.col)

    def gen_assignment(self, expr: Assignment):
        if expr.op == "=":
            self.gen_expr(expr.value)
            self.emit("    pushq %rax")
            self.gen_lvalue_addr(expr.target)
            self.emit("    movq %rax, %rcx")
            self.emit("    popq %rax")

            # Determine store size
            store_size = 4
            target_type = self.get_expr_type(expr.target)
            if target_type:
                if target_type.is_pointer() or target_type.size_bytes() == 8:
                    store_size = 8
                elif target_type.base == "char" and not target_type.is_pointer():
                    store_size = 1
            elif isinstance(expr.target, Identifier):
                _, ts = self.get_var_location(expr.target.name)
                if ts and (ts.is_pointer() or ts.size_bytes() == 8):
                    store_size = 8
                elif ts and ts.base == "char":
                    store_size = 1

            if store_size == 1:
                self.emit("    movb %al, (%rcx)")
            elif store_size == 8:
                self.emit("    movq %rax, (%rcx)")
            else:
                self.emit("    movl %eax, (%rcx)")
        else:
            # Compound assignment: +=, -=, etc.
            op = expr.op[:-1]  # strip '='
            self.gen_lvalue_addr(expr.target)
            self.emit("    pushq %rax")
            self.emit("    movl (%rax), %eax")
            self.emit("    pushq %rax")
            self.gen_expr(expr.value)
            self.emit("    movl %eax, %ecx")
            self.emit("    popq %rax")

            if op == "+":
                self.emit("    addl %ecx, %eax")
            elif op == "-":
                self.emit("    subl %ecx, %eax")
            elif op == "*":
                self.emit("    imull %ecx, %eax")
            elif op == "/":
                self.emit("    cdq")
                self.emit("    idivl %ecx")
            elif op == "%":
                self.emit("    cdq")
                self.emit("    idivl %ecx")
                self.emit("    movl %edx, %eax")
            elif op == "&":
                self.emit("    andl %ecx, %eax")
            elif op == "|":
                self.emit("    orl %ecx, %eax")
            elif op == "^":
                self.emit("    xorl %ecx, %eax")
            elif op == "<<":
                self.emit("    shll %cl, %eax")
            elif op == ">>":
                self.emit("    sarl %cl, %eax")

            self.emit("    popq %rcx")
            self.emit("    movl %eax, (%rcx)")

    def gen_func_call(self, expr: FuncCall):
        if not isinstance(expr.name, Identifier):
            self.error("indirect function calls not yet supported", expr.line, expr.col)

        func_name = expr.name.name
        num_args = len(expr.args)

        # Align stack to 16 bytes before call if needed
        # Push args in reverse order for stack args
        stack_args = max(0, num_args - 6)
        if stack_args % 2 != 0:
            self.emit("    subq $8, %rsp")  # align

        # Evaluate args and push (we need to handle register args)
        # First push all args, then pop into registers
        for arg in reversed(expr.args):
            self.gen_expr(arg)
            self.emit("    pushq %rax")

        # Pop into registers
        for i in range(min(num_args, 6)):
            self.emit(f"    popq {self.ARG_REGS_64[i]}")

        # Stack args are already in order on the stack

        self.emit("    xorl %eax, %eax")  # clear AL for variadic functions
        self.emit(f"    call {func_name}")

        # Clean up stack args
        if stack_args > 0:
            cleanup = stack_args * 8
            if stack_args % 2 != 0:
                cleanup += 8  # alignment padding
            self.emit(f"    addq ${cleanup}, %rsp")
        elif stack_args == 0 and num_args > 6:
            pass
        # If we added alignment padding but no stack args
        if stack_args == 0 and num_args <= 6:
            pass

    def gen_ternary(self, expr: TernaryOp):
        false_label = self.new_label("tern_f")
        end_label = self.new_label("tern_e")

        self.gen_expr(expr.condition)
        self.emit("    cmpl $0, %eax")
        self.emit(f"    je {false_label}")
        self.gen_expr(expr.true_expr)
        self.emit(f"    jmp {end_label}")
        self.label(false_label)
        self.gen_expr(expr.false_expr)
        self.label(end_label)
