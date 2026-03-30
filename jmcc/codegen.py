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
        self.known_functions: set = set()  # function names
        self.label_count = 0
        self.break_labels: List[str] = []  # stack of break target labels
        self.continue_labels: List[str] = []  # stack of continue target labels

        # Current function state
        self.locals: Dict[str, Tuple[int, TypeSpec]] = {}  # name -> (stack_offset, type)
        self.params: Dict[str, Tuple[int, TypeSpec]] = {}
        self.static_locals: Dict[str, str] = {}  # local_name -> mangled_global_name
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

        # First pass: collect globals, infer array sizes from initializers
        for decl in program.declarations:
            if isinstance(decl, GlobalVarDecl):
                # Infer array size from initializer if unsized (e.g., int a[] = {1,2,3})
                ts = decl.type_spec
                if ts.is_array() and ts.array_sizes and ts.array_sizes[0] is None:
                    if isinstance(decl.init, InitList):
                        # Simulate sequential index progression with designated jumps
                        idx = 0
                        max_idx = 0
                        for item in decl.init.items:
                            if item.designator_index is not None:
                                idx = item.designator_index
                            max_idx = max(max_idx, idx + 1)
                            idx += 1
                        ts.array_sizes[0] = IntLiteral(value=max_idx)
                    elif isinstance(decl.init, StringLiteral):
                        ts.array_sizes[0] = IntLiteral(value=len(decl.init.value) + 1)
                self.global_vars[decl.name] = decl
            elif isinstance(decl, FuncDecl):
                self.known_functions.add(decl.name)

        # Generate functions
        for decl in program.declarations:
            if isinstance(decl, FuncDecl) and decl.body is not None:
                self.gen_function(decl)

        # (String literals emitted at the end, after globals may add more)

        # Generate float constants
        if hasattr(self, 'float_constants') and self.float_constants:
            if not self.string_literals:
                self.emit("")
                self.emit("    .section .rodata")
            for lbl, val_int in self.float_constants:
                self.emit(f"    .align 8")
                self.label(lbl)
                self.emit(f"    .quad {val_int}")

        # Generate global variables
        if self.global_vars:
            for name, decl in self.global_vars.items():
                self.emit("")
                const_val = self._try_eval_const(decl.init) if decl.init else None
                is_float_init = decl.init and isinstance(decl.init, FloatLiteral)
                # Global pointer init with &var or function name
                is_addr_init = (decl.init and isinstance(decl.init, UnaryOp) and
                                decl.init.op == "&" and isinstance(decl.init.operand, Identifier))
                is_func_init = (decl.init and isinstance(decl.init, Identifier) and
                                decl.init.name in self.known_functions)
                is_cast_addr = (decl.init and isinstance(decl.init, CastExpr) and
                                isinstance(decl.init.operand, UnaryOp) and
                                decl.init.operand.op == "&" and
                                isinstance(decl.init.operand.operand, Identifier))
                if is_addr_init or is_func_init or is_cast_addr:
                    self.emit("    .data")
                    self.emit(f"    .globl {name}")
                    self.emit(f"    .align 8")
                    self.label(name)
                    if is_addr_init:
                        self.emit(f"    .quad {decl.init.operand.name}")
                    elif is_cast_addr:
                        self.emit(f"    .quad {decl.init.operand.operand.name}")
                    else:
                        self.emit(f"    .quad {decl.init.name}")
                elif is_float_init:
                    import struct
                    self.emit("    .data")
                    self.emit(f"    .globl {name}")
                    self.emit(f"    .align 8")
                    self.label(name)
                    packed = struct.pack('<d', decl.init.value)
                    val_int = int.from_bytes(packed, 'little')
                    self.emit(f"    .quad {val_int}")
                elif const_val is not None:
                    self.emit("    .data")
                    self.emit(f"    .globl {name}")
                    size = decl.type_spec.size_bytes()
                    self.emit(f"    .align {min(max(size, 4), 8)}")
                    self.label(name)
                    if decl.type_spec.base in ("double", "float", "long double"):
                        # Store as IEEE 754 double
                        import struct
                        packed = struct.pack('<d', float(const_val))
                        val_int = int.from_bytes(packed, 'little')
                        self.emit(f"    .quad {val_int}")
                    elif size == 1:
                        self.emit(f"    .byte {const_val}")
                    elif size == 2:
                        self.emit(f"    .word {const_val}")
                    elif size == 4:
                        self.emit(f"    .long {const_val}")
                    else:
                        self.emit(f"    .quad {const_val}")
                elif (decl.init and isinstance(decl.init, UnaryOp) and
                      decl.init.op == "&" and isinstance(decl.init.operand, InitList)):
                    # &(struct S){1, 2} — compound literal with address-of
                    # Create anonymous static for the compound literal
                    anon_name = self.new_label("compound")
                    anon_init = decl.init.operand
                    sdef = decl.type_spec.struct_def  # pointer to struct
                    self.emit("    .data")
                    self.emit(f"    .align 8")
                    self.label(anon_name)
                    if sdef:
                        self._emit_struct_init_data(sdef, anon_init)
                    else:
                        # Fallback: emit zeros
                        self.emit(f"    .zero 8")
                    # Now emit the pointer
                    self.emit(f"    .globl {name}")
                    self.emit(f"    .align 8")
                    self.label(name)
                    self.emit(f"    .quad {anon_name}")
                elif decl.init and isinstance(decl.init, StringLiteral) and decl.type_spec.is_array():
                    # char s[] = "hello";
                    self.emit("    .data")
                    self.emit(f"    .globl {name}")
                    self.emit(f"    .align 1")
                    self.label(name)
                    asm_str = ""
                    for ch in decl.init.value:
                        if ch == '\n': asm_str += "\\n"
                        elif ch == '\t': asm_str += "\\t"
                        elif ch == '\\': asm_str += "\\\\"
                        elif ch == '"': asm_str += '\\"'
                        elif ord(ch) < 32 or ord(ch) > 126: asm_str += f"\\{ord(ch):03o}"
                        else: asm_str += ch
                    self.emit(f'    .string "{asm_str}"')
                elif decl.init and isinstance(decl.init, InitList):
                    self.emit("    .data")
                    self.emit(f"    .globl {name}")
                    self.emit(f"    .align 8")
                    self.label(name)
                    sdef = decl.type_spec.struct_def
                    if sdef and not decl.type_spec.is_array():
                        # Single struct init
                        self._emit_struct_init_data(sdef, decl.init)
                    elif decl.type_spec.is_array() and sdef:
                        # Array of structs initializer
                        sdef = decl.type_spec.struct_def
                        total_elems = 0
                        if decl.type_spec.array_sizes and decl.type_spec.array_sizes[0]:
                            first = decl.type_spec.array_sizes[0]
                            if isinstance(first, IntLiteral):
                                total_elems = first.value
                        # Check if init items are nested InitLists or flat values
                        has_nested = any(isinstance(item.value, InitList) for item in decl.init.items)

                        if has_nested:
                            # Build element map: idx -> InitList
                            elem_inits = [None] * total_elems
                            idx = 0
                            for item in decl.init.items:
                                if item.designator_index is not None:
                                    idx = item.designator_index
                                if isinstance(item.value, InitList) and idx < total_elems:
                                    elem_inits[idx] = item.value
                                idx += 1
                            for einit in elem_inits:
                                if einit:
                                    self._emit_struct_init_data(sdef, einit)
                                else:
                                    self.emit(f"    .zero {sdef.size_bytes()}")
                        else:
                            # Flat initializer: distribute values across struct members
                            # Count total member slots including array elements
                            member_count = 0
                            for m in sdef.members:
                                if m.type_spec.is_array() and m.type_spec.array_sizes:
                                    first = m.type_spec.array_sizes[0]
                                    if isinstance(first, IntLiteral):
                                        member_count += first.value
                                    else:
                                        member_count += 1
                                else:
                                    member_count += 1

                            flat_vals = []
                            for item in decl.init.items:
                                cv = self._try_eval_const(item.value)
                                flat_vals.append(cv if cv is not None else 0)

                            for elem_idx in range(total_elems):
                                start = elem_idx * member_count
                                for j in range(member_count):
                                    val_idx = start + j
                                    val = flat_vals[val_idx] if val_idx < len(flat_vals) else 0
                                    if sdef.members and sdef.members[0].type_spec.size_bytes() == 8:
                                        self.emit(f"    .quad {val}")
                                    else:
                                        self.emit(f"    .long {val}")
                                # Pad to struct size
                                data_bytes = member_count * 8  # assuming long
                                struct_bytes = sdef.size_bytes()
                                if data_bytes < struct_bytes:
                                    self.emit(f"    .zero {struct_bytes - data_bytes}")
                    else:
                        # Plain array initializer (with designated initializer support)
                        elem_size = decl.type_spec.size_bytes()
                        total_elems = 0
                        if decl.type_spec.array_sizes and decl.type_spec.array_sizes[0]:
                            first = decl.type_spec.array_sizes[0]
                            if isinstance(first, IntLiteral):
                                total_elems = first.value
                        elems = [0] * total_elems
                        idx = 0
                        for item in decl.init.items:
                            if item.designator_index is not None:
                                idx = item.designator_index
                            cv = self._try_eval_const(item.value)
                            if cv is not None and idx < total_elems:
                                elems[idx] = cv
                            idx += 1
                        for val in elems:
                            if elem_size <= 4:
                                self.emit(f"    .long {val}")
                            else:
                                self.emit(f"    .quad {val}")
                else:
                    self.emit("    .bss")
                    self.emit(f"    .globl {name}")
                    size = decl.type_spec.size_bytes()
                    if decl.type_spec.is_array() and decl.type_spec.array_sizes:
                        first = decl.type_spec.array_sizes[0]
                        if isinstance(first, IntLiteral):
                            size *= first.value
                    align = min(decl.type_spec.size_bytes(), 8)
                    if align < 4:
                        align = 4
                    self.emit(f"    .align {align}")
                    self.label(name)
                    self.emit(f"    .zero {size}")

        # Generate string literals (at the end, after globals which may add more)
        if self.string_literals:
            self.emit("")
            self.emit("    .section .rodata")
            for lbl, val in self.string_literals:
                self.label(lbl)
                asm_str = ""
                for ch in val:
                    if ch == '\n': asm_str += "\\n"
                    elif ch == '\t': asm_str += "\\t"
                    elif ch == '\r': asm_str += "\\r"
                    elif ch == '\0': asm_str += "\\0"
                    elif ch == '"': asm_str += '\\"'
                    elif ch == '\\': asm_str += "\\\\"
                    elif ord(ch) < 32 or ord(ch) > 126: asm_str += f"\\{ord(ch):03o}"
                    else: asm_str += ch
                self.emit(f'    .string "{asm_str}"')

        return "\n".join(self.output) + "\n"

    def _emit_struct_init_data(self, sdef, init_list):
        """Emit data section entries for a struct initializer."""
        # Build a map of member values
        values = {}
        for i, item in enumerate(init_list.items):
            if item.designator:
                values[item.designator] = item.value
            elif i < len(sdef.members):
                values[sdef.members[i].name] = item.value

        offset = 0
        for mem in sdef.members:
            size = mem.type_spec.size_bytes()
            # Alignment padding
            align = min(size, 8)
            if align > 0:
                aligned = (offset + align - 1) & ~(align - 1)
                if aligned > offset:
                    self.emit(f"    .zero {aligned - offset}")
                offset = aligned

            val = values.get(mem.name)
            # Calculate actual member size (including array)
            actual_size = size
            if mem.type_spec.is_array() and mem.type_spec.array_sizes:
                first = mem.type_spec.array_sizes[0]
                if isinstance(first, IntLiteral):
                    actual_size = size * first.value

            if val and isinstance(val, InitList) and mem.type_spec.is_array():
                # Array member initialized with {val1, val2, ...}
                arr_count = 0
                if mem.type_spec.array_sizes and mem.type_spec.array_sizes[0]:
                    first = mem.type_spec.array_sizes[0]
                    if isinstance(first, IntLiteral):
                        arr_count = first.value
                elems = [0] * arr_count
                for j, item in enumerate(val.items):
                    cv = self._try_eval_const(item.value)
                    if cv is not None and j < arr_count:
                        elems[j] = cv
                for ev in elems:
                    if size <= 4:
                        self.emit(f"    .long {ev}")
                    else:
                        self.emit(f"    .quad {ev}")
            elif val and isinstance(val, InitList) and mem.type_spec.struct_def:
                # Nested struct member
                self._emit_struct_init_data(mem.type_spec.struct_def, val)
            else:
                cv = self._try_eval_const(val) if val else None
                if cv is not None:
                    if size <= 4:
                        self.emit(f"    .long {cv}")
                    else:
                        self.emit(f"    .quad {cv}")
                elif val and isinstance(val, StringLiteral):
                    lbl = self.new_label("str")
                    self.string_literals.append((lbl, val.value))
                    self.emit(f"    .quad {lbl}")
                elif (val and isinstance(val, UnaryOp) and val.op == "&" and
                      isinstance(val.operand, Identifier)):
                    self.emit(f"    .quad {val.operand.name}")
                elif val and isinstance(val, Identifier) and val.name in self.known_functions:
                    self.emit(f"    .quad {val.name}")
                else:
                    if actual_size <= 4:
                        self.emit(f"    .long 0")
                    elif actual_size <= 8:
                        self.emit(f"    .quad 0")
                    else:
                        self.emit(f"    .zero {actual_size}")
            offset += actual_size

        # Pad to total struct size
        total = sdef.size_bytes()
        if offset < total:
            self.emit(f"    .zero {total - offset}")

    def _try_eval_const(self, expr) -> Optional[int]:
        """Try to evaluate an expression as a compile-time integer constant."""
        if isinstance(expr, IntLiteral):
            return expr.value
        if isinstance(expr, CastExpr):
            return self._try_eval_const(expr.operand)
        if isinstance(expr, UnaryOp):
            val = self._try_eval_const(expr.operand)
            if val is None:
                return None
            if expr.op == "-":
                return -val
            if expr.op == "~":
                return ~val
            if expr.op == "!":
                return 0 if val else 1
        if isinstance(expr, BinaryOp):
            left = self._try_eval_const(expr.left)
            right = self._try_eval_const(expr.right)
            if left is None or right is None:
                return None
            ops = {
                "+": lambda a, b: a + b, "-": lambda a, b: a - b,
                "*": lambda a, b: a * b, "/": lambda a, b: a // b if b else 0,
                "%": lambda a, b: a % b if b else 0,
                "<<": lambda a, b: a << b, ">>": lambda a, b: a >> b,
                "&": lambda a, b: a & b, "|": lambda a, b: a | b,
                "^": lambda a, b: a ^ b,
                "==": lambda a, b: int(a == b), "!=": lambda a, b: int(a != b),
                "<": lambda a, b: int(a < b), ">": lambda a, b: int(a > b),
                "<=": lambda a, b: int(a <= b), ">=": lambda a, b: int(a >= b),
                "&&": lambda a, b: int(bool(a) and bool(b)),
                "||": lambda a, b: int(bool(a) or bool(b)),
            }
            if expr.op in ops:
                return ops[expr.op](left, right)
        if isinstance(expr, TernaryOp):
            cond = self._try_eval_const(expr.condition)
            if cond is None:
                return None
            return self._try_eval_const(expr.true_expr if cond else expr.false_expr)
        if isinstance(expr, SizeofExpr):
            if expr.is_type:
                ts = expr.operand
                size = ts.size_bytes()
                if ts.is_array() and ts.array_sizes:
                    first = ts.array_sizes[0]
                    if isinstance(first, IntLiteral):
                        size *= first.value
                return size
            # sizeof on expression
            if isinstance(expr.operand, Identifier):
                _, ts = self.get_var_location(expr.operand.name)
                if ts:
                    size = ts.size_bytes()
                    if ts.is_array() and ts.array_sizes:
                        first = ts.array_sizes[0]
                        if isinstance(first, IntLiteral):
                            size *= first.value
                    return size
            return 4
        return None

    def gen_function(self, func: FuncDecl):
        self.current_func = func
        self.locals = {}
        self.params = {}
        self.static_locals = {}
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
            fname = self.current_func.name if self.current_func else ""
            self.emit(f"    jmp .Luser_{fname}_{stmt.label}")
        elif isinstance(stmt, LabelStmt):
            fname = self.current_func.name if self.current_func else ""
            self.label(f".Luser_{fname}_{stmt.label}")
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
        if decl.name in ("__skip__", ""):
            return  # Skip no-op declarations

        size = decl.type_spec.size_bytes()

        # Static local variable: store as a global with mangled name
        if decl.type_spec.is_static and self.current_func:
            mangled = f"__static_{self.current_func.name}_{decl.name}"
            gdecl = GlobalVarDecl(type_spec=decl.type_spec, name=mangled, init=decl.init)
            self.global_vars[mangled] = gdecl
            self.static_locals[decl.name] = mangled
            return

        if decl.type_spec.is_array() and decl.type_spec.array_sizes:
            first = decl.type_spec.array_sizes[0]
            # Infer array size from initializer if unsized
            if first is None and isinstance(decl.init, InitList):
                count = len(decl.init.items)
                first = IntLiteral(value=count)
                decl.type_spec.array_sizes[0] = first
            elif first is None and isinstance(decl.init, StringLiteral):
                first = IntLiteral(value=len(decl.init.value) + 1)
                decl.type_spec.array_sizes[0] = first
            # Try to evaluate constant array size
            if not isinstance(first, IntLiteral):
                cv = self._try_eval_const(first)
                if cv is not None:
                    first = IntLiteral(value=cv)
                    decl.type_spec.array_sizes[0] = first
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
            if isinstance(decl.init, InitList) and decl.type_spec.struct_def:
                self.gen_struct_init(decl.name, decl.type_spec, decl.init)
            elif isinstance(decl.init, InitList) and decl.type_spec.is_array():
                self.gen_array_init(decl.name, decl.type_spec, decl.init)
            else:
                self.gen_expr(decl.init)
                offset = self.locals[decl.name][0]
                if size <= 4 and not decl.type_spec.is_pointer():
                    self.emit(f"    movl %eax, {offset}(%rbp)")
                else:
                    self.emit(f"    movq %rax, {offset}(%rbp)")

    def gen_struct_init(self, var_name: str, type_spec: TypeSpec, init: 'InitList'):
        """Generate code for struct initialization from { ... }."""
        sdef = type_spec.struct_def
        base_offset = self.locals[var_name][0]

        for i, item in enumerate(init.items):
            if item.designator:
                # .field = value
                mem_offset = sdef.member_offset(item.designator)
                mem_type = sdef.member_type(item.designator)
            elif i < len(sdef.members):
                # Positional init
                mem_offset = sdef.member_offset(sdef.members[i].name)
                mem_type = sdef.members[i].type_spec
            else:
                continue

            if mem_offset is None:
                continue

            self.gen_expr(item.value)
            abs_offset = base_offset + mem_offset
            if mem_type and (mem_type.is_pointer() or mem_type.size_bytes() == 8):
                self.emit(f"    movq %rax, {abs_offset}(%rbp)")
            elif mem_type and mem_type.base == "char" and not mem_type.is_pointer():
                self.emit(f"    movb %al, {abs_offset}(%rbp)")
            else:
                self.emit(f"    movl %eax, {abs_offset}(%rbp)")

    def gen_array_init(self, var_name: str, type_spec: TypeSpec, init: 'InitList'):
        """Generate code for array initialization from { ... }."""
        base_offset = self.locals[var_name][0]
        elem_size = type_spec.size_bytes()

        for i, item in enumerate(init.items):
            idx = item.designator_index if item.designator_index is not None else i
            self.gen_expr(item.value)
            offset = base_offset + idx * elem_size
            if elem_size == 1:
                self.emit(f"    movb %al, {offset}(%rbp)")
            elif elem_size == 8:
                self.emit(f"    movq %rax, {offset}(%rbp)")
            else:
                self.emit(f"    movl %eax, {offset}(%rbp)")

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

        # Collect cases from the body
        body = stmt.body
        if not isinstance(body, Block):
            # Wrap single statement in a block
            if isinstance(body, CaseStmt):
                body = Block(stmts=[body], line=body.line, col=body.col)
            else:
                self.emit(f"    jmp {end_label}")
                self.gen_stmt(body)
                self.label(end_label)
                self.break_labels.pop()
                return
        stmt.body = body

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

        elif isinstance(expr, FloatLiteral):
            # Store double constant in rodata, load via SSE AND into rax
            import struct
            lbl = self.new_label("flt")
            packed = struct.pack('<d', expr.value)
            val_as_int = int.from_bytes(packed, 'little')
            if not hasattr(self, 'float_constants'):
                self.float_constants = []
            self.float_constants.append((lbl, val_as_int))
            self.emit(f"    movsd {lbl}(%rip), %xmm0")
            self.emit(f"    movq %xmm0, %rax")  # also in rax for push/pop

        elif isinstance(expr, CharLiteral):
            self.emit(f"    movl ${ord(expr.value)}, %eax")

        elif isinstance(expr, StringLiteral):
            lbl = self.new_label("str")
            self.string_literals.append((lbl, expr.value))
            self.emit(f"    leaq {lbl}(%rip), %rax")

        elif isinstance(expr, Identifier):
            # Function name used as value (address of function)
            if expr.name in self.known_functions:
                loc, _ = self.get_var_location(expr.name)
                if loc is None:
                    # It's a function name, not a variable — load its address
                    self.emit(f"    leaq {expr.name}(%rip), %rax")
                else:
                    self.gen_load_var(expr.name, expr.line, expr.col)
            else:
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
                ts = expr.operand
                size = ts.size_bytes()
                if ts.is_array() and ts.array_sizes:
                    first = ts.array_sizes[0]
                    if isinstance(first, IntLiteral):
                        size *= first.value
            else:
                # sizeof on an expression — infer type
                et = self.get_expr_type(expr.operand)
                if et:
                    size = et.size_bytes()
                    if et.is_array() and et.array_sizes:
                        first = et.array_sizes[0]
                        if isinstance(first, IntLiteral):
                            size *= first.value
                else:
                    size = 4
            self.emit(f"    movl ${size}, %eax")

        elif isinstance(expr, CommaExpr):
            for e in expr.exprs:
                self.gen_expr(e)

        else:
            self.error(f"unhandled expression type: {type(expr).__name__}", expr.line, expr.col)

    def get_var_location(self, name: str) -> Tuple[str, TypeSpec]:
        """Return (asm_location, type) for a variable."""
        if name in self.static_locals:
            mangled = self.static_locals[name]
            decl = self.global_vars[mangled]
            return f"{mangled}(%rip)", decl.type_spec
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
            if loc is None and expr.name in self.known_functions:
                # Address of function
                self.emit(f"    leaq {expr.name}(%rip), %rax")
                return
            if loc is None:
                self.error(f"undeclared variable '{expr.name}'", expr.line, expr.col)
            if expr.name in self.static_locals:
                mangled = self.static_locals[expr.name]
                self.emit(f"    leaq {mangled}(%rip), %rax")
            elif expr.name in self.locals or expr.name in self.params:
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

        # Determine element size for load (based on pointed-to/element type)
        elem_size = 4
        if isinstance(expr.array, Identifier):
            _, ts = self.get_var_location(expr.array.name)
            if ts:
                # For pointer or array, element type is one level of indirection less
                if ts.is_pointer() and ts.pointer_depth == 1:
                    # Pointer to base type: element is the base type
                    if ts.base == "char":
                        elem_size = 1
                    elif ts.base in ("long", "long long") or ts.struct_def:
                        elem_size = 8
                    else:
                        elem_size = 4
                elif ts.is_pointer() and ts.pointer_depth > 1:
                    # Pointer to pointer: element is a pointer (8 bytes)
                    elem_size = 8
                elif ts.is_array():
                    if ts.pointer_depth > 0:
                        elem_size = 8
                    elif ts.base == "char":
                        elem_size = 1
                    elif ts.struct_def:
                        elem_size = ts.struct_def.size_bytes()
                    elif ts.base in ("long", "long long"):
                        elem_size = 8
                    else:
                        elem_size = 4

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
        if isinstance(expr, IntLiteral):
            return TypeSpec(base="int")
        if isinstance(expr, UnaryOp) and expr.op == "*":
            inner = self.get_expr_type(expr.operand)
            if inner and inner.is_pointer():
                return TypeSpec(base=inner.base, pointer_depth=inner.pointer_depth - 1,
                                struct_def=inner.struct_def, enum_def=inner.enum_def)
        if isinstance(expr, UnaryOp) and expr.op == "&":
            inner = self.get_expr_type(expr.operand)
            if inner:
                return TypeSpec(base=inner.base, pointer_depth=inner.pointer_depth + 1,
                                struct_def=inner.struct_def, enum_def=inner.enum_def)
        if isinstance(expr, MemberAccess):
            obj_type = self.get_expr_type(expr.obj)
            if obj_type and expr.arrow:
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
        if isinstance(expr, BinaryOp) and expr.op in ("+", "-"):
            lt = self.get_expr_type(expr.left)
            if lt and lt.is_pointer():
                return lt
        if isinstance(expr, Assignment):
            return self.get_expr_type(expr.target)
        if isinstance(expr, CastExpr):
            return expr.target_type
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

        if mem_type and mem_type.is_array():
            # Array member: return address (don't dereference)
            pass  # address already in %rax from gen_member_addr
        elif mem_type is None:
            self.emit("    movl (%rax), %eax")
        elif mem_type.is_pointer() or mem_type.size_bytes() == 8:
            self.emit("    movq (%rax), %rax")
        elif mem_type.base == "char" and not mem_type.is_pointer():
            self.emit("    movsbl (%rax), %eax")
        else:
            self.emit("    movl (%rax), %eax")

    def _is_float_type(self, expr):
        """Check if expression has float/double type."""
        et = self.get_expr_type(expr)
        return et and et.base in ("float", "double", "long double") and not et.is_pointer()

    def gen_binary_op(self, expr: BinaryOp):
        # Float comparison: use SSE
        if expr.op in ("<", ">", "<=", ">=", "==", "!=") and (
                self._is_float_type(expr.left) or self._is_float_type(expr.right)):
            # Load left into xmm0
            lt = self.get_expr_type(expr.left)
            if lt and lt.base in ("float", "double", "long double"):
                self.gen_expr(expr.left)  # loads double into rax via movq
                self.emit("    movq %rax, %xmm0")
            else:
                self.gen_expr(expr.left)
                self.emit("    cvtsi2sd %eax, %xmm0")
            # Load right into xmm1
            rt = self.get_expr_type(expr.right)
            if rt and rt.base in ("float", "double", "long double"):
                self.gen_expr(expr.right)
                self.emit("    movq %rax, %xmm1")
            else:
                self.gen_expr(expr.right)
                self.emit("    cvtsi2sd %eax, %xmm1")
            # Compare
            self.emit("    ucomisd %xmm1, %xmm0")
            cond_map = {
                "<": "setb", ">": "seta",
                "<=": "setbe", ">=": "setae",
                "==": "sete", "!=": "setne",
            }
            self.emit(f"    {cond_map[expr.op]} %al")
            self.emit("    movzbl %al, %eax")
            return

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

        # Check for pointer arithmetic
        left_type = self.get_expr_type(expr.left)
        right_type = self.get_expr_type(expr.right)
        is_ptr_op = ((left_type and left_type.is_pointer()) or
                      (right_type and right_type.is_pointer()))

        if is_ptr_op:
            self.emit("    movq %rax, %rcx")   # right operand in rcx (64-bit for pointers)
            self.emit("    popq %rax")          # left operand in rax
        else:
            self.emit("    movl %eax, %ecx")   # right operand in ecx (32-bit for ints)
            self.emit("    popq %rax")          # left operand in eax

        if expr.op == "+" and left_type and left_type.is_pointer():
            # pointer + int: scale int by element size, result in rax
            elem_size = TypeSpec(base=left_type.base, pointer_depth=left_type.pointer_depth - 1,
                                  struct_def=left_type.struct_def).size_bytes()
            if elem_size > 1:
                self.emit(f"    imulq ${elem_size}, %rcx")
            self.emit("    addq %rcx, %rax")
        elif expr.op == "+" and right_type and right_type.is_pointer():
            # int + pointer: rcx has pointer, rax has int
            elem_size = TypeSpec(base=right_type.base, pointer_depth=right_type.pointer_depth - 1,
                                  struct_def=right_type.struct_def).size_bytes()
            if elem_size > 1:
                self.emit(f"    imulq ${elem_size}, %rax")
            self.emit("    addq %rcx, %rax")
        elif expr.op == "+":
            self.emit("    addl %ecx, %eax")
        elif expr.op == "-" and left_type and left_type.is_pointer():
            # pointer - int: scale int by element size
            right_is_ptr = right_type and right_type.is_pointer()
            if not right_is_ptr:
                elem_size = TypeSpec(base=left_type.base, pointer_depth=left_type.pointer_depth - 1,
                                      struct_def=left_type.struct_def).size_bytes()
                if elem_size > 1:
                    self.emit(f"    imull ${elem_size}, %ecx")
                self.emit("    movslq %ecx, %rcx")
                self.emit("    subq %rcx, %rax")
            else:
                # pointer - pointer: result is element count
                self.emit("    subq %rcx, %rax")
                elem_size = TypeSpec(base=left_type.base, pointer_depth=left_type.pointer_depth - 1).size_bytes()
                if elem_size > 1:
                    self.emit("    cqo")
                    self.emit(f"    movq ${elem_size}, %rcx")
                    self.emit("    idivq %rcx")
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
            # Determine pointed-to type for correct load size
            inner_type = self.get_expr_type(expr.operand)
            if inner_type and inner_type.pointer_depth > 1:
                # Pointer to pointer: load a pointer (8 bytes)
                self.emit("    movq (%rax), %rax")
            elif inner_type and inner_type.base == "char" and inner_type.pointer_depth == 1:
                self.emit("    movsbl (%rax), %eax")
            elif inner_type and inner_type.pointer_depth == 1 and (inner_type.base in ("long", "long long") or inner_type.struct_def):
                self.emit("    movq (%rax), %rax")
            else:
                self.emit("    movl (%rax), %eax")
        elif expr.op in ("++", "--") and (expr.prefix or not expr.prefix):
            is_inc = (expr.op == "++")
            is_prefix = expr.prefix
            operand_type = self.get_expr_type(expr.operand)
            is_ptr = operand_type and operand_type.is_pointer()

            if is_ptr:
                elem_size = TypeSpec(base=operand_type.base,
                                     pointer_depth=operand_type.pointer_depth - 1,
                                     struct_def=operand_type.struct_def).size_bytes()
            else:
                elem_size = 1

            self.gen_lvalue_addr(expr.operand)
            self.emit("    pushq %rax")

            if is_ptr:
                self.emit("    movq (%rax), %rax")
                if not is_prefix:
                    self.emit("    movq %rax, %rdx")  # save old value
                op = "addq" if is_inc else "subq"
                self.emit(f"    {op} ${elem_size}, %rax")
                self.emit("    popq %rcx")
                self.emit("    movq %rax, (%rcx)")
                if not is_prefix:
                    self.emit("    movq %rdx, %rax")
            else:
                self.emit("    movl (%rax), %eax")
                if not is_prefix:
                    self.emit("    movl %eax, %edx")
                op = "addl" if is_inc else "subl"
                self.emit(f"    {op} ${elem_size}, %eax")
                self.emit("    popq %rcx")
                self.emit("    movl %eax, (%rcx)")
                if not is_prefix:
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
            target_type = self.get_expr_type(expr.target)
            is_ptr = target_type and target_type.is_pointer()

            self.gen_lvalue_addr(expr.target)
            self.emit("    pushq %rax")
            if is_ptr:
                self.emit("    movq (%rax), %rax")
            else:
                self.emit("    movl (%rax), %eax")
            self.emit("    pushq %rax")
            self.gen_expr(expr.value)
            self.emit("    movl %eax, %ecx")
            self.emit("    popq %rax")

            if is_ptr and op in ("+", "-"):
                elem_size = TypeSpec(base=target_type.base,
                                      pointer_depth=target_type.pointer_depth - 1,
                                      struct_def=target_type.struct_def).size_bytes()
                if elem_size > 1:
                    self.emit(f"    imull ${elem_size}, %ecx")
                self.emit("    movslq %ecx, %rcx")
                if op == "+":
                    self.emit("    addq %rcx, %rax")
                else:
                    self.emit("    subq %rcx, %rax")
            elif op == "+":
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
            if is_ptr:
                self.emit("    movq %rax, (%rcx)")
            else:
                self.emit("    movl %eax, (%rcx)")

    def gen_func_call(self, expr: FuncCall):
        is_indirect = not isinstance(expr.name, Identifier)
        is_fptr = False
        if isinstance(expr.name, Identifier):
            loc, ts = self.get_var_location(expr.name.name)
            if loc is not None and ts and ts.is_pointer():
                is_fptr = True

        func_name = expr.name.name if isinstance(expr.name, Identifier) else None
        num_args = len(expr.args)

        # Classify args as int or float
        arg_is_float = []
        for arg in expr.args:
            at = self.get_expr_type(arg)
            is_flt = (at and at.base in ("float", "double", "long double") and
                      not at.is_pointer())
            # Also check if it's a FloatLiteral
            if isinstance(arg, FloatLiteral):
                is_flt = True
            arg_is_float.append(is_flt)

        # Count integer and float args for register assignment
        int_arg_idx = 0
        xmm_arg_idx = 0

        # Align stack to 16 bytes before call if needed
        stack_args = max(0, num_args - 6)
        if stack_args % 2 != 0:
            self.emit("    subq $8, %rsp")

        # For indirect calls, save function pointer
        if is_indirect or is_fptr:
            if is_indirect:
                self.gen_expr(expr.name)
            else:
                self.gen_load_var(func_name, expr.line, expr.col)
            self.emit("    pushq %rax")

        # Evaluate args and push (all go on stack first, then distributed)
        for arg in reversed(expr.args):
            self.gen_expr(arg)
            self.emit("    pushq %rax")

        # Pop into correct registers (int regs or xmm regs)
        int_idx = 0
        xmm_idx = 0
        for i in range(min(num_args, 6)):
            if arg_is_float[i] and xmm_idx < 8:
                # Float arg: pop to temp, move to xmm
                self.emit(f"    popq %rax")
                self.emit(f"    movq %rax, %xmm{xmm_idx}")
                xmm_idx += 1
            else:
                # Integer arg
                if int_idx < 6:
                    self.emit(f"    popq {self.ARG_REGS_64[int_idx]}")
                    int_idx += 1
                else:
                    self.emit(f"    addq $8, %rsp")  # skip (stays on stack)

        # For remaining args beyond 6, they stay on stack
        # (already there from the push loop)

        # Set %al to number of xmm registers used (required for variadic calls)
        self.emit(f"    movl ${xmm_idx}, %eax")

        if is_indirect or is_fptr:
            self.emit("    popq %r11")
            self.emit("    call *%r11")
        else:
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
