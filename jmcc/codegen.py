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
        self.pending_compound_literals = []  # (label, struct_def, init_list) for anonymous compound literals
        self.global_vars: Dict[str, GlobalVarDecl] = {}
        self.known_functions: set = set()  # function names
        self.func_return_types: Dict[str, TypeSpec] = {}  # func name -> return type
        self.func_param_types: Dict[str, List] = {}  # func name -> list of param TypeSpec
        self.func_is_variadic: Dict[str, bool] = {}  # func name -> is variadic
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

    def _is_struct_by_value(self, ts):
        """Check if a type is a struct passed/returned by value (not pointer, not array)."""
        return (ts and ts.struct_def is not None and ts.pointer_depth == 0
                and not ts.is_array() and not ts.is_ptr_array
                and not (ts.array_sizes and any(d is not None for d in ts.array_sizes)))

    def _struct_arg_regs(self, size):
        """Return number of integer registers needed for a struct arg (System V ABI).
        Structs <= 8 bytes: 1 reg, 9-16 bytes: 2 regs, >16 bytes: passed by pointer (1 reg)."""
        if size <= 8:
            return 1
        elif size <= 16:
            return 2
        else:
            return 1  # pointer

    def _emit_memcpy_from_rax(self, dst_offset, size):
        """Copy 'size' bytes from address in %rax to dst_offset(%rbp).
        Uses %r11 as temp to avoid clobbering arg registers."""
        i = 0
        while i + 8 <= size:
            self.emit(f"    movq {i}(%rax), %r11")
            self.emit(f"    movq %r11, {dst_offset + i}(%rbp)")
            i += 8
        while i + 4 <= size:
            self.emit(f"    movl {i}(%rax), %r11d")
            self.emit(f"    movl %r11d, {dst_offset + i}(%rbp)")
            i += 4
        while i < size:
            self.emit(f"    movb {i}(%rax), %r11b")
            self.emit(f"    movb %r11b, {dst_offset + i}(%rbp)")
            i += 1

    def generate(self, program: Program) -> str:
        self.emit("    .text")

        # First pass: collect globals, infer array sizes from initializers
        for decl in program.declarations:
            if isinstance(decl, GlobalVarDecl):
                # Infer array size from initializer if unsized (e.g., int a[] = {1,2,3})
                ts = decl.type_spec
                if (ts.is_array() or ts.is_ptr_array) and ts.array_sizes and ts.array_sizes[0] is None:
                    if isinstance(decl.init, InitList):
                        # Simulate sequential index progression with designated jumps
                        idx = 0
                        max_idx = 0
                        has_nested = any(isinstance(item.value, InitList) for item in decl.init.items)
                        for item in decl.init.items:
                            if item.designator_index is not None:
                                idx = item.designator_index
                            max_idx = max(max_idx, idx + 1)
                            idx += 1
                        # For flat struct array init, divide by members per struct
                        # (skip for ptr_arrays — each item is a pointer, not struct members)
                        if ts.struct_def and not has_nested and not ts.is_ptr_array:
                            member_count = 0
                            for m in ts.struct_def.members:
                                if m.type_spec.is_array() and m.type_spec.array_sizes:
                                    first = m.type_spec.array_sizes[0]
                                    if isinstance(first, IntLiteral):
                                        member_count += first.value
                                    else:
                                        member_count += 1
                                else:
                                    member_count += 1
                            if member_count > 0:
                                max_idx = (max_idx + member_count - 1) // member_count
                        ts.array_sizes[0] = IntLiteral(value=max_idx)
                    elif isinstance(decl.init, StringLiteral):
                        ts.array_sizes[0] = IntLiteral(value=len(decl.init.value) + 1)
                self.global_vars[decl.name] = decl
            elif isinstance(decl, FuncDecl):
                self.known_functions.add(decl.name)
                if decl.return_type:
                    self.func_return_types[decl.name] = decl.return_type
                self.func_param_types[decl.name] = [p.type_spec for p in decl.params]
                self.func_is_variadic[decl.name] = decl.is_variadic

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
                is_array_elem_addr = (decl.init and isinstance(decl.init, UnaryOp) and
                                      decl.init.op == "&" and
                                      isinstance(decl.init.operand, ArrayAccess) and
                                      isinstance(decl.init.operand.array, Identifier))
                # Global var init with another global (array decay to pointer)
                is_global_ref = (decl.init and isinstance(decl.init, Identifier) and
                                 decl.init.name in self.global_vars and
                                 decl.init.name not in self.known_functions)
                if is_addr_init or is_func_init or is_cast_addr or is_array_elem_addr or is_global_ref:
                    self.emit("    .data")
                    if not decl.type_spec.is_static:
                        self.emit(f"    .globl {name}")
                    self.emit(f"    .align 8")
                    self.label(name)
                    if is_array_elem_addr:
                        arr_name = decl.init.operand.array.name
                        idx_val = self._try_eval_const(decl.init.operand.index)
                        if idx_val is not None and idx_val != 0:
                            # Element size from the array's declaration
                            elem_size = 4  # default int
                            if arr_name in self.global_vars:
                                gts = self.global_vars[arr_name].type_spec
                                elem_size = gts.size_bytes()
                                if gts.struct_def:
                                    elem_size = gts.struct_def.size_bytes()
                            self.emit(f"    .quad {arr_name}+{idx_val * elem_size}")
                        else:
                            self.emit(f"    .quad {arr_name}")
                    elif is_addr_init:
                        self.emit(f"    .quad {decl.init.operand.name}")
                    elif is_cast_addr:
                        self.emit(f"    .quad {decl.init.operand.operand.name}")
                    else:
                        self.emit(f"    .quad {decl.init.name}")
                elif is_float_init:
                    import struct
                    self.emit("    .data")
                    if not decl.type_spec.is_static:
                        self.emit(f"    .globl {name}")
                    self.emit(f"    .align 8")
                    self.label(name)
                    packed = struct.pack('<d', decl.init.value)
                    val_int = int.from_bytes(packed, 'little')
                    self.emit(f"    .quad {val_int}")
                elif const_val is not None:
                    self.emit("    .data")
                    if not decl.type_spec.is_static:
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
                      decl.init.op == "&" and
                      (isinstance(decl.init.operand, InitList) or
                       (isinstance(decl.init.operand, CastExpr) and isinstance(decl.init.operand.operand, InitList)))):
                    # &(struct S){1, 2} — compound literal with address-of
                    # Create anonymous static for the compound literal
                    anon_name = self.new_label("compound")
                    anon_init = self._unwrap_compound_literal(decl.init.operand)
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
                    if not decl.type_spec.is_static:
                        self.emit(f"    .globl {name}")
                    self.emit(f"    .align 8")
                    self.label(name)
                    self.emit(f"    .quad {anon_name}")
                elif decl.init and isinstance(decl.init, StringLiteral) and decl.type_spec.is_pointer():
                    # char *s = "hello"; — pointer to string literal
                    lbl = self.new_label("str")
                    self.string_literals.append((lbl, decl.init.value, decl.init.wide))
                    self.emit("    .data")
                    if not decl.type_spec.is_static:
                        self.emit(f"    .globl {name}")
                    self.emit(f"    .align 8")
                    self.label(name)
                    self.emit(f"    .quad {lbl}")
                elif decl.init and isinstance(decl.init, StringLiteral) and decl.type_spec.is_array():
                    # char s[] = "hello";  or  wchar_t s[] = L"hello";
                    self.emit("    .data")
                    if not decl.type_spec.is_static:
                        self.emit(f"    .globl {name}")
                    if decl.init.wide:
                        self.emit(f"    .align 4")
                        self.label(name)
                        for ch in decl.init.value:
                            self.emit(f"    .long {ord(ch)}")
                        self.emit("    .long 0")
                    else:
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
                elif decl.init and (isinstance(decl.init, InitList) or
                                     (isinstance(decl.init, CastExpr) and isinstance(decl.init.operand, InitList))):
                    actual_init = decl.init
                    if isinstance(actual_init, CastExpr):
                        actual_init = actual_init.operand
                    self.emit("    .data")
                    if not decl.type_spec.is_static:
                        self.emit(f"    .globl {name}")
                    self.emit(f"    .align 8")
                    self.label(name)
                    sdef = decl.type_spec.struct_def
                    if sdef and not decl.type_spec.is_array() and not decl.type_spec.is_ptr_array:
                        # Single struct init
                        self._emit_struct_init_data(sdef, actual_init)
                    elif decl.type_spec.is_array() and sdef:
                        # Array of structs initializer
                        sdef = decl.type_spec.struct_def
                        total_elems = 0
                        if decl.type_spec.array_sizes and decl.type_spec.array_sizes[0]:
                            first = decl.type_spec.array_sizes[0]
                            if isinstance(first, IntLiteral):
                                total_elems = first.value
                        # Check if init items are nested InitLists/compound literals or flat values
                        def _is_struct_init_item(item_val):
                            v = self._unwrap_compound_literal(item_val)
                            return isinstance(v, InitList)
                        has_nested = any(_is_struct_init_item(item.value) for item in actual_init.items)

                        if has_nested:
                            # Build element map: idx -> InitList or single-value init
                            elem_inits = [None] * total_elems
                            idx = 0
                            for item in actual_init.items:
                                if item.designator_index is not None:
                                    idx = item.designator_index
                                val = self._unwrap_compound_literal(item.value)
                                if idx < total_elems:
                                    if isinstance(val, InitList):
                                        elem_inits[idx] = val
                                    else:
                                        # Wrap scalar/identifier in a single-item InitList
                                        elem_inits[idx] = InitList(items=[InitItem(value=item.value)])
                                idx += 1
                            for einit in elem_inits:
                                if einit:
                                    self._emit_struct_init_data(sdef, einit)
                                else:
                                    self.emit(f"    .zero {sdef.size_bytes()}")
                        else:
                            # Flat initializer: use _build_data_bytes for each element
                            # by splitting items across elements using brace elision
                            items_per_elem = len(actual_init.items) // total_elems if total_elems > 0 else 0
                            if items_per_elem * total_elems < len(actual_init.items):
                                items_per_elem += 1
                            item_pos = 0
                            for elem_idx in range(total_elems):
                                elem_items = actual_init.items[item_pos:item_pos + items_per_elem]
                                item_pos += items_per_elem
                                if elem_items:
                                    sub_init = InitList(items=elem_items)
                                    self._emit_struct_init_data(sdef, sub_init)
                                else:
                                    self.emit(f"    .zero {sdef.size_bytes()}")
                    else:
                        # Plain array initializer (with designated initializer support)
                        elem_size = decl.type_spec.size_bytes()
                        total_elems = 0
                        if decl.type_spec.array_sizes and decl.type_spec.array_sizes[0]:
                            first = decl.type_spec.array_sizes[0]
                            dv = self._dim_value(first)
                            if dv is not None:
                                total_elems = dv
                        elif actual_init and actual_init.items:
                            # Unsized array: infer from initializer length
                            total_elems = len(actual_init.items)

                        # Handle pointer-sized elements (function pointers) vs scalar arrays
                        is_ptr_array = decl.type_spec.is_pointer() or (decl.type_spec.struct_def and decl.type_spec.size_bytes() == 8)
                        if not is_ptr_array and not decl.type_spec.struct_def:
                            # Check if element type is a pointer (e.g., void* or function pointer).
                            # Don't treat double/float arrays (8-byte scalar elements) as pointer arrays.
                            if elem_size == 8 and decl.type_spec.base not in ("double", "float"):
                                is_ptr_array = True

                        if is_ptr_array:
                            # Array of pointers: handle relocations
                            elems = [None] * total_elems  # None = zero, string = symbol
                            idx = 0
                            for item in actual_init.items:
                                if item.designator_index is not None:
                                    idx = item.designator_index
                                end_idx = idx
                                if item.designator_end is not None:
                                    end_idx = item.designator_end
                                for j in range(idx, end_idx + 1):
                                    if j < total_elems:
                                        orig_val = item.value
                                        # Check for &(Type){...} — anonymous compound literal
                                        # (must check BEFORE unwrapping CastExpr which would lose the &)
                                        if (isinstance(orig_val, UnaryOp) and orig_val.op == "&" and
                                                isinstance(orig_val.operand, CastExpr) and
                                                isinstance(orig_val.operand.operand, InitList)):
                                            cl_type = orig_val.operand.target_type
                                            cl_init = orig_val.operand.operand
                                            if cl_type.struct_def:
                                                anon = self.new_label("compound")
                                                self.pending_compound_literals.append((anon, cl_type.struct_def, cl_init))
                                                elems[j] = anon
                                                continue
                                        val = self._unwrap_compound_literal(item.value)
                                        # Unwrap casts
                                        while isinstance(val, CastExpr):
                                            val = val.operand
                                        # Check if it's an address or function ref
                                        if isinstance(val, UnaryOp) and val.op == "&" and isinstance(val.operand, Identifier):
                                            elems[j] = val.operand.name
                                        elif (isinstance(val, UnaryOp) and val.op == "&" and
                                              isinstance(val.operand, ArrayAccess) and
                                              isinstance(val.operand.array, Identifier)):
                                            arr_name = val.operand.array.name
                                            idx_val = self._try_eval_const(val.operand.index)
                                            if idx_val is not None and idx_val == 0:
                                                elems[j] = arr_name
                                            elif idx_val is not None:
                                                elem_sz = 4
                                                if arr_name in self.global_vars:
                                                    gts = self.global_vars[arr_name].type_spec
                                                    elem_sz = gts.size_bytes()
                                                    if gts.struct_def:
                                                        elem_sz = gts.struct_def.size_bytes()
                                                elems[j] = f"{arr_name}+{idx_val * elem_sz}"
                                        elif isinstance(val, Identifier) and val.name in self.known_functions:
                                            elems[j] = val.name
                                        elif isinstance(val, Identifier) and val.name in self.global_vars:
                                            elems[j] = val.name
                                        elif isinstance(val, Identifier) and val.name in self.static_locals:
                                            # Reference to another static local: use its mangled name
                                            elems[j] = self.static_locals[val.name]
                                        elif isinstance(val, InitList) and val.items:
                                            # Unwrap {func_ptr}
                                            inner = self._unwrap_compound_literal(val.items[0].value)
                                            if isinstance(inner, Identifier) and inner.name in self.known_functions:
                                                elems[j] = inner.name
                                            elif isinstance(inner, UnaryOp) and inner.op == "&" and isinstance(inner.operand, Identifier):
                                                elems[j] = inner.operand.name
                                        elif isinstance(val, StringLiteral):
                                            lbl = self.new_label("str")
                                            self.string_literals.append((lbl, val.value, val.wide))
                                            elems[j] = lbl
                                        else:
                                            cv = self._try_eval_const(val)
                                            if cv is not None:
                                                elems[j] = cv
                                idx = end_idx + 1
                            for val in elems:
                                if val is None:
                                    self.emit(f"    .quad 0")
                                elif isinstance(val, str):
                                    self.emit(f"    .quad {val}")
                                else:
                                    self.emit(f"    .quad {val}")
                        else:
                            # Compute total flat element count for multi-dim
                            total_flat = total_elems
                            inner_count = 1
                            if decl.type_spec.array_sizes and len(decl.type_spec.array_sizes) > 1:
                                for dim in decl.type_spec.array_sizes[1:]:
                                    dv = self._dim_value(dim)
                                    if dv is not None:
                                        inner_count *= dv
                                total_flat = total_elems * inner_count
                            is_float_array = decl.type_spec.base in ("float", "double") and not decl.type_spec.is_pointer()
                            elems = [0] * total_flat
                            flat_idx = 0
                            for item in actual_init.items:
                                if item.designator_index is not None:
                                    flat_idx = item.designator_index * inner_count
                                val = item.value
                                # Unwrap CastExpr
                                while isinstance(val, CastExpr):
                                    val = val.operand
                                if isinstance(val, StringLiteral) and inner_count > 1:
                                    # String literal for char row in 2D char array
                                    row_start = flat_idx
                                    for ch in val.value:
                                        if flat_idx < total_flat:
                                            elems[flat_idx] = ord(ch)
                                        flat_idx += 1
                                    # Null terminator
                                    if flat_idx < total_flat:
                                        elems[flat_idx] = 0
                                    flat_idx = row_start + inner_count
                                elif isinstance(val, InitList) and inner_count >= 1:
                                    # Inner init list for multi-dim array
                                    row_start = flat_idx
                                    for sub_item in val.items:
                                        sv = sub_item.value
                                        while isinstance(sv, CastExpr):
                                            sv = sv.operand
                                        fv = self._try_eval_float_const(sv) if is_float_array else None
                                        if fv is not None and flat_idx < total_flat:
                                            elems[flat_idx] = ('float', fv)
                                        else:
                                            cv = self._try_eval_const(sv)
                                            if cv is not None and flat_idx < total_flat:
                                                if is_float_array:
                                                    elems[flat_idx] = ('float', float(cv))
                                                else:
                                                    elems[flat_idx] = cv
                                        flat_idx += 1
                                    # Advance to next row boundary (zero-fill partial rows)
                                    flat_idx = row_start + inner_count
                                else:
                                    fv = self._try_eval_float_const(val) if is_float_array else None
                                    if fv is not None and flat_idx < total_flat:
                                        elems[flat_idx] = ('float', fv)
                                    else:
                                        cv = self._try_eval_const(val)
                                        if cv is not None and flat_idx < total_flat:
                                            if is_float_array:
                                                elems[flat_idx] = ('float', float(cv))
                                            else:
                                                elems[flat_idx] = cv
                                    flat_idx += 1
                            import struct as _struct
                            for val in elems:
                                if isinstance(val, tuple) and val[0] == 'float':
                                    fval = val[1]
                                    if elem_size <= 4:
                                        packed = _struct.pack('<f', fval)
                                        ival = int.from_bytes(packed, 'little')
                                        self.emit(f"    .long {ival}")
                                    else:
                                        packed = _struct.pack('<d', fval)
                                        ival = int.from_bytes(packed, 'little')
                                        self.emit(f"    .quad {ival}")
                                elif elem_size == 1:
                                    self.emit(f"    .byte {val}")
                                elif elem_size == 2:
                                    self.emit(f"    .word {val}")
                                elif elem_size <= 4:
                                    self.emit(f"    .long {val}")
                                else:
                                    self.emit(f"    .quad {val}")
                elif decl.type_spec.is_extern:
                    pass  # extern declaration — symbol provided by linker, don't emit
                else:
                    self.emit("    .bss")
                    if not decl.type_spec.is_static:
                        self.emit(f"    .globl {name}")
                    size = decl.type_spec.size_bytes()
                    if (decl.type_spec.is_array() or decl.type_spec.is_ptr_array) and decl.type_spec.array_sizes:
                        for dim in decl.type_spec.array_sizes:
                            dv = self._dim_value(dim)
                            if dv is not None:
                                size *= dv
                    align = min(decl.type_spec.size_bytes(), 8)
                    if align < 4:
                        align = 4
                    self.emit(f"    .align {align}")
                    self.label(name)
                    self.emit(f"    .zero {size}")

        # Emit pending anonymous compound literals (from global array inits)
        if self.pending_compound_literals:
            self.emit("")
            self.emit("    .data")
            for anon, sdef, init_list in self.pending_compound_literals:
                self.emit(f"    .align 8")
                self.label(anon)
                self._emit_struct_init_data(sdef, init_list)

        # Generate string literals (at the end, after globals which may add more)
        if self.string_literals:
            self.emit("")
            self.emit("    .section .rodata")
            for lbl, val, *rest in self.string_literals:
                wide = rest[0] if rest else False
                self.label(lbl)
                if wide:
                    for ch in val:
                        self.emit(f"    .long {ord(ch)}")
                    self.emit("    .long 0")
                else:
                    asm_str = ""
                    for ch in val:
                        if ch == '\n': asm_str += "\\n"
                        elif ch == '\t': asm_str += "\\t"
                        elif ch == '\r': asm_str += "\\r"
                        elif ch == '\0': asm_str += "\\0"
                        elif ch == '"': asm_str += '\\"'
                        elif ch == '\\': asm_str += "\\\\"
                        elif 0xF700 <= ord(ch) <= 0xF7FF:
                            # Raw byte from octal/hex escape (stored in PUA)
                            asm_str += f"\\{ord(ch) - 0xF700:03o}"
                        elif ord(ch) > 126:
                            # Encode non-ASCII as UTF-8 bytes
                            for b in ch.encode('utf-8'):
                                asm_str += f"\\{b:03o}"
                        elif ord(ch) < 32: asm_str += f"\\{ord(ch):03o}"
                        else: asm_str += ch
                    self.emit(f'    .string "{asm_str}"')

        return "\n".join(self.output) + "\n"

    def _unwrap_compound_literal(self, expr):
        """Unwrap CastExpr(InitList) -> InitList for compound literals."""
        if isinstance(expr, CastExpr) and isinstance(expr.operand, InitList):
            return expr.operand
        return expr

    def _get_member_total_size(self, ts):
        """Get total size of a type including all array dimensions."""
        size = ts.size_bytes()
        if (ts.is_array() or ts.is_ptr_array) and ts.array_sizes:
            for dim in ts.array_sizes:
                if dim is None:
                    return 0  # Flexible array
                if isinstance(dim, IntLiteral):
                    size *= dim.value
                else:
                    # Runtime-sized (VLA) — can't compute statically
                    return 0
        return size

    def _build_data_bytes(self, sdef, init_list, is_union=False):
        """Build a byte buffer + reloc list for a struct/union initializer.
        Returns (bytes_buf, relocs) where relocs is [(offset, symbol_name), ...].
        Handles brace elision, nested structs, unions, string literals, empty structs."""
        total_size = sdef.size_bytes()
        buf = bytearray(total_size)
        relocs = []

        items = init_list.items
        item_idx = [0]  # mutable for nested consumption

        def consume_item():
            if item_idx[0] < len(items):
                it = items[item_idx[0]]
                item_idx[0] += 1
                return it
            return None

        def peek_item():
            if item_idx[0] < len(items):
                return items[item_idx[0]]
            return None

        def store_byte(off, val):
            if 0 <= off < len(buf):
                buf[off] = val & 0xFF

        def store_val(off, size, val):
            """Store a little-endian integer value."""
            val = val & ((1 << (size * 8)) - 1)
            for i in range(size):
                store_byte(off + i, (val >> (i * 8)) & 0xFF)

        def fill_member(mem_offset, mem_ts, value):
            """Fill a member at given offset with given value expression."""
            value = self._unwrap_compound_literal(value)
            mem_size = mem_ts.size_bytes()
            actual_size = self._get_member_total_size(mem_ts)

            if isinstance(value, StringLiteral) and mem_ts.is_array() and mem_size == 1:
                # String literal for char array
                for i, ch in enumerate(value.value):
                    if mem_offset + i < total_size:
                        store_byte(mem_offset + i, ord(ch))
                # null terminator
                null_off = mem_offset + len(value.value)
                if null_off < total_size:
                    store_byte(null_off, 0)
                return

            if isinstance(value, InitList) and mem_ts.is_array():
                # Array init list (check BEFORE struct to handle struct arrays correctly)
                pass  # fall through to array handler below

            elif isinstance(value, InitList) and mem_ts.struct_def and not mem_ts.is_pointer():
                # Nested struct/union init
                sub_buf, sub_relocs = self._build_data_bytes(
                    mem_ts.struct_def, value, is_union=mem_ts.struct_def.is_union)
                for i, b in enumerate(sub_buf):
                    if mem_offset + i < total_size:
                        buf[mem_offset + i] = b
                for r_off, r_sym in sub_relocs:
                    relocs.append((mem_offset + r_off, r_sym))
                return

            if isinstance(value, InitList) and mem_ts.is_array():
                # Array init list
                arr_elem_size = mem_size
                arr_count = 1
                if mem_ts.array_sizes and mem_ts.array_sizes[0]:
                    first = mem_ts.array_sizes[0]
                    if isinstance(first, IntLiteral):
                        arr_count = first.value
                fill_array(mem_offset, mem_ts, value, arr_elem_size, arr_count)
                return

            # Scalar value
            # Unwrap {value} braces around scalar
            unwrapped = value
            while isinstance(unwrapped, InitList) and unwrapped.items:
                unwrapped = unwrapped.items[0].value
            unwrapped = self._unwrap_compound_literal(unwrapped)
            # Unwrap casts (e.g. (int *) &var)
            while isinstance(unwrapped, CastExpr):
                unwrapped = unwrapped.operand

            cv = self._try_eval_const(unwrapped) if unwrapped else None
            if cv is not None:
                store_val(mem_offset, min(mem_size, actual_size), cv)
            elif isinstance(unwrapped, FloatLiteral):
                import struct as pystruct
                fval = unwrapped.value
                if mem_ts.base == "float" and not mem_ts.is_pointer():
                    packed = pystruct.pack('<f', fval)
                    for bi, bv in enumerate(packed):
                        store_byte(mem_offset + bi, bv)
                elif mem_ts.base == "long double" and not mem_ts.is_pointer():
                    # 80-bit extended precision, stored in 16 bytes
                    # Python doesn't have native 80-bit float support
                    # Use 64-bit double as approximation, stored in first 8 bytes
                    packed = pystruct.pack('<d', fval)
                    for bi, bv in enumerate(packed):
                        store_byte(mem_offset + bi, bv)
                    # Set the rest to form a proper 80-bit representation
                    # Actually, x86 long double is 80-bit: use ctypes
                    try:
                        import ctypes
                        ld = ctypes.c_longdouble(fval)
                        ld_bytes = bytes(ctypes.c_char * 16).join(b'')  # won't work
                        # Fallback: construct from parts
                        raise Exception("use fallback")
                    except Exception:
                        # Encode as 80-bit IEEE 754 extended precision
                        self._store_long_double(buf, mem_offset, fval)
                else:
                    # double
                    packed = pystruct.pack('<d', fval)
                    for bi, bv in enumerate(packed):
                        store_byte(mem_offset + bi, bv)
            elif isinstance(unwrapped, StringLiteral):
                # String literal as a pointer
                lbl = self.new_label("str")
                self.string_literals.append((lbl, unwrapped.value, unwrapped.wide))
                relocs.append((mem_offset, lbl))
            elif (isinstance(unwrapped, UnaryOp) and unwrapped.op == "&" and
                  isinstance(unwrapped.operand, Identifier)):
                relocs.append((mem_offset, unwrapped.operand.name))
            elif (isinstance(unwrapped, UnaryOp) and unwrapped.op == "&" and
                  isinstance(unwrapped.operand, ArrayAccess) and
                  isinstance(unwrapped.operand.array, Identifier)):
                # &array[index] — emit as symbol + offset
                arr_name = unwrapped.operand.array.name
                idx_val = self._try_eval_const(unwrapped.operand.index)
                if idx_val is not None and idx_val == 0:
                    relocs.append((mem_offset, arr_name))
                elif idx_val is not None:
                    # Need symbol+offset: emit as reloc with addend
                    # Get element size from the global var declaration
                    elem_size = 4  # default to int
                    if arr_name in self.global_vars:
                        gdecl = self.global_vars[arr_name]
                        elem_size = gdecl.type_spec.size_bytes()
                    relocs.append((mem_offset, f"{arr_name}+{idx_val * elem_size}"))
            elif isinstance(unwrapped, Identifier) and unwrapped.name in self.known_functions:
                relocs.append((mem_offset, unwrapped.name))
            elif isinstance(unwrapped, Identifier) and unwrapped.name in self.global_vars:
                # Global variable reference (array decaying to pointer)
                relocs.append((mem_offset, unwrapped.name))
            elif isinstance(unwrapped, Identifier) and unwrapped.name in self.static_locals:
                # Static local variable reference (array decaying to pointer)
                relocs.append((mem_offset, self.static_locals[unwrapped.name]))
            elif (isinstance(unwrapped, ArrayAccess) and
                  isinstance(unwrapped.array, Identifier) and
                  unwrapped.array.name in self.global_vars):
                # array[index] — row of 2D array decaying to pointer
                arr_name = unwrapped.array.name
                idx_val = self._try_eval_const(unwrapped.index)
                if idx_val is not None:
                    gdecl = self.global_vars[arr_name]
                    gts = gdecl.type_spec
                    # Row size = element_size * inner_dimension
                    row_size = gts.size_bytes()
                    if gts.struct_def:
                        row_size = gts.struct_def.size_bytes()
                    if gts.array_sizes and len(gts.array_sizes) > 1:
                        for dim in gts.array_sizes[1:]:
                            dv = self._dim_value(dim)
                            if dv is not None:
                                row_size *= dv
                    offset = idx_val * row_size
                    if offset == 0:
                        relocs.append((mem_offset, arr_name))
                    else:
                        relocs.append((mem_offset, f"{arr_name}+{offset}"))

        def fill_array(arr_offset, arr_ts, init, elem_size, arr_count):
            """Fill array from init list items."""
            idx = 0
            for item in init.items:
                if item.designator_index is not None:
                    idx = item.designator_index
                end_idx = idx
                if item.designator_end is not None:
                    end_idx = item.designator_end
                for j in range(idx, end_idx + 1):
                    if j < arr_count:
                        val = self._unwrap_compound_literal(item.value)
                        if arr_ts.struct_def and isinstance(val, InitList):
                            # Struct array element: fill struct members
                            elem_off = arr_offset + j * elem_size
                            sub_buf, sub_relocs = self._build_data_bytes(
                                arr_ts.struct_def, val, is_union=arr_ts.struct_def.is_union)
                            for bi, bv in enumerate(sub_buf):
                                if elem_off + bi < total_size:
                                    buf[elem_off + bi] = bv
                            for r_off, r_sym in sub_relocs:
                                relocs.append((elem_off + r_off, r_sym))
                        else:
                            fill_scalar_or_val(arr_offset + j * elem_size, elem_size, item.value)
                idx = end_idx + 1

        def fill_scalar_or_val(off, size, value):
            """Fill a scalar slot."""
            value = self._unwrap_compound_literal(value)
            # Unwrap braces
            unwrapped = value
            while isinstance(unwrapped, InitList) and unwrapped.items:
                unwrapped = unwrapped.items[0].value
            unwrapped = self._unwrap_compound_literal(unwrapped)
            cv = self._try_eval_const(unwrapped) if unwrapped else None
            if cv is not None:
                store_val(off, size, cv)
            elif isinstance(unwrapped, StringLiteral):
                lbl = self.new_label("str")
                self.string_literals.append((lbl, unwrapped.value, unwrapped.wide))
                relocs.append((off, lbl))
            elif (isinstance(value, UnaryOp) and value.op == "&" and
                  isinstance(value.operand, CastExpr) and isinstance(value.operand.operand, InitList)):
                # &(struct T){...} — anonymous compound literal, emit as static
                cl_type = value.operand.target_type
                cl_init = value.operand.operand
                if cl_type.struct_def:
                    anon = self.new_label("compound")
                    self.pending_compound_literals.append((anon, cl_type.struct_def, cl_init))
                    relocs.append((off, anon))
            elif (isinstance(unwrapped, UnaryOp) and unwrapped.op == "&" and
                  isinstance(unwrapped.operand, Identifier)):
                relocs.append((off, unwrapped.operand.name))
            elif isinstance(unwrapped, Identifier) and unwrapped.name in self.known_functions:
                relocs.append((off, unwrapped.name))

        def get_member_offset(sdef_, name):
            """Get offset of a member in a struct."""
            return sdef_.member_offset(name)

        def fill_struct_sequential(sdef_, base_off, items_ref, item_idx_ref):
            """Fill struct members sequentially from items, handling brace elision."""
            members = sdef_.members
            mem_idx = 0

            while mem_idx < len(members) or (item_idx_ref[0] < len(items_ref) and items_ref[item_idx_ref[0]].designator):
                if mem_idx >= len(members):
                    # Past end but next item has designator - handle it
                    it = items_ref[item_idx_ref[0]]
                    found = False
                    for mi, m in enumerate(members):
                        if m.name == it.designator:
                            mem_idx = mi
                            found = True
                            break
                        if m.name == "" and m.type_spec.struct_def:
                            sub_off = m.type_spec.struct_def.member_offset(it.designator)
                            if sub_off is not None:
                                mem_idx = mi
                                found = True
                                break
                    if not found:
                        break
                mem = members[mem_idx]
                # Calculate member offset
                mem_off = get_member_offset(sdef_, mem.name)
                if mem_off is None:
                    # Anonymous member - try to handle inline
                    if mem.name == "" and mem.type_spec.struct_def:
                        sub_sdef = mem.type_spec.struct_def
                        # Compute offset of anonymous member manually
                        off = 0
                        for m2 in sdef_.members:
                            al = sdef_._member_align(m2.type_spec)
                            act_size = self._get_member_total_size(m2.type_spec)
                            if al > 0:
                                off = (off + al - 1) & ~(al - 1)
                            if m2 is mem:
                                break
                            off += act_size
                        # Check if current item is a braced InitList -> use directly
                        it = peek_item_ref(items_ref, item_idx_ref)
                        if it and isinstance(self._unwrap_compound_literal(it.value), InitList):
                            consume_item_ref(items_ref, item_idx_ref)
                            fill_member(base_off + off, mem.type_spec,
                                       self._unwrap_compound_literal(it.value))
                        else:
                            # Brace elision: fill sub-members from parent items
                            fill_struct_sequential(sub_sdef, base_off + off, items_ref, item_idx_ref)
                        mem_idx += 1
                        continue
                    mem_idx += 1
                    continue

                abs_off = base_off + mem_off
                mem_ts = mem.type_spec
                actual_size = self._get_member_total_size(mem_ts)

                # Empty struct member (size 0): skip it
                if actual_size == 0:
                    # Consume an item if available (empty struct init)
                    it = peek_item_ref(items_ref, item_idx_ref)
                    if it and isinstance(it.value, CastExpr) and isinstance(it.value.operand, InitList):
                        consume_item_ref(items_ref, item_idx_ref)
                    elif it and isinstance(it.value, InitList) and len(it.value.items) == 0:
                        consume_item_ref(items_ref, item_idx_ref)
                    mem_idx += 1
                    continue

                it = peek_item_ref(items_ref, item_idx_ref)
                if it is None:
                    break

                # Check designator
                if it.designator:
                    # Jump to designated member
                    found = False
                    for mi, m in enumerate(members):
                        if m.name == it.designator:
                            mem_idx = mi
                            mem = m
                            mem_off = get_member_offset(sdef_, m.name)
                            abs_off = base_off + mem_off
                            mem_ts = m.type_spec
                            actual_size = self._get_member_total_size(mem_ts)
                            found = True
                            break
                        # Check anonymous sub-members
                        if m.name == "" and m.type_spec.struct_def:
                            sub_off = m.type_spec.struct_def.member_offset(it.designator)
                            if sub_off is not None:
                                # Found in anonymous member
                                anon_mem_off = get_member_offset(sdef_, "")
                                if anon_mem_off is None:
                                    # compute manually
                                    aoff = 0
                                    for m2 in members:
                                        es = m2.type_spec.size_bytes()
                                        asz = self._get_member_total_size(m2.type_spec)
                                        al = min(es, 8) if es > 0 else 1
                                        if al > 0:
                                            aoff = (aoff + al - 1) & ~(al - 1)
                                        if m2 is m:
                                            break
                                        aoff += asz
                                    anon_mem_off = aoff
                                sub_ts = m.type_spec.struct_def.member_type(it.designator)
                                consume_item_ref(items_ref, item_idx_ref)
                                fill_member(base_off + anon_mem_off + sub_off, sub_ts, it.value)
                                mem_idx = mi + 1
                                found = True
                                break
                    if not found:
                        consume_item_ref(items_ref, item_idx_ref)
                        mem_idx += 1
                        continue
                    if it.designator and not (it.designator_path and len(it.designator_path) > 1):
                        pass  # will handle below
                    # Check for chained designator path like .a.j
                    if it.designator_path and len(it.designator_path) > 1:
                        # Navigate to nested member
                        consume_item_ref(items_ref, item_idx_ref)
                        curr_off = abs_off
                        curr_sdef = mem_ts.struct_def
                        for dp in it.designator_path[1:]:
                            if curr_sdef:
                                sub_off = curr_sdef.member_offset(dp)
                                if sub_off is not None:
                                    curr_off += sub_off
                                    curr_ts = curr_sdef.member_type(dp)
                                    curr_sdef = curr_ts.struct_def if curr_ts else None
                        fill_member(curr_off, curr_ts if curr_ts else mem_ts, it.value)
                        mem_idx += 1
                        continue

                # Consume the item
                consume_item_ref(items_ref, item_idx_ref)
                val = self._unwrap_compound_literal(it.value)

                # Check if value is an InitList -> fills the member directly
                if isinstance(val, InitList):
                    fill_member(abs_off, mem_ts, val)
                elif isinstance(val, StringLiteral) and mem_ts.is_array() and mem_ts.size_bytes() == 1:
                    fill_member(abs_off, mem_ts, val)
                elif mem_ts.struct_def and not mem_ts.is_pointer() and not isinstance(val, InitList):
                    # Brace elision: fill nested struct by consuming more items
                    # Put this item back and fill from the items
                    item_idx_ref[0] -= 1
                    sub_items_ref = items_ref
                    fill_struct_sequential(mem_ts.struct_def, abs_off, sub_items_ref, item_idx_ref)
                elif mem_ts.is_array() and not isinstance(val, InitList):
                    # Brace elision for array: consume scalars
                    elem_sz = mem_ts.size_bytes()
                    arr_count = 1
                    if mem_ts.array_sizes and mem_ts.array_sizes[0]:
                        first = mem_ts.array_sizes[0]
                        if isinstance(first, IntLiteral):
                            arr_count = first.value
                    # Put back and fill
                    item_idx_ref[0] -= 1
                    for ai in range(arr_count):
                        ait = peek_item_ref(items_ref, item_idx_ref)
                        if ait is None or ait.designator:
                            break
                        consume_item_ref(items_ref, item_idx_ref)
                        cv = self._try_eval_const(ait.value)
                        if cv is not None:
                            store_val(abs_off + ai * elem_sz, elem_sz, cv)
                else:
                    # Scalar value
                    fill_member(abs_off, mem_ts, val)

                if sdef_.is_union:
                    # Union: only initialize first member
                    break

                mem_idx += 1

        def peek_item_ref(items_ref, idx_ref):
            if idx_ref[0] < len(items_ref):
                return items_ref[idx_ref[0]]
            return None

        def consume_item_ref(items_ref, idx_ref):
            if idx_ref[0] < len(items_ref):
                it = items_ref[idx_ref[0]]
                idx_ref[0] += 1
                return it
            return None

        fill_struct_sequential(sdef, 0, items, item_idx)

        return buf, relocs

    def _emit_struct_init_data(self, sdef, init_list):
        """Emit data section entries for a struct initializer."""
        init_list_unwrapped = init_list
        if isinstance(init_list, CastExpr) and isinstance(init_list.operand, InitList):
            init_list_unwrapped = init_list.operand
        if not isinstance(init_list_unwrapped, InitList):
            self.emit(f"    .zero {sdef.size_bytes()}")
            return

        buf, relocs = self._build_data_bytes(sdef, init_list_unwrapped, is_union=sdef.is_union)

        # Emit byte-by-byte, coalescing zeros and handling relocs
        reloc_offsets = {r[0]: r[1] for r in relocs}
        i = 0
        total = len(buf)
        while i < total:
            if i in reloc_offsets:
                self.emit(f"    .quad {reloc_offsets[i]}")
                i += 8
            elif buf[i] == 0:
                # Count consecutive zeros
                j = i
                while j < total and j not in reloc_offsets and buf[j] == 0:
                    j += 1
                self.emit(f"    .zero {j - i}")
                i = j
            else:
                self.emit(f"    .byte {buf[i]}")
                i += 1

    def _store_long_double(self, buf, offset, fval):
        """Store a float value as 80-bit x86 extended precision (padded to 16 bytes)."""
        import ctypes
        # Use ctypes to get the correct long double representation
        try:
            ld = ctypes.c_longdouble(fval)
            # Get bytes via pointer cast
            ptr = ctypes.cast(ctypes.pointer(ld), ctypes.POINTER(ctypes.c_ubyte * 16))
            ld_bytes = bytes(ptr.contents)
            for i in range(min(16, len(buf) - offset)):
                buf[offset + i] = ld_bytes[i]
        except Exception:
            # Fallback: store as double in first 8 bytes
            import struct as pystruct
            packed = pystruct.pack('<d', fval)
            for i in range(8):
                if offset + i < len(buf):
                    buf[offset + i] = packed[i]

    def _dim_value(self, dim) -> Optional[int]:
        """Evaluate an array dimension expression to an integer."""
        if isinstance(dim, IntLiteral):
            return dim.value
        return self._try_eval_const(dim)

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
                if (ts.base.startswith("struct ") or ts.base.startswith("union ")) and \
                   not ts.struct_def and not ts.is_pointer():
                    import sys
                    print(f"warning: sizeof applied to unknown type '{ts.base}' "
                          f"(defaulting to {size})", file=sys.stderr)
                if (ts.is_array() or (ts.is_ptr_array)) and ts.array_sizes:
                    first = ts.array_sizes[0]
                    if isinstance(first, IntLiteral):
                        size *= first.value
                return size
            # sizeof on expression
            if isinstance(expr.operand, Identifier):
                _, ts = self.get_var_location(expr.operand.name)
                if ts:
                    size = ts.size_bytes()
                    if (ts.is_array() or (ts.is_ptr_array)) and ts.array_sizes:
                        first = ts.array_sizes[0]
                        if isinstance(first, IntLiteral):
                            size *= first.value
                    return size
            # sizeof(array[i]) — array element: get element type size
            if isinstance(expr.operand, ArrayAccess) and isinstance(expr.operand.array, Identifier):
                _, ts = self.get_var_location(expr.operand.array.name)
                if ts:
                    if ts.is_ptr_array or (ts.is_array() and ts.pointer_depth > 0):
                        return 8  # element is a pointer
                    elem_ts = TypeSpec(base=ts.base, pointer_depth=max(ts.pointer_depth - 1, 0),
                                      is_unsigned=ts.is_unsigned, struct_def=ts.struct_def,
                                      enum_def=ts.enum_def)
                    # For multi-dim arrays, element includes remaining dimensions
                    if ts.array_sizes and len(ts.array_sizes) > 1:
                        size = elem_ts.size_bytes()
                        for dim in ts.array_sizes[1:]:
                            dv = self._dim_value(dim) if dim is not None else None
                            if dv is not None:
                                size *= dv
                        return size
                    return elem_ts.size_bytes()
            # sizeof(compound_literal) — e.g., sizeof((struct ntd[]){...})
            if isinstance(expr.operand, CastExpr) and isinstance(expr.operand.operand, InitList):
                cl_type = expr.operand.target_type
                if cl_type.is_array():
                    elem_size = cl_type.size_bytes()
                    if cl_type.struct_def:
                        elem_size = cl_type.struct_def.size_bytes()
                    n_items = len(expr.operand.operand.items)
                    return elem_size * n_items
                elif cl_type.struct_def:
                    return cl_type.struct_def.size_bytes()
                return cl_type.size_bytes()
            # sizeof(*expr) — dereference: get element type size
            if isinstance(expr.operand, UnaryOp) and expr.operand.op == "*":
                inner = expr.operand.operand
                if isinstance(inner, Identifier):
                    _, ts = self.get_var_location(inner.name)
                    if ts:
                        if ts.is_ptr_array or (ts.is_array() and ts.pointer_depth > 0):
                            return 8  # element is a pointer
                        elif ts.is_pointer() and ts.array_sizes:
                            # Pointer-to-array: *p gives the array, size = base_size * product(dims)
                            elem = TypeSpec(base=ts.base, pointer_depth=ts.pointer_depth - 1,
                                            struct_def=ts.struct_def).size_bytes()
                            for dim in ts.array_sizes:
                                dv = self._dim_value(dim) if dim is not None else None
                                if dv is not None:
                                    elem *= dv
                            return elem
                        elif ts.is_pointer():
                            return TypeSpec(base=ts.base, pointer_depth=ts.pointer_depth - 1,
                                            struct_def=ts.struct_def).size_bytes()
                        elif ts.is_array():
                            return ts.size_bytes()
            return 4
        return None

    def _try_eval_float_const(self, expr) -> Optional[float]:
        """Try to evaluate an expression as a compile-time float constant."""
        if isinstance(expr, FloatLiteral):
            return expr.value
        if isinstance(expr, IntLiteral):
            return float(expr.value)
        if isinstance(expr, CastExpr):
            return self._try_eval_float_const(expr.operand)
        if isinstance(expr, UnaryOp) and expr.op == "-":
            val = self._try_eval_float_const(expr.operand)
            if val is not None:
                return -val
        return None

    def gen_function(self, func: FuncDecl):
        self.current_func = func
        self.locals = {}
        self.params = {}
        self.static_locals = {}
        self.vla_sizes = {}  # VLA name -> stack offset of saved size
        self.vla_dim_offsets = {}  # VLA name -> list of stack offsets for runtime inner dims
        self.stack_offset = -8  # -8(%rbp) is used by saved %rbx
        if hasattr(self, '_va_area_offset'):
            del self._va_area_offset

        self.emit("")
        if not (func.return_type and func.return_type.is_static):
            self.emit(f"    .globl {func.name}")
        self.emit(f"    .type {func.name}, @function")
        self.label(func.name)

        # Prologue
        self.emit("    pushq %rbp")
        self.emit("    movq %rsp, %rbp")
        self.emit("    pushq %rbx")  # save callee-saved %rbx (used for call alignment)

        # We'll patch the stack allocation later
        stack_alloc_idx = len(self.output)
        self.emit("    subq $PLACEHOLDER, %rsp")  # placeholder

        # If function returns struct > 16 bytes, hidden pointer in %rdi
        self._hidden_ret_ptr_offset = None
        if func.return_type and self._is_struct_by_value(func.return_type):
            ret_size = func.return_type.size_bytes()
            if ret_size > 16:
                self.stack_offset -= 8
                self._hidden_ret_ptr_offset = self.stack_offset
                self.emit(f"    movq %rdi, {self.stack_offset}(%rbp)")

        # For variadic functions, save all 6 GP registers + 8 xmm registers.
        # Layout: [0..47] GP regs (rdi,rsi,rdx,rcx,r8,r9)
        #         [48..175] xmm0..xmm7 (16 bytes each)
        if func.is_variadic:
            self.stack_offset -= 176  # 48 gp + 128 xmm
            self._va_area_offset = self.stack_offset
            for ri, reg in enumerate(self.ARG_REGS_64):
                self.emit(f"    movq {reg}, {self._va_area_offset + ri * 8}(%rbp)")
            # Save xmm0..xmm7 (16 bytes each) — only if any were potentially used.
            # Guard with %al (set by caller to # of xmm args used, typical variadic ABI).
            va_save_end = self.new_label("va_save_end")
            self.emit(f"    testb %al, %al")
            self.emit(f"    je {va_save_end}")
            for xi in range(8):
                self.emit(f"    movups %xmm{xi}, {self._va_area_offset + 48 + xi * 16}(%rbp)")
            self.label(va_save_end)

        # Save parameters to stack (float params come in xmm registers)
        int_param_idx = 0
        # Account for hidden return pointer consuming %rdi
        if self._hidden_ret_ptr_offset is not None:
            int_param_idx = 1
        xmm_param_idx = 0
        stack_param_offset = 16  # first stack arg is at 16(%rbp) (above saved rbp and return addr)
        for i, param in enumerate(func.params):
            size = param.type_spec.size_bytes()
            is_float_param = (param.type_spec.base in ("float", "double", "long double")
                              and not param.type_spec.is_pointer()
                              and not param.type_spec.struct_def)
            is_struct = self._is_struct_by_value(param.type_spec)

            if is_struct:
                # Struct parameter: allocate full size on stack
                alloc = (size + 7) & ~7
                self.stack_offset -= alloc
                self.params[param.name] = (self.stack_offset, param.type_spec)
                if size <= 8 and int_param_idx < 6:
                    self.emit(f"    movq {self.ARG_REGS_64[int_param_idx]}, {self.stack_offset}(%rbp)")
                    int_param_idx += 1
                elif size <= 16 and int_param_idx + 1 < 6:
                    # Two registers
                    self.emit(f"    movq {self.ARG_REGS_64[int_param_idx]}, {self.stack_offset}(%rbp)")
                    self.emit(f"    movq {self.ARG_REGS_64[int_param_idx + 1]}, {self.stack_offset + 8}(%rbp)")
                    int_param_idx += 2
                elif size > 16 and int_param_idx < 6:
                    # Passed by pointer: copy from pointer to local
                    self.emit(f"    movq {self.ARG_REGS_64[int_param_idx]}, %rax")
                    self._emit_memcpy_from_rax(self.stack_offset, size)
                    int_param_idx += 1
                else:
                    # From stack
                    if size > 16:
                        # >16 bytes: stack has a pointer to the struct
                        self.emit(f"    movq {stack_param_offset}(%rbp), %rax")
                        self._emit_memcpy_from_rax(self.stack_offset, size)
                        stack_param_offset += 8
                    else:
                        # <=16 bytes: struct data directly on stack
                        for off in range(0, alloc, 8):
                            self.emit(f"    movq {stack_param_offset + off}(%rbp), %rax")
                            self.emit(f"    movq %rax, {self.stack_offset + off}(%rbp)")
                        stack_param_offset += alloc
            elif is_float_param and xmm_param_idx < 8:
                self.stack_offset -= 8
                self.params[param.name] = (self.stack_offset, param.type_spec)
                # Float param: save from xmm register
                if param.type_spec.base == "float":
                    self.emit(f"    cvtsd2ss %xmm{xmm_param_idx}, %xmm{xmm_param_idx}")
                    self.emit(f"    movss %xmm{xmm_param_idx}, {self.stack_offset}(%rbp)")
                else:
                    self.emit(f"    movsd %xmm{xmm_param_idx}, {self.stack_offset}(%rbp)")
                xmm_param_idx += 1
            elif not is_float_param and int_param_idx < 6:
                self.stack_offset -= 8
                self.params[param.name] = (self.stack_offset, param.type_spec)
                if size <= 4:
                    self.emit(f"    movl {self.ARG_REGS_32[int_param_idx]}, {self.stack_offset}(%rbp)")
                else:
                    self.emit(f"    movq {self.ARG_REGS_64[int_param_idx]}, {self.stack_offset}(%rbp)")
                int_param_idx += 1
            else:
                self.stack_offset -= 8
                self.params[param.name] = (self.stack_offset, param.type_spec)
                self.emit(f"    movq {stack_param_offset}(%rbp), %rax")
                self.emit(f"    movq %rax, {self.stack_offset}(%rbp)")
                stack_param_offset += 8

        # Generate body
        self.gen_block(func.body)

        # Default return 0 for main, or just ret for void functions
        if func.name == "main":
            self.emit("    movl $0, %eax")
        self.emit("    movq -8(%rbp), %rbx")  # restore callee-saved %rbx
        self.emit("    leave")
        self.emit("    ret")

        # Patch stack allocation (align to 16)
        # After pushq %rbp and pushq %rbx, rsp is 16-aligned minus 8.
        # So subq needs to be 8 mod 16 to restore 16-byte alignment.
        raw = -self.stack_offset
        total_stack = (raw + 15) & ~15
        if total_stack % 16 == 0:
            total_stack += 8  # ensure rsp ends 16-aligned after odd push count
        if total_stack == 0:
            total_stack = 8
        self.output[stack_alloc_idx] = f"    subq ${total_stack}, %rsp"
        # Zero-initialize declared local variables area (not the full frame
        # padding) to prevent UB from uninitialized locals.
        # Only zero the actual locals region, not alignment padding beyond it.
        # IMPORTANT: preserve %eax (contains # xmm regs for variadic)
        locals_size = -self.stack_offset - 8  # subtract saved rbx at -8
        if locals_size > 0:
            zero_code = []
            zero_code.append("    pushq %rax")  # preserve %al for variadic xmm save
            zero_code.append("    pushq %rdi")
            zero_code.append("    pushq %rcx")
            zero_code.append(f"    leaq -{locals_size + 8}(%rbp), %rdi")
            zero_code.append(f"    movl ${locals_size}, %ecx")
            zero_code.append("    xorl %eax, %eax")
            zero_code.append("    rep stosb")
            zero_code.append("    popq %rcx")
            zero_code.append("    popq %rdi")
            zero_code.append("    popq %rax")
            for i, line in enumerate(zero_code):
                self.output.insert(stack_alloc_idx + 1 + i, line)

    def gen_block(self, block: Block):
        # Only apply scope save/restore for blocks that contain non-declaration
        # statements (real { } blocks), not synthetic blocks from comma-separated decls
        has_non_decl = any(not isinstance(s, VarDecl) for s in block.stmts)
        if has_non_decl:
            saved_locals = dict(self.locals)
        for stmt in block.stmts:
            self.gen_stmt(stmt)
        if has_non_decl:
            self.locals = saved_locals

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
            if hasattr(stmt, '_label'):
                self.label(stmt._label)
            self.gen_stmt(stmt.stmt)
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
            # Check if returning a struct by value
            ret_type = None
            if self.current_func and self.current_func.return_type:
                ret_type = self.current_func.return_type
            if ret_type and self._is_struct_by_value(ret_type):
                size = ret_type.size_bytes()
                # Get address of the struct being returned
                if isinstance(stmt.value, Identifier):
                    loc, vts = self.get_var_location(stmt.value.name)
                    if stmt.value.name in self.locals or stmt.value.name in self.params:
                        off = (self.locals.get(stmt.value.name) or self.params.get(stmt.value.name))[0]
                        self.emit(f"    leaq {off}(%rbp), %rcx")
                    elif stmt.value.name in self.static_locals:
                        mangled = self.static_locals[stmt.value.name]
                        self.emit(f"    leaq {mangled}(%rip), %rcx")
                    else:
                        self.emit(f"    leaq {stmt.value.name}(%rip), %rcx")
                elif isinstance(stmt.value, FuncCall):
                    # FuncCall returning a struct
                    # Allocate temp space and call - then copy/return via hidden ptr if needed
                    if size > 16:
                        # Pass our own hidden ret ptr to the called function so it
                        # writes the result directly to where our caller expects it.
                        self.emit(f"    movq {self._hidden_ret_ptr_offset}(%rbp), %rdi")
                        # Generate call - it writes to the buffer and returns the pointer in %rax
                        # We need to ensure the FuncCall codegen uses our %rdi as hidden ptr.
                        # Save and restore: easier approach is to allocate temp space
                        # and copy. But for now: allocate temp and copy.
                        self.stack_offset -= ((size + 15) & ~15)
                        tmp_off = self.stack_offset
                        # Tell gen_func_call to use this temp as the hidden ret ptr
                        self._struct_ret_dest = tmp_off
                        self.gen_expr(stmt.value)
                        self._struct_ret_dest = None
                        self.emit(f"    leaq {tmp_off}(%rbp), %rcx")
                    else:
                        self.gen_expr(stmt.value)
                        # For size<=16, return value is in rax/rdx; need to put on stack to address
                        self.stack_offset -= 16
                        tmp_off = self.stack_offset
                        self.emit(f"    movq %rax, {tmp_off}(%rbp)")
                        if size > 8:
                            self.emit(f"    movq %rdx, {tmp_off + 8}(%rbp)")
                        self.emit(f"    leaq {tmp_off}(%rbp), %rcx")
                else:
                    self.gen_lvalue_addr(stmt.value)
                    self.emit("    movq %rax, %rcx")

                if size <= 8:
                    self.emit("    movq (%rcx), %rax")
                elif size <= 16:
                    self.emit("    movq (%rcx), %rax")
                    self.emit("    movq 8(%rcx), %rdx")
                else:
                    # >16 bytes: hidden pointer was passed in %rdi (first param)
                    # Copy struct to *%rdi and return %rdi in %rax
                    # The hidden pointer was saved to the first param slot
                    # For now, assume it's the first integer param saved
                    self.emit(f"    movq {self._hidden_ret_ptr_offset}(%rbp), %rdi")
                    for off in range(0, size, 8):
                        if off + 8 <= size:
                            self.emit(f"    movq {off}(%rcx), %r11")
                            self.emit(f"    movq %r11, {off}(%rdi)")
                        else:
                            for b in range(off, size):
                                self.emit(f"    movb {b}(%rcx), %r11b")
                                self.emit(f"    movb %r11b, {b}(%rdi)")
                    self.emit("    movq %rdi, %rax")
            else:
                self.gen_expr(stmt.value)
                # Result is in %rax/%eax — convert/move to xmm0 if returning float/double
                if ret_type and ret_type.base in ("float", "double") and not ret_type.is_pointer():
                    if not (ret_type.struct_def and ret_type.pointer_depth == 0):
                        # If the returned expression is an integer type, convert to float
                        val_is_float = self._is_float_type(stmt.value)
                        if not val_is_float:
                            # Integer value in %eax/%rax — convert to double
                            val_type = self.get_expr_type(stmt.value)
                            if val_type and (val_type.base in ("long", "long long") or val_type.is_pointer()):
                                if val_type.is_unsigned:
                                    # Unsigned 64-bit -> double (cvtsi2sd treats as signed)
                                    self.emit("    cvtsi2sdq %rax, %xmm0")
                                else:
                                    self.emit("    cvtsi2sdq %rax, %xmm0")
                            else:
                                self.emit("    cvtsi2sd %eax, %xmm0")
                            if ret_type.base == "float":
                                self.emit("    cvtsd2ss %xmm0, %xmm0")
                        else:
                            self.emit("    movq %rax, %xmm0")
        self.emit("    movq -8(%rbp), %rbx")  # restore callee-saved %rbx
        self.emit("    leave")
        self.emit("    ret")

    def gen_var_decl(self, decl: VarDecl):
        if decl.name in ("__skip__", ""):
            return  # Skip no-op declarations

        size = decl.type_spec.size_bytes()

        # Static local variable: store as a global with mangled name
        if decl.type_spec.is_static and self.current_func:
            mangled = f"__static_{self.current_func.name}_{decl.name}"
            # Infer array size from initializer if unsized (e.g., static int a[] = {1,2,3})
            ts = decl.type_spec
            if (ts.is_array() or ts.is_ptr_array) and ts.array_sizes and ts.array_sizes[0] is None:
                if isinstance(decl.init, InitList):
                    count = len(decl.init.items)
                    ts.array_sizes[0] = IntLiteral(value=count)
                elif isinstance(decl.init, StringLiteral):
                    ts.array_sizes[0] = IntLiteral(value=len(decl.init.value) + 1)
            gdecl = GlobalVarDecl(type_spec=decl.type_spec, name=mangled, init=decl.init)
            self.global_vars[mangled] = gdecl
            self.static_locals[decl.name] = mangled
            return

        _is_local_array = decl.type_spec.is_array() or (decl.type_spec.is_ptr_array)
        if _is_local_array and decl.type_spec.array_sizes:
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
            # Check if any inner dim is a VLA (non-constant). If so, route to
            # VLA path even if the outer dim is constant.
            inner_has_vla = False
            for dim in (decl.type_spec.array_sizes or [])[1:]:
                if dim is None:
                    continue
                if not isinstance(dim, IntLiteral):
                    if self._try_eval_const(dim) is None:
                        inner_has_vla = True
                        break

            if isinstance(first, IntLiteral) and not inner_has_vla:
                elem_size = size
                if decl.type_spec.is_struct():
                    elem_size = decl.type_spec.struct_def.size_bytes()
                total = elem_size
                # Multiply all dimensions for multi-dim arrays
                for dim in decl.type_spec.array_sizes:
                    if isinstance(dim, IntLiteral):
                        total *= dim.value
                    else:
                        cv = self._try_eval_const(dim) if dim else None
                        if cv:
                            total *= cv
            else:
                # Variable-length array: runtime stack allocation
                self.gen_expr(first)  # size expression in %eax
                elem_size = size
                # Check for struct element size
                if decl.type_spec.struct_def:
                    elem_size = decl.type_spec.struct_def.size_bytes()
                # Collect runtime inner dimensions that need runtime multiply
                runtime_inner_dims = []
                # Multiply by all remaining dimensions (e.g., char a[n][15] or a[n][m])
                for dim in decl.type_spec.array_sizes[1:]:
                    if isinstance(dim, IntLiteral):
                        elem_size *= dim.value
                    else:
                        cv = self._try_eval_const(dim) if dim else None
                        if cv:
                            elem_size *= cv
                        elif dim is not None:
                            runtime_inner_dims.append(dim)
                if elem_size != 1:
                    self.emit(f"    imull ${elem_size}, %eax")
                # Multiply by runtime inner dimensions
                for rdim in runtime_inner_dims:
                    self.emit("    pushq %rax")  # save current total
                    self.gen_expr(rdim)
                    self.emit("    movl %eax, %ecx")
                    self.emit("    popq %rax")
                    self.emit("    imull %ecx, %eax")
                # Save unaligned total size for sizeof
                self.emit("    movslq %eax, %rax")
                self.stack_offset -= 8
                vla_size_off = self.stack_offset
                self.emit(f"    movq %rax, {vla_size_off}(%rbp)")
                self.vla_sizes[decl.name] = vla_size_off
                # Save runtime inner dimension values for stride calculation during indexing
                vla_dim_offsets = []
                for rdim in runtime_inner_dims:
                    self.emit("    pushq %rax")  # save size
                    self.gen_expr(rdim)
                    self.emit("    movslq %eax, %rax")
                    self.stack_offset -= 8
                    dim_off = self.stack_offset
                    self.emit(f"    movq %rax, {dim_off}(%rbp)")
                    self.emit("    popq %rax")  # restore size
                    vla_dim_offsets.append(dim_off)
                if not hasattr(self, 'vla_dim_offsets'):
                    self.vla_dim_offsets = {}
                if vla_dim_offsets:
                    self.vla_dim_offsets[decl.name] = vla_dim_offsets
                # Align to 16
                self.emit("    addl $15, %eax")
                self.emit("    andl $-16, %eax")
                self.emit("    movslq %eax, %rax")
                self.emit("    subq %rax, %rsp")  # allocate on stack
                # Store the pointer (rsp is now the base of the VLA)
                self.stack_offset -= 8
                # Preserve inner dimensions so indexing computes correct stride
                inner_dims = decl.type_spec.array_sizes[1:] if len(decl.type_spec.array_sizes) > 1 else None
                self.locals[decl.name] = (self.stack_offset, TypeSpec(
                    base=decl.type_spec.base, pointer_depth=decl.type_spec.pointer_depth + 1,
                    is_unsigned=decl.type_spec.is_unsigned, struct_def=decl.type_spec.struct_def,
                    enum_def=decl.type_spec.enum_def,
                    array_sizes=inner_dims))
                self.emit(f"    movq %rsp, {self.stack_offset}(%rbp)")
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
            is_real_array = decl.type_spec.is_array() or (decl.type_spec.is_ptr_array)
            if isinstance(decl.init, InitList) and decl.type_spec.struct_def and not is_real_array:
                self.gen_struct_init(decl.name, decl.type_spec, decl.init)
            elif isinstance(decl.init, InitList) and is_real_array:
                self.gen_array_init(decl.name, decl.type_spec, decl.init)
            elif isinstance(decl.init, StringLiteral) and decl.type_spec.is_array():
                # char s[] = "..." or wchar_t s[] = L"..."
                base_offset = self.locals[decl.name][0]
                s = decl.init
                if s.wide:
                    for i, ch in enumerate(s.value):
                        self.emit(f"    movl ${ord(ch)}, {base_offset + i * 4}(%rbp)")
                    self.emit(f"    movl $0, {base_offset + len(s.value) * 4}(%rbp)")
                else:
                    for i, ch in enumerate(s.value):
                        self.emit(f"    movb ${ord(ch)}, {base_offset + i}(%rbp)")
                    self.emit(f"    movb $0, {base_offset + len(s.value)}(%rbp)")
            elif self._is_struct_by_value(decl.type_spec) and not isinstance(decl.init, InitList):
                # Struct init from expression (function call, va_arg, variable, etc.)
                offset = self.locals[decl.name][0]
                struct_size = decl.type_spec.size_bytes()

                if isinstance(decl.init, BuiltinVaArg):
                    # va_arg returns address of struct temp in %rax
                    self.gen_expr(decl.init)
                    self._emit_memcpy_from_rax(offset, struct_size)
                elif isinstance(decl.init, FuncCall):
                    # Function returning struct: value in %rax (and %rdx for 9-16 bytes)
                    self.gen_expr(decl.init)
                    if struct_size <= 8:
                        self.emit(f"    movq %rax, {offset}(%rbp)")
                    elif struct_size <= 16:
                        self.emit(f"    movq %rax, {offset}(%rbp)")
                        self.emit(f"    movq %rdx, {offset + 8}(%rbp)")
                    else:
                        # >16 bytes: return value is pointer in %rax
                        self._emit_memcpy_from_rax(offset, struct_size)
                elif isinstance(decl.init, Identifier):
                    # Copy from another struct variable
                    name = decl.init.name
                    if name in self.locals or name in self.params:
                        src_off = (self.locals.get(name) or self.params.get(name))[0]
                        self._emit_memcpy_stack(offset, src_off, struct_size)
                    elif name in self.static_locals:
                        mangled = self.static_locals[name]
                        self.emit(f"    leaq {mangled}(%rip), %rax")
                        self._emit_memcpy_from_rax(offset, struct_size)
                    else:
                        self.emit(f"    leaq {name}(%rip), %rax")
                        self._emit_memcpy_from_rax(offset, struct_size)
                elif isinstance(decl.init, Assignment):
                    # Chained struct assignment: pq[0] = pq[1] returns dest addr in %rax
                    self.gen_expr(decl.init)
                    self._emit_memcpy_from_rax(offset, struct_size)
                else:
                    # Generic struct expression: get address and copy
                    self.gen_lvalue_addr(decl.init)
                    self._emit_memcpy_from_rax(offset, struct_size)
            else:
                is_float_var = decl.type_spec.base in ("float", "double") and not decl.type_spec.is_pointer()
                is_float_init = isinstance(decl.init, FloatLiteral) or self._is_float_type(decl.init)
                self.gen_expr(decl.init)
                offset = self.locals[decl.name][0]

                if is_float_var and not is_float_init:
                    # int -> float: convert and store
                    self.emit(f"    cvtsi2sd %eax, %xmm0")
                    if decl.type_spec.base == "float":
                        self.emit(f"    cvtsd2ss %xmm0, %xmm0")
                        self.emit(f"    movss %xmm0, {offset}(%rbp)")
                    else:
                        self.emit(f"    movsd %xmm0, {offset}(%rbp)")
                elif not is_float_var and is_float_init:
                    # float -> int: convert (value in xmm0 and rax)
                    self.emit(f"    movq %rax, %xmm0")
                    self.emit(f"    cvttsd2si %xmm0, %eax")
                    self.emit(f"    movl %eax, {offset}(%rbp)")
                elif is_float_var:
                    # float -> float: store correctly
                    if decl.type_spec.base == "float":
                        self.emit(f"    movq %rax, %xmm0")
                        self.emit(f"    cvtsd2ss %xmm0, %xmm0")
                        self.emit(f"    movss %xmm0, {offset}(%rbp)")
                    else:
                        self.emit(f"    movq %rax, {offset}(%rbp)")
                elif decl.type_spec.base == "_Bool" and not decl.type_spec.is_pointer():
                    # _Bool truncation: any non-zero value becomes 1
                    self.emit(f"    testl %eax, %eax")
                    self.emit(f"    setne %al")
                    self.emit(f"    movb %al, {offset}(%rbp)")
                elif size <= 4 and not decl.type_spec.is_pointer():
                    self.emit(f"    movl %eax, {offset}(%rbp)")
                else:
                    # 64-bit target: if init is a narrower int, extend to 64 bits
                    init_type = self.get_expr_type(decl.init)
                    init_is_narrow = (init_type is not None and not is_float_init and
                                      init_type.base not in ("long", "long long") and
                                      not init_type.is_pointer() and
                                      not init_type.is_array())
                    if init_is_narrow:
                        if init_type.is_unsigned:
                            self.emit("    movl %eax, %eax")  # zero-extend
                        else:
                            self.emit("    cltq")  # sign-extend
                    self.emit(f"    movq %rax, {offset}(%rbp)")

    def _emit_zero_fill(self, offset, size):
        """Emit code to zero-fill a region on the stack."""
        i = 0
        while i + 8 <= size:
            self.emit(f"    movq $0, {offset + i}(%rbp)")
            i += 8
        while i + 4 <= size:
            self.emit(f"    movl $0, {offset + i}(%rbp)")
            i += 4
        while i < size:
            self.emit(f"    movb $0, {offset + i}(%rbp)")
            i += 1

    def _emit_store(self, offset, size, reg="al"):
        """Emit a store of the right size."""
        if size == 1:
            self.emit(f"    movb %al, {offset}(%rbp)")
        elif size == 2:
            self.emit(f"    movw %ax, {offset}(%rbp)")
        elif size <= 4:
            self.emit(f"    movl %eax, {offset}(%rbp)")
        else:
            self.emit(f"    movq %rax, {offset}(%rbp)")

    def _emit_memcpy_stack(self, dst_offset, src_offset, size):
        """Emit code to copy 'size' bytes from src_offset(%rbp) to dst_offset(%rbp)."""
        i = 0
        while i + 8 <= size:
            self.emit(f"    movq {src_offset + i}(%rbp), %rax")
            self.emit(f"    movq %rax, {dst_offset + i}(%rbp)")
            i += 8
        while i + 4 <= size:
            self.emit(f"    movl {src_offset + i}(%rbp), %eax")
            self.emit(f"    movl %eax, {dst_offset + i}(%rbp)")
            i += 4
        while i < size:
            self.emit(f"    movb {src_offset + i}(%rbp), %al")
            self.emit(f"    movb %al, {dst_offset + i}(%rbp)")
            i += 1

    def _emit_memcpy_from_addr(self, dst_offset, size):
        """Emit code to copy 'size' bytes from address in %rax to dst_offset(%rbp).
        Clobbers %rax, %rcx, %rdx."""
        self.emit(f"    movq %rax, %rcx")  # save source address
        i = 0
        while i + 8 <= size:
            self.emit(f"    movq {i}(%rcx), %rax")
            self.emit(f"    movq %rax, {dst_offset + i}(%rbp)")
            i += 8
        while i + 4 <= size:
            self.emit(f"    movl {i}(%rcx), %eax")
            self.emit(f"    movl %eax, {dst_offset + i}(%rbp)")
            i += 4
        while i < size:
            self.emit(f"    movb {i}(%rcx), %al")
            self.emit(f"    movb %al, {dst_offset + i}(%rbp)")
            i += 1

    def gen_struct_init(self, var_name: str, type_spec: TypeSpec, init: 'InitList'):
        """Generate code for struct initialization from { ... }."""
        sdef = type_spec.struct_def
        base_offset = self.locals[var_name][0]
        struct_size = self._get_member_total_size(type_spec)

        # Zero-fill the struct first
        self._emit_zero_fill(base_offset, struct_size)

        # Walk init items with brace elision
        items = init.items
        item_idx = [0]

        self._gen_struct_init_sequential(sdef, base_offset, items, item_idx)

    def _gen_struct_init_sequential(self, sdef, base_offset, items, item_idx):
        """Generate code for struct init, consuming items sequentially with brace elision."""
        members = sdef.members

        def peek():
            return items[item_idx[0]] if item_idx[0] < len(items) else None

        def consume():
            if item_idx[0] < len(items):
                it = items[item_idx[0]]
                item_idx[0] += 1
                return it
            return None

        def compute_anon_offset(sdef_, mem_target):
            """Compute offset of an anonymous member in a struct."""
            off = 0
            for m2 in sdef_.members:
                al = sdef_._member_align(m2.type_spec)
                act_size = self._get_member_total_size(m2.type_spec)
                if al > 0:
                    off = (off + al - 1) & ~(al - 1)
                if m2 is mem_target:
                    return off
                off += act_size
            return 0

        mem_idx = 0
        while mem_idx < len(members) or (item_idx[0] < len(items) and items[item_idx[0]].designator):
            if mem_idx >= len(members):
                # Past end but next item has designator
                it = items[item_idx[0]]
                found = False
                for mi, m in enumerate(members):
                    if m.name == it.designator:
                        mem_idx = mi
                        found = True
                        break
                    if m.name == "" and m.type_spec.struct_def:
                        sub_off = m.type_spec.struct_def.member_offset(it.designator)
                        if sub_off is not None:
                            mem_idx = mi
                            found = True
                            break
                if not found:
                    break

            mem = members[mem_idx]
            mem_ts = mem.type_spec

            # Anonymous struct/union member
            if mem.name == "" and mem_ts.struct_def:
                anon_off = compute_anon_offset(sdef, mem)
                it = peek()
                if it and isinstance(self._unwrap_compound_literal(it.value), InitList) and not it.designator:
                    consume()
                    self._gen_struct_init_sequential(
                        mem_ts.struct_def, base_offset + anon_off,
                        self._unwrap_compound_literal(it.value).items, [0])
                elif it and it.designator:
                    # Check if designator matches a sub-member of this anon struct
                    sub_sdef = mem_ts.struct_def
                    sub_off = sub_sdef.member_offset(it.designator)
                    if sub_off is not None:
                        # Consume and handle the designator within the anon struct
                        consume()
                        sub_ts = sub_sdef.member_type(it.designator)
                        abs_off = base_offset + anon_off + sub_off
                        self._gen_init_value_store(abs_off, sub_ts, it.value)
                        mem_idx += 1
                        continue
                    else:
                        mem_idx += 1
                        continue
                else:
                    # Brace elision: fill sub-members from parent items
                    self._gen_struct_init_sequential(
                        mem_ts.struct_def, base_offset + anon_off, items, item_idx)
                mem_idx += 1
                continue

            mem_off = sdef.member_offset(mem.name) if mem.name else None
            if mem_off is None:
                mem_idx += 1
                continue

            abs_off = base_offset + mem_off
            actual_size = self._get_member_total_size(mem_ts)

            # Empty struct member
            if actual_size == 0:
                it = peek()
                if it and (isinstance(it.value, CastExpr) and isinstance(it.value.operand, InitList)):
                    consume()
                elif it and isinstance(it.value, InitList) and len(it.value.items) == 0:
                    consume()
                mem_idx += 1
                continue

            it = peek()
            if it is None:
                break

            # Designator handling
            if it.designator:
                found = False
                for mi, m in enumerate(members):
                    if m.name == it.designator:
                        mem_idx = mi
                        found = True
                        break
                    if m.name == "" and m.type_spec.struct_def:
                        sub_off = m.type_spec.struct_def.member_offset(it.designator)
                        if sub_off is not None:
                            anon_off = compute_anon_offset(sdef, m)
                            sub_ts = m.type_spec.struct_def.member_type(it.designator)
                            consume()
                            # Handle chained designator path
                            if it.designator_path and len(it.designator_path) > 1:
                                curr_off = base_offset + anon_off + sub_off
                                curr_ts = sub_ts
                                curr_sdef = sub_ts.struct_def if sub_ts else None
                                for dp in it.designator_path[1:]:
                                    if curr_sdef:
                                        so = curr_sdef.member_offset(dp)
                                        if so is not None:
                                            curr_off += so
                                            curr_ts = curr_sdef.member_type(dp)
                                            curr_sdef = curr_ts.struct_def if curr_ts else None
                                self._gen_init_value_store(curr_off, curr_ts, it.value)
                            else:
                                self._gen_init_value_store(base_offset + anon_off + sub_off, sub_ts, it.value)
                            mem_idx = mi + 1
                            found = True
                            break
                if not found:
                    consume()
                    mem_idx += 1
                    continue
                # Re-read member info after potential jump
                mem = members[mem_idx]
                mem_ts = mem.type_spec
                mem_off = sdef.member_offset(mem.name)
                abs_off = base_offset + mem_off
                actual_size = self._get_member_total_size(mem_ts)

                # Chained designator
                if it.designator_path and len(it.designator_path) > 1:
                    consume()
                    curr_off = abs_off
                    curr_ts = mem_ts
                    curr_sdef = mem_ts.struct_def
                    for dp in it.designator_path[1:]:
                        if curr_sdef:
                            sub_off = curr_sdef.member_offset(dp)
                            if sub_off is not None:
                                curr_off += sub_off
                                curr_ts = curr_sdef.member_type(dp)
                                curr_sdef = curr_ts.struct_def if curr_ts else None
                    self._gen_init_value_store(curr_off, curr_ts, it.value)
                    mem_idx += 1
                    continue

            # Consume the item
            consume()

            # Handle compound literal arrays as pointer values
            # e.g., .t = (struct ntd[]){...} where .t is a pointer
            if (isinstance(it.value, CastExpr) and isinstance(it.value.operand, InitList)
                    and it.value.target_type.is_array()):
                # Array compound literal: allocate on stack, store address
                self.gen_expr(it.value)
                self.emit(f"    movq %rax, {abs_off}(%rbp)")
                if sdef.is_union:
                    break
                mem_idx += 1
                continue

            val = self._unwrap_compound_literal(it.value)

            if isinstance(val, InitList):
                if mem_ts.struct_def:
                    self._gen_struct_init_sequential(
                        mem_ts.struct_def, abs_off, val.items, [0])
                elif mem_ts.is_array():
                    self._gen_array_init_from_list(abs_off, mem_ts, val)
                else:
                    # Scalar with braces: unwrap
                    self._gen_init_value_store(abs_off, mem_ts, val)
            elif isinstance(val, StringLiteral) and mem_ts.is_array() and mem_ts.size_bytes() == 1:
                # String literal for char array member
                for ci, ch in enumerate(val.value):
                    self.emit(f"    movb ${ord(ch)}, {abs_off + ci}(%rbp)")
                self.emit(f"    movb $0, {abs_off + len(val.value)}(%rbp)")
            elif mem_ts.struct_def and not mem_ts.is_pointer() and not isinstance(val, InitList):
                # Brace elision or struct copy
                # Check if it's an expression that evaluates to a struct
                is_struct_expr = False
                if isinstance(val, Identifier):
                    loc, vts = self.get_var_location(val.name)
                    if vts and vts.struct_def:
                        if val.name in self.locals or val.name in self.params:
                            src_off = (self.locals.get(val.name) or self.params.get(val.name))[0]
                            self._emit_memcpy_stack(abs_off, src_off, actual_size)
                            is_struct_expr = True
                if not is_struct_expr:
                    # Check if it's a struct-typed expression (e.g., *pls, (ls), w->t.s)
                    expr_type = self.get_expr_type(val)
                    if expr_type and expr_type.struct_def and not expr_type.is_pointer():
                        # Generate address of the struct expression and memcpy
                        # For CastExpr wrapping a struct lvalue, use the operand's address
                        addr_expr = val
                        if isinstance(val, CastExpr):
                            addr_expr = val.operand
                        try:
                            self.gen_lvalue_addr(addr_expr)
                            # rax now has address of source struct
                            self._emit_memcpy_from_addr(abs_off, actual_size)
                            is_struct_expr = True
                        except Exception:
                            pass  # Fall through to brace elision
                if is_struct_expr:
                    if sdef.is_union:
                        break
                    mem_idx += 1
                    continue
                # Brace elision: put item back and fill sub-struct
                item_idx[0] -= 1
                self._gen_struct_init_sequential(
                    mem_ts.struct_def, abs_off, items, item_idx)
            elif mem_ts.is_array() and not isinstance(val, InitList):
                # Brace elision for array: put back and consume scalars
                elem_sz = mem_ts.size_bytes()
                item_idx[0] -= 1
                arr_count = 1
                if mem_ts.array_sizes and mem_ts.array_sizes[0]:
                    first = mem_ts.array_sizes[0]
                    if isinstance(first, IntLiteral):
                        arr_count = first.value
                for ai in range(arr_count):
                    ait = peek()
                    if ait is None or ait.designator:
                        break
                    consume()
                    self.gen_expr(ait.value)
                    off = abs_off + ai * elem_sz
                    if elem_sz == 1:
                        self.emit(f"    movb %al, {off}(%rbp)")
                    elif elem_sz == 8:
                        self.emit(f"    movq %rax, {off}(%rbp)")
                    else:
                        self.emit(f"    movl %eax, {off}(%rbp)")
            else:
                self._gen_init_value_store(abs_off, mem_ts, val)

            if sdef.is_union:
                break

            mem_idx += 1

    def _gen_init_value_store(self, offset, mem_ts, value):
        """Generate code to store an init value at a given stack offset."""
        value = self._unwrap_compound_literal(value)

        # Unwrap braces around scalar
        unwrapped = value
        while isinstance(unwrapped, InitList) and unwrapped.items:
            unwrapped = unwrapped.items[0].value
        unwrapped = self._unwrap_compound_literal(unwrapped)

        mem_size = mem_ts.size_bytes() if mem_ts else 4

        if isinstance(unwrapped, StringLiteral) and mem_ts and mem_ts.is_array() and mem_size == 1:
            # String literal for char array
            for ci, ch in enumerate(unwrapped.value):
                self.emit(f"    movb ${ord(ch)}, {offset + ci}(%rbp)")
            self.emit(f"    movb $0, {offset + len(unwrapped.value)}(%rbp)")
            return

        self.gen_expr(unwrapped)
        # Float/double member: handle int-to-float conversions
        if mem_ts and mem_ts.base in ("float", "double") and not mem_ts.is_pointer():
            if isinstance(unwrapped, IntLiteral) or (isinstance(unwrapped, UnaryOp) and unwrapped.op == "-"):
                # Integer value needs conversion to float/double
                self.emit("    cvtsi2sd %eax, %xmm0")
                if mem_ts.base == "float":
                    self.emit("    cvtsd2ss %xmm0, %xmm0")
                    self.emit(f"    movss %xmm0, {offset}(%rbp)")
                else:
                    self.emit(f"    movsd %xmm0, {offset}(%rbp)")
                return
            elif isinstance(unwrapped, FloatLiteral) and mem_ts.base == "float":
                # Double literal to float member
                self.emit("    movq %rax, %xmm0")
                self.emit("    cvtsd2ss %xmm0, %xmm0")
                self.emit(f"    movss %xmm0, {offset}(%rbp)")
                return
        if mem_ts and (mem_ts.is_pointer() or mem_size == 8):
            self.emit(f"    movq %rax, {offset}(%rbp)")
        elif mem_ts and mem_size == 1:
            self.emit(f"    movb %al, {offset}(%rbp)")
        elif mem_ts and mem_size == 2:
            self.emit(f"    movw %ax, {offset}(%rbp)")
        else:
            self.emit(f"    movl %eax, {offset}(%rbp)")

    def _gen_array_init_from_list(self, base_offset, arr_ts, init_list):
        """Generate code for array init from an InitList at a given stack offset."""
        elem_size = arr_ts.size_bytes()
        arr_count = 1
        if arr_ts.array_sizes and arr_ts.array_sizes[0]:
            first = arr_ts.array_sizes[0]
            if isinstance(first, IntLiteral):
                arr_count = first.value

        idx = 0
        for item in init_list.items:
            if item.designator_index is not None:
                idx = item.designator_index
            end_idx = idx
            if item.designator_end is not None:
                end_idx = item.designator_end
            for j in range(idx, end_idx + 1):
                if j < arr_count:
                    self.gen_expr(item.value)
                    off = base_offset + j * elem_size
                    if elem_size == 1:
                        self.emit(f"    movb %al, {off}(%rbp)")
                    elif elem_size == 8:
                        self.emit(f"    movq %rax, {off}(%rbp)")
                    else:
                        self.emit(f"    movl %eax, {off}(%rbp)")
            idx = end_idx + 1

    def gen_array_init(self, var_name: str, type_spec: TypeSpec, init: 'InitList', override_offset=None):
        """Generate code for array initialization from { ... }."""
        base_offset = override_offset if override_offset is not None else self.locals[var_name][0]
        elem_size = type_spec.size_bytes()
        # Zero-fill first
        total_size = self._get_member_total_size(type_spec)
        self._emit_zero_fill(base_offset, total_size)

        # Handle struct array or plain array
        if type_spec.struct_def:
            # Array of structs
            sdef = type_spec.struct_def
            struct_size = sdef.size_bytes()
            idx = 0
            for item in init.items:
                if item.designator_index is not None:
                    idx = item.designator_index
                val = self._unwrap_compound_literal(item.value)
                if isinstance(val, InitList):
                    self._gen_struct_init_sequential(
                        sdef, base_offset + idx * struct_size, val.items, [0])
                else:
                    # Single value wrapping
                    self._gen_struct_init_sequential(
                        sdef, base_offset + idx * struct_size,
                        [InitItem(value=item.value)], [0])
                idx += 1
        else:
            # Compute inner dimension count for multi-dim arrays
            inner_count = 1
            if type_spec.array_sizes and len(type_spec.array_sizes) > 1:
                for dim in type_spec.array_sizes[1:]:
                    dv = self._dim_value(dim) if dim else 1
                    if dv:
                        inner_count *= dv

            idx = 0
            for item in init.items:
                if item.designator_index is not None:
                    idx = item.designator_index
                val = item.value
                # Unwrap CastExpr
                while isinstance(val, CastExpr):
                    val = val.operand
                if isinstance(val, InitList) and inner_count >= 1:
                    # Inner init list for multi-dim array row
                    row_base = base_offset + idx * inner_count * elem_size
                    is_float_arr = type_spec.base in ("float", "double") and not type_spec.is_pointer()
                    for k, sub_item in enumerate(val.items):
                        self.gen_expr(sub_item.value)
                        offset = row_base + k * elem_size
                        needs_int2flt = isinstance(sub_item.value, IntLiteral) or (
                            isinstance(sub_item.value, UnaryOp) and not isinstance(sub_item.value.operand, FloatLiteral) and not self._is_float_type(sub_item.value.operand))
                        if is_float_arr and needs_int2flt:
                            self.emit("    cvtsi2sd %eax, %xmm0")
                            if type_spec.base == "float":
                                self.emit("    cvtsd2ss %xmm0, %xmm0")
                                self.emit(f"    movss %xmm0, {offset}(%rbp)")
                            else:
                                self.emit(f"    movsd %xmm0, {offset}(%rbp)")
                        elif elem_size == 1:
                            self.emit(f"    movb %al, {offset}(%rbp)")
                        elif elem_size == 8:
                            self.emit(f"    movq %rax, {offset}(%rbp)")
                        else:
                            self.emit(f"    movl %eax, {offset}(%rbp)")
                elif isinstance(val, StringLiteral) and inner_count > 1:
                    # String literal for char row
                    row_base = base_offset + idx * inner_count * elem_size
                    for k, ch in enumerate(val.value):
                        self.emit(f"    movb ${ord(ch)}, {row_base + k}(%rbp)")
                    self.emit(f"    movb $0, {row_base + len(val.value)}(%rbp)")
                else:
                    end_idx = idx
                    if item.designator_end is not None:
                        end_idx = item.designator_end
                    is_float_arr = type_spec.base in ("float", "double") and not type_spec.is_pointer()
                    for j in range(idx, end_idx + 1):
                        self.gen_expr(val)
                        offset = base_offset + j * elem_size
                        needs_int2flt = isinstance(val, IntLiteral) or (
                            isinstance(val, UnaryOp) and not isinstance(val.operand, FloatLiteral) and not self._is_float_type(val.operand))
                        if is_float_arr and needs_int2flt:
                            # Convert integer to float/double for float array init
                            self.emit("    cvtsi2sd %eax, %xmm0")
                            if type_spec.base == "float":
                                self.emit("    cvtsd2ss %xmm0, %xmm0")
                                self.emit(f"    movss %xmm0, {offset}(%rbp)")
                            else:
                                self.emit(f"    movsd %xmm0, {offset}(%rbp)")
                        elif elem_size == 1:
                            self.emit(f"    movb %al, {offset}(%rbp)")
                        elif elem_size == 8:
                            self.emit(f"    movq %rax, {offset}(%rbp)")
                        elif elem_size == 2:
                            self.emit(f"    movw %ax, {offset}(%rbp)")
                        else:
                            self.emit(f"    movl %eax, {offset}(%rbp)")
                idx += 1

    def gen_if(self, stmt: IfStmt):
        else_label = self.new_label("else")
        end_label = self.new_label("endif")

        self.gen_expr(stmt.condition)
        self._emit_cond_test(stmt.condition)

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
        self._emit_cond_test(stmt.condition)
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
        self._emit_cond_test(stmt.condition)
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
            self._emit_cond_test(stmt.condition)
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

        def collect_cases(node):
            """Recursively find all CaseStmt nodes in the switch body."""
            nonlocal default_label
            if isinstance(node, CaseStmt):
                lbl = self.new_label("case")
                if node.is_default:
                    default_label = lbl
                else:
                    cases.append((node, lbl))
                node._label = lbl
                if node.stmt:
                    collect_cases(node.stmt)
            elif isinstance(node, Block):
                for s in node.stmts:
                    collect_cases(s)
            elif isinstance(node, DoWhileStmt):
                if node.body:
                    collect_cases(node.body)
            elif isinstance(node, WhileStmt):
                if node.body:
                    collect_cases(node.body)
            elif isinstance(node, ForStmt):
                if node.body:
                    collect_cases(node.body)
            elif isinstance(node, IfStmt):
                if node.then_body:
                    collect_cases(node.then_body)
                if node.else_body:
                    collect_cases(node.else_body)
            elif isinstance(node, LabelStmt):
                if node.stmt:
                    collect_cases(node.stmt)

        collect_cases(stmt.body)

        # Generate comparison jumps
        for case_stmt, lbl in cases:
            cv = self._try_eval_const(case_stmt.value)
            if cv is not None:
                self.emit(f"    cmpl ${cv}, %r10d")
                self.emit(f"    je {lbl}")

        if default_label:
            self.emit(f"    jmp {default_label}")
        else:
            self.emit(f"    jmp {end_label}")

        # Generate switch body (case labels emitted by gen_stmt(CaseStmt))
        self.gen_stmt(stmt.body)

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
            self.string_literals.append((lbl, expr.value, expr.wide))
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

        elif isinstance(expr, BuiltinVaArg):
            self._gen_builtin_va_arg(expr)

        elif isinstance(expr, ArrayAccess):
            self.gen_array_access(expr)

        elif isinstance(expr, MemberAccess):
            self.gen_member_access(expr)

        elif isinstance(expr, TernaryOp):
            self.gen_ternary(expr)

        elif isinstance(expr, CastExpr) and isinstance(expr.operand, InitList):
            # Compound literal: (type){init} — allocate on stack, return address
            self.gen_lvalue_addr(expr)

        elif isinstance(expr, CastExpr):
            self.gen_expr(expr.operand)
            src_type = self.get_expr_type(expr.operand)
            dst_type = expr.target_type
            if dst_type and src_type:
                src_is_ptr = src_type.is_pointer() or src_type.is_array()
                dst_is_ptr = dst_type.is_pointer() or dst_type.is_array()
                # Pointer-to-pointer casts are no-ops
                if src_is_ptr and dst_is_ptr:
                    pass
                else:
                    src_size = 8 if src_is_ptr else src_type.size_bytes()
                    dst_size = 8 if dst_is_ptr else dst_type.size_bytes()
                    src_is_float = src_type.base in ("float", "double", "long double") and not src_type.is_pointer()
                    dst_is_float = dst_type.base in ("float", "double", "long double") and not dst_type.is_pointer()
                    if src_is_float and not dst_is_float:
                        # float/double -> int
                        self.emit("    movq %rax, %xmm0")
                        self.emit("    cvttsd2si %xmm0, %rax")
                    elif not src_is_float and dst_is_float:
                        # int -> float/double
                        if src_size <= 4:
                            self.emit("    cvtsi2sd %eax, %xmm0")  # 32-bit signed int
                        else:
                            self.emit("    cvtsi2sd %rax, %xmm0")  # 64-bit long
                        self.emit("    movq %xmm0, %rax")
                    elif not src_is_float and not dst_is_float:
                        # int -> int: handle widening/narrowing
                        if dst_size > src_size:
                            # Widening cast
                            if src_size <= 4 and dst_size == 8:
                                if src_type.is_unsigned:
                                    # Zero-extend: movl %eax, %eax clears upper 32 bits
                                    self.emit("    movl %eax, %eax")
                                else:
                                    # Sign-extend 32-bit to 64-bit
                                    self.emit("    movslq %eax, %rax")
                            elif src_size == 1 and dst_size >= 2:
                                if src_type.is_unsigned:
                                    self.emit("    movzbl %al, %eax")
                                else:
                                    self.emit("    movsbl %al, %eax")
                                if dst_size == 8 and not src_type.is_unsigned:
                                    self.emit("    movslq %eax, %rax")
                            elif src_size == 2 and dst_size >= 4:
                                if src_type.is_unsigned:
                                    self.emit("    movzwl %ax, %eax")
                                else:
                                    self.emit("    movswl %ax, %eax")
                                if dst_size == 8 and not src_type.is_unsigned:
                                    self.emit("    movslq %eax, %rax")
                        elif dst_size == src_size and dst_size < 4:
                            # Same size but different signedness (e.g., char -> unsigned char)
                            if dst_size == 1:
                                if dst_type.is_unsigned:
                                    self.emit("    movzbl %al, %eax")
                                else:
                                    self.emit("    movsbl %al, %eax")
                            elif dst_size == 2:
                                if dst_type.is_unsigned:
                                    self.emit("    movzwl %ax, %eax")
                                else:
                                    self.emit("    movswl %ax, %eax")
                        elif dst_size < src_size:
                            # Narrowing cast — must sign/zero-extend the truncated value
                            # so it matches what a load of that size would produce
                            if dst_size == 1:
                                if dst_type.is_unsigned:
                                    self.emit("    movzbl %al, %eax")
                                else:
                                    self.emit("    movsbl %al, %eax")
                            elif dst_size == 2:
                                if dst_type.is_unsigned:
                                    self.emit("    movzwl %ax, %eax")
                                else:
                                    self.emit("    movswl %ax, %eax")

        elif isinstance(expr, SizeofExpr):
            if expr.is_type:
                ts = expr.operand
                size = ts.size_bytes()
                if ts.struct_def and not ts.is_pointer():
                    size = ts.struct_def.size_bytes()
                # Warn if sizeof on incomplete or unknown struct/union type
                if not ts.is_pointer():
                    if (ts.base.startswith("struct ") or ts.base.startswith("union ")) and not ts.struct_def:
                        import sys
                        print(f"warning: sizeof applied to unknown type '{ts.base}' "
                              f"(defaulting to {size})", file=sys.stderr)
                    elif ts.struct_def and not ts.struct_def.members:
                        import sys
                        print(f"warning: sizeof applied to incomplete type '{ts.base}' "
                              f"(no members defined, size is 0)", file=sys.stderr)
                if (ts.is_array() or ts.is_ptr_array) and ts.array_sizes:
                    for dim in ts.array_sizes:
                        dv = self._dim_value(dim)
                        if dv is not None:
                            size *= dv
            else:
                # sizeof on an expression — check for VLA first
                if isinstance(expr.operand, Identifier) and expr.operand.name in self.vla_sizes:
                    off = self.vla_sizes[expr.operand.name]
                    self.emit(f"    movq {off}(%rbp), %rax")
                    return
                # sizeof(compound_literal) — e.g., sizeof((struct ntd[]){...})
                if isinstance(expr.operand, CastExpr) and isinstance(expr.operand.operand, InitList):
                    cl_type = expr.operand.target_type
                    if cl_type.is_array():
                        elem_size = cl_type.size_bytes()
                        if cl_type.struct_def:
                            elem_size = cl_type.struct_def.size_bytes()
                        n_items = len(expr.operand.operand.items)
                        size = elem_size * n_items
                    elif cl_type.struct_def:
                        size = cl_type.struct_def.size_bytes()
                    else:
                        size = cl_type.size_bytes()
                    self.emit(f"    movl ${size}, %eax")
                    return
                # sizeof on an expression — infer type
                et = self.get_expr_type(expr.operand)
                if et:
                    size = et.size_bytes()
                    if et.struct_def and not et.is_pointer():
                        size = et.struct_def.size_bytes()
                    if (et.is_array() or et.is_ptr_array) and et.array_sizes:
                        for dim in et.array_sizes:
                            dv = self._dim_value(dim)
                            if dv is not None:
                                size *= dv
                else:
                    size = 4
            self.emit(f"    movl ${size}, %eax")

        elif isinstance(expr, GenericSelection):
            ct = self.get_expr_type(expr.controlling)
            selected = None
            default_expr = None
            for assoc in expr.associations:
                if assoc.type_spec is None:
                    default_expr = assoc.expr
                elif ct and self._generic_types_match(ct, assoc.type_spec):
                    selected = assoc.expr
                    break
            if selected is None:
                selected = default_expr
            if selected is not None:
                self.gen_expr(selected)
            else:
                self.emit("    movl $0, %eax")

        elif isinstance(expr, CommaExpr):
            # Evaluate all expressions, result is the last one
            for sub in expr.exprs:
                self.gen_expr(sub)

        elif isinstance(expr, StatementExpr):
            saved_locals = dict(self.locals)
            for stmt in expr.body.stmts:
                self.gen_stmt(stmt)
            # Last ExprStmt's value is already in %rax
            self.locals = saved_locals

        elif isinstance(expr, CommaExpr):
            for e in expr.exprs:
                self.gen_expr(e)

        elif isinstance(expr, InitList):
            # Compound literal in expression: (type){val, ...}
            # For simple cases, evaluate the first item
            if expr.items:
                self.gen_expr(expr.items[0].value)

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

        if ts and (ts.is_array() or ts.is_ptr_array):
            # Array: load address (array-to-pointer decay)
            if name in self.locals or name in self.params:
                offset = self.locals.get(name, self.params.get(name, (0, None)))[0]
                self.emit(f"    leaq {offset}(%rbp), %rax")
            elif name in self.static_locals:
                mangled = self.static_locals[name]
                self.emit(f"    leaq {mangled}(%rip), %rax")
            else:
                self.emit(f"    leaq {name}(%rip), %rax")
        elif ts and ts.base == "float" and not ts.is_pointer() and ts.pointer_depth == 0:
            # Load 4-byte float, convert to double, store in %rax
            self.emit(f"    movss {loc}, %xmm0")
            self.emit("    cvtss2sd %xmm0, %xmm0")
            self.emit("    movq %xmm0, %rax")
        elif ts and (ts.is_pointer() or ts.size_bytes() == 8 or
                     ts.base in ("double", "long double")):
            self.emit(f"    movq {loc}, %rax")
        elif ts and ts.size_bytes() == 2:
            if ts.is_unsigned:
                self.emit(f"    movzwl {loc}, %eax")
            else:
                self.emit(f"    movswl {loc}, %eax")
        elif ts and ts.size_bytes() == 1:
            if ts.is_unsigned:
                self.emit(f"    movzbl {loc}, %eax")
            else:
                self.emit(f"    movsbl {loc}, %eax")
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
        elif isinstance(expr, CastExpr) and isinstance(expr.operand, InitList):
            # Compound literal: (Type){init} — allocate on stack and return address
            ts = expr.target_type
            size = ts.size_bytes()
            if ts.struct_def:
                size = ts.struct_def.size_bytes()
            if ts.is_array() and ts.array_sizes:
                # Array compound literal: (int[]){1, 2, 3}
                elem_size = size
                n_items = len(expr.operand.items)
                arr_count = n_items
                for dim in ts.array_sizes:
                    if dim and isinstance(dim, IntLiteral):
                        arr_count = dim.value
                total = elem_size * arr_count
                alloc = (total + 7) & ~7
                self.stack_offset -= alloc
                temp_off = self.stack_offset
                self._emit_zero_fill(temp_off, total)
                self.gen_array_init("__compound_arr__", ts, expr.operand,
                                    override_offset=temp_off)
                self.emit(f"    leaq {temp_off}(%rbp), %rax")
            else:
                alloc = (size + 7) & ~7
                self.stack_offset -= alloc
                temp_off = self.stack_offset
                self._emit_zero_fill(temp_off, size)
                if ts.struct_def:
                    self._gen_struct_init_sequential(
                        ts.struct_def, temp_off, expr.operand.items, [0])
                self.emit(f"    leaq {temp_off}(%rbp), %rax")
        elif isinstance(expr, FuncCall):
            # Function call returning struct: call the function, store result
            # to a temp on the stack, and return the temp's address.
            ret_type = self.get_expr_type(expr)
            struct_size = ret_type.struct_def.size_bytes() if ret_type and ret_type.struct_def else 16
            alloc = (struct_size + 7) & ~7
            self.stack_offset -= alloc
            temp_off = self.stack_offset
            self.gen_expr(expr)
            # Small structs are returned in %rax/%rdx
            self.emit(f"    movq %rax, {temp_off}(%rbp)")
            if struct_size > 8:
                self.emit(f"    movq %rdx, {temp_off + 8}(%rbp)")
            self.emit(f"    leaq {temp_off}(%rbp), %rax")
        elif isinstance(expr, InitList):
            # Bare compound literal (type was parsed separately or omitted)
            # Infer struct type from context if available, or use pointer size per member
            n_items = len(expr.items)
            alloc = ((n_items * 8) + 7) & ~7
            self.stack_offset -= alloc
            temp_off = self.stack_offset
            self._emit_zero_fill(temp_off, n_items * 8)
            for i, item in enumerate(expr.items):
                self.gen_expr(item.value)
                self.emit(f"    movq %rax, {temp_off + i * 8}(%rbp)")
            self.emit(f"    leaq {temp_off}(%rbp), %rax")
        elif isinstance(expr, Assignment):
            # Chained assignment: a = (b = expr)
            # Execute the inner assignment, then return target's address
            self.gen_assignment(expr)
            self.gen_lvalue_addr(expr.target)
        elif isinstance(expr, TernaryOp):
            # Ternary returning a struct: allocate temp, evaluate selected branch
            # into temp via memcpy, return temp's address
            tt = self.get_expr_type(expr)
            if tt and tt.struct_def and not tt.is_pointer():
                size = tt.struct_def.size_bytes()
                alloc = (size + 7) & ~7
                self.stack_offset -= alloc
                temp_off = self.stack_offset
                false_label = self.new_label("tern_lv_f")
                end_label = self.new_label("tern_lv_e")
                self.gen_expr(expr.condition)
                self._emit_cond_test(expr.condition)
                self.emit(f"    je {false_label}")
                self.gen_lvalue_addr(expr.true_expr)
                self.emit("    movq %rax, %rsi")
                self.emit(f"    leaq {temp_off}(%rbp), %rdi")
                self.emit(f"    movl ${size}, %ecx")
                self.emit("    rep movsb")
                self.emit(f"    jmp {end_label}")
                self.label(false_label)
                self.gen_lvalue_addr(expr.false_expr)
                self.emit("    movq %rax, %rsi")
                self.emit(f"    leaq {temp_off}(%rbp), %rdi")
                self.emit(f"    movl ${size}, %ecx")
                self.emit("    rep movsb")
                self.label(end_label)
                self.emit(f"    leaq {temp_off}(%rbp), %rax")
            else:
                self.error("expression is not an lvalue", expr.line, expr.col)
        else:
            self.error("expression is not an lvalue", expr.line, expr.col)

    def gen_array_addr(self, expr: ArrayAccess):
        """Generate address of array element into %rax."""
        # Get array base address
        if isinstance(expr.array, Identifier):
            loc, ts = self.get_var_location(expr.array.name)
            is_real_array = ts and (ts.is_array() or (ts.is_ptr_array))
            if is_real_array:
                # Array: base address
                if expr.array.name in self.locals or expr.array.name in self.params:
                    offset = (self.locals.get(expr.array.name) or self.params.get(expr.array.name))[0]
                    self.emit(f"    leaq {offset}(%rbp), %rax")
                elif expr.array.name in self.static_locals:
                    mangled = self.static_locals[expr.array.name]
                    self.emit(f"    leaq {mangled}(%rip), %rax")
                else:
                    self.emit(f"    leaq {expr.array.name}(%rip), %rax")
            else:
                # Pointer: load pointer value
                self.gen_expr(expr.array)
        elif isinstance(expr.array, ArrayAccess):
            # Nested array access (multi-dim): get address, don't dereference
            # EXCEPT for ptr_array where the intermediate result is a pointer value
            self.gen_array_addr(expr.array)
            # Check if the intermediate result is a pointer that needs dereferencing
            # (ptr_array intermediate results are sub-arrays, not pointer values)
            inner_type = self.get_expr_type(expr.array)
            if inner_type and inner_type.is_pointer() and not inner_type.is_array() and not inner_type.is_ptr_array:
                self.emit("    movq (%rax), %rax")  # dereference pointer
        elif isinstance(expr.array, MemberAccess):
            # Member access as array base: check if it's an array member
            arr_type = self.get_expr_type(expr.array)
            if arr_type and (arr_type.is_array() or arr_type.is_ptr_array):
                # Array member: use address, not value
                self.gen_member_addr(expr.array)
            elif arr_type and arr_type.is_pointer() and arr_type.array_sizes:
                # Pointer-to-array member: load the pointer value (it's a pointer, not an array)
                self.gen_expr(expr.array)
            else:
                # Pointer member: load the pointer value
                self.gen_expr(expr.array)
        else:
            self.gen_expr(expr.array)

        self.emit("    pushq %rax")

        # Generate index
        self.gen_expr(expr.index)
        self.emit("    movslq %eax, %rax")

        # Element size (default to 4 for int, 8 for pointer, 1 for char)
        elem_size = 4  # default
        if isinstance(expr.array, ArrayAccess):
            # Nested array access or member access — get element size from type
            root = expr.array
            depth = 1
            while isinstance(root, ArrayAccess):
                root = root.array
                depth += 1
            ts = None
            if isinstance(root, Identifier):
                _, ts = self.get_var_location(root.name)
            elif isinstance(root, MemberAccess):
                ts = self.get_expr_type(root)
            if ts and ts.is_ptr_array and ts.array_sizes:
                num_dims = len(ts.array_sizes)
                if depth <= num_dims:
                    # Still within the pointer array dimensions
                    elem_size = 8
                    if num_dims > depth:
                        for dim in ts.array_sizes[depth:]:
                            dv = self._dim_value(dim)
                            if dv is not None:
                                elem_size *= dv
                else:
                    # Past array dims — indexing into pointed-to type
                    elem_size = TypeSpec(base=ts.base).size_bytes()
            elif ts and ts.is_array() and ts.array_sizes and len(ts.array_sizes) > depth:
                # Element size is product of remaining dimensions * base size
                elem_size = ts.size_bytes()
                if ts.struct_def:
                    elem_size = ts.struct_def.size_bytes()
                for dim in ts.array_sizes[depth:]:
                    if isinstance(dim, IntLiteral):
                        elem_size *= dim.value
            elif ts and ts.is_array() and ts.array_sizes and len(ts.array_sizes) == depth:
                # Innermost dimension — element is the base type
                elem_size = ts.size_bytes()
                if ts.struct_def:
                    elem_size = ts.struct_def.size_bytes()
            elif ts and ts.is_pointer() and ts.array_sizes:
                # Pointer-to-array: inner element is the base type
                elem_size = TypeSpec(base=ts.base).size_bytes()
            elif ts:
                # For double pointers (e.g., short**), inner access uses base type size
                if ts.is_pointer() and ts.pointer_depth > 1 and depth >= ts.pointer_depth:
                    elem_size = TypeSpec(base=ts.base, is_unsigned=ts.is_unsigned).size_bytes()
                else:
                    elem_size = ts.size_bytes()
        elif isinstance(expr.array, Identifier):
            _, ts = self.get_var_location(expr.array.name)
            if ts:
                if ts.is_array() and ts.struct_def:
                    # Array of structs
                    elem_size = ts.struct_def.size_bytes()
                    # Multi-dim struct array: outer stride includes inner dimensions
                    if ts.array_sizes and len(ts.array_sizes) > 1:
                        for dim in ts.array_sizes[1:]:
                            dv = self._dim_value(dim)
                            if dv is not None:
                                elem_size *= dv
                elif ts.is_array():
                    elem_ts = TypeSpec(base=ts.base, pointer_depth=ts.pointer_depth,
                                       is_unsigned=ts.is_unsigned)
                    elem_size = elem_ts.size_bytes()
                    # Multi-dim array: element size includes inner dimensions
                    if ts.array_sizes and len(ts.array_sizes) > 1:
                        for dim in ts.array_sizes[1:]:
                            dv = self._dim_value(dim)
                            if dv is not None:
                                elem_size *= dv
                elif ts.is_ptr_array:
                    # Array of pointers (e.g., void (*table[3])(void))
                    elem_size = 8  # pointer size
                    # Multi-dim pointer array: outer stride includes inner dimensions
                    if ts.array_sizes and len(ts.array_sizes) > 1:
                        for dim in ts.array_sizes[1:]:
                            dv = self._dim_value(dim)
                            if dv is not None:
                                elem_size *= dv
                else:
                    if ts.is_pointer() and ts.struct_def and ts.pointer_depth == 1:
                        # Pointer to struct: element size is the struct size
                        elem_size = ts.struct_def.size_bytes()
                    else:
                        elem_ts = TypeSpec(base=ts.base, pointer_depth=max(ts.pointer_depth - 1, 0),
                                           is_unsigned=ts.is_unsigned, struct_def=ts.struct_def)
                        elem_size = elem_ts.size_bytes()
                    # Pointer to array: (*p)[N] — element stride includes array size
                    vla_stride_dims = []
                    if ts.is_pointer() and ts.array_sizes:
                        for dim in ts.array_sizes:
                            dv = self._dim_value(dim)
                            if dv is not None:
                                elem_size *= dv
                            elif dim is not None:
                                vla_stride_dims.append(dim)

        # Fallback: use get_expr_type for element size
        if elem_size == 4 and not isinstance(expr.array, Identifier):
            arr_type = self.get_expr_type(expr.array)
            if arr_type and arr_type.is_array():
                elem_size = arr_type.size_bytes()
                # Multi-dim: stride includes inner dimensions
                if arr_type.array_sizes and len(arr_type.array_sizes) > 1:
                    for dim in arr_type.array_sizes[1:]:
                        if isinstance(dim, IntLiteral):
                            elem_size *= dim.value
            elif arr_type and arr_type.is_ptr_array:
                elem_size = 8  # pointer array: element is a pointer
            elif arr_type and arr_type.is_pointer() and arr_type.pointer_depth >= 2:
                elem_size = 8  # double pointer: element is pointer
            elif arr_type and arr_type.is_pointer() and arr_type.array_sizes:
                # Pointer-to-array: element stride includes array dimensions
                pointed = TypeSpec(base=arr_type.base, pointer_depth=arr_type.pointer_depth - 1,
                                   struct_def=arr_type.struct_def)
                elem_size = pointed.size_bytes()
                for dim in arr_type.array_sizes:
                    dv = self._dim_value(dim)
                    if dv is not None:
                        elem_size *= dv
            elif arr_type and arr_type.is_pointer():
                pointed = TypeSpec(base=arr_type.base, pointer_depth=arr_type.pointer_depth - 1,
                                   struct_def=arr_type.struct_def)
                elem_size = pointed.size_bytes()

        if elem_size != 1:
            self.emit(f"    imulq ${elem_size}, %rax")
        # Runtime VLA stride multiply (for pointer-to-VLA like (*p)[runtime_dim])
        if 'vla_stride_dims' in dir() and vla_stride_dims:
            for dim_expr in vla_stride_dims:
                self.emit("    pushq %rax")
                self.gen_expr(dim_expr)
                self.emit("    movslq %eax, %rcx")
                self.emit("    popq %rax")
                self.emit("    imulq %rcx, %rax")

        self.emit("    popq %rcx")
        self.emit("    addq %rcx, %rax")

    def gen_array_access(self, expr: ArrayAccess):
        """Generate array access (load value)."""
        self.gen_array_addr(expr)

        # Determine element size for load (based on pointed-to/element type)
        elem_size = 4
        if isinstance(expr.array, ArrayAccess):
            # Nested array access — find root type for base element size
            root = expr.array
            depth = 1
            while isinstance(root, ArrayAccess):
                root = root.array
                depth += 1
            if isinstance(root, Identifier):
                _, ts = self.get_var_location(root.name)
                if ts and ts.is_ptr_array:
                    # Pointer array: depth 1 = pointer element (8 bytes)
                    # depth 2+ = dereferenced pointer element (base type)
                    num_dims = len(ts.array_sizes) if ts.array_sizes else 1
                    if depth <= num_dims:
                        elem_size = 8  # still indexing within the pointer array
                    else:
                        # Past the array dimensions — indexing the pointed-to type
                        elem_size = TypeSpec(base=ts.base).size_bytes()
                elif ts:
                    # For nested access, the base element type matters
                    base = ts.base
                    if base in ("char", "_Bool"):
                        elem_size = 1
                    elif base == "short":
                        elem_size = 2
                    elif base in ("long", "long long", "double"):
                        elem_size = 8
                    elif ts.struct_def:
                        elem_size = ts.struct_def.size_bytes()
                    elif ts.is_pointer() and not ts.array_sizes:
                        # Pure pointer (not ptr-to-array): element is pointer
                        elem_size = 8
        elif isinstance(expr.array, Identifier):
            _, ts = self.get_var_location(expr.array.name)
            if ts:
                # For pointer or array, element type is one level of indirection less
                if ts.is_ptr_array:
                    # Array of pointers: element is a pointer (8 bytes)
                    elem_size = 8
                elif ts.is_pointer() and ts.pointer_depth == 1:
                    # Pointer to base type: element is the base type
                    if ts.base in ("char", "_Bool"):
                        elem_size = 1
                    elif ts.base == "short":
                        elem_size = 2
                    elif ts.base in ("long", "long long", "double") or ts.struct_def:
                        elem_size = 8
                    elif ts.base == "long double":
                        elem_size = 16
                    else:
                        elem_size = 4
                elif ts.is_pointer() and ts.pointer_depth > 1:
                    # Pointer to pointer: element is a pointer (8 bytes)
                    elem_size = 8
                elif ts.is_array():
                    if ts.pointer_depth > 0:
                        elem_size = 8
                    elif ts.base in ("char", "_Bool"):
                        elem_size = 1
                    elif ts.base == "short":
                        elem_size = 2
                    elif ts.struct_def:
                        elem_size = ts.struct_def.size_bytes()
                    elif ts.base in ("long", "long long", "double"):
                        elem_size = 8
                    elif ts.base == "float":
                        elem_size = 4
                    elif ts.base == "long double":
                        elem_size = 16
                    else:
                        elem_size = 4

        # Fallback: use get_expr_type for proper element size
        if elem_size == 4 and not isinstance(expr.array, (Identifier, ArrayAccess)):
            arr_type = self.get_expr_type(expr.array)
            if arr_type:
                if arr_type.is_ptr_array:
                    elem_size = 8  # pointer array: element is pointer
                elif arr_type.is_pointer() and arr_type.pointer_depth >= 2:
                    elem_size = 8  # double pointer: element is pointer
                elif arr_type.is_pointer():
                    # Single pointer: element is the pointed-to type
                    pointed = TypeSpec(base=arr_type.base, pointer_depth=0,
                                       struct_def=arr_type.struct_def,
                                       is_unsigned=arr_type.is_unsigned)
                    elem_size = pointed.size_bytes()
                elif arr_type.is_array():
                    elem_size = arr_type.size_bytes()

        # Check if result is an array (sub-array of multi-dim) — return address, don't load
        expr_type = self.get_expr_type(expr)
        if expr_type and (expr_type.is_array() or (expr_type.array_sizes and len(expr_type.array_sizes) > 0)):
            return  # address already in %rax — array decay

        # Determine signedness for 1/2-byte loads
        is_unsigned = False
        if expr_type:
            is_unsigned = expr_type.is_unsigned

        # Check for float element type — need special SSE load
        if expr_type and expr_type.base == "float" and not expr_type.is_pointer() and elem_size == 4:
            self.emit("    movss (%rax), %xmm0")
            self.emit("    cvtss2sd %xmm0, %xmm0")
            self.emit("    movq %xmm0, %rax")
            return

        if elem_size == 1:
            if is_unsigned:
                self.emit("    movzbl (%rax), %eax")
            else:
                self.emit("    movsbl (%rax), %eax")
        elif elem_size == 2:
            if is_unsigned:
                self.emit("    movzwl (%rax), %eax")
            else:
                self.emit("    movswl (%rax), %eax")
        elif elem_size == 8:
            self.emit("    movq (%rax), %rax")
        else:
            self.emit("    movl (%rax), %eax")

    def get_expr_type(self, expr: Expr) -> Optional[TypeSpec]:
        """Try to determine the type of an expression."""
        if isinstance(expr, Identifier):
            _, ts = self.get_var_location(expr.name)
            if ts is not None:
                return ts
            # Function name used as value decays to function pointer
            if expr.name in self.func_return_types:
                rt = self.func_return_types[expr.name]
                return TypeSpec(base=rt.base, pointer_depth=rt.pointer_depth + 1,
                                is_unsigned=rt.is_unsigned, struct_def=rt.struct_def)
            return None
        if isinstance(expr, IntLiteral):
            s = expr.suffix.upper()
            val = expr.value
            if 'LL' in s:
                base = "long long"
            elif 'L' in s:
                base = "long"
            elif val > 4294967295:  # > UINT32_MAX: must be long
                base = "long"
            elif val > 2147483647:  # > INT32_MAX: unsigned int
                base = "int"
            else:
                base = "int"
            is_unsigned = 'U' in s
            if not is_unsigned and val > 2147483647 and base == "int":
                is_unsigned = True  # hex/octal large values are unsigned int
            return TypeSpec(base=base, is_unsigned=is_unsigned)
        if isinstance(expr, StringLiteral):
            return TypeSpec(base="char", pointer_depth=1)
        if isinstance(expr, FloatLiteral):
            return TypeSpec(base="float" if expr.is_single else "double")
        if isinstance(expr, UnaryOp) and expr.op in ("-", "+", "~"):
            return self.get_expr_type(expr.operand)
        if isinstance(expr, UnaryOp) and expr.op == "!":
            return TypeSpec(base="int")
        if isinstance(expr, UnaryOp) and expr.op == "*":
            inner = self.get_expr_type(expr.operand)
            if inner and (inner.is_ptr_array or (inner.is_array() and inner.pointer_depth > 0)):
                # Dereferencing a pointer array: element is the pointer type (keep pd)
                return TypeSpec(base=inner.base, pointer_depth=inner.pointer_depth,
                                struct_def=inner.struct_def, enum_def=inner.enum_def,
                                is_unsigned=inner.is_unsigned)
            if inner and inner.is_pointer() and inner.array_sizes:
                # Pointer-to-array: *p gives the array type
                return TypeSpec(base=inner.base, pointer_depth=inner.pointer_depth - 1,
                                struct_def=inner.struct_def, enum_def=inner.enum_def,
                                is_unsigned=inner.is_unsigned,
                                array_sizes=inner.array_sizes)
            if inner and inner.is_pointer():
                return TypeSpec(base=inner.base, pointer_depth=inner.pointer_depth - 1,
                                struct_def=inner.struct_def, enum_def=inner.enum_def,
                                is_unsigned=inner.is_unsigned)
            if inner and inner.is_array():
                # Dereferencing array: element type (array decays to pointer, then deref)
                return TypeSpec(base=inner.base, pointer_depth=0,
                                struct_def=inner.struct_def, enum_def=inner.enum_def,
                                is_unsigned=inner.is_unsigned)
        if isinstance(expr, UnaryOp) and expr.op == "&":
            inner = self.get_expr_type(expr.operand)
            if inner:
                return TypeSpec(base=inner.base, pointer_depth=inner.pointer_depth + 1,
                                struct_def=inner.struct_def, enum_def=inner.enum_def,
                                is_unsigned=inner.is_unsigned)
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
                if arr_type.is_array() and arr_type.array_sizes and len(arr_type.array_sizes) > 1:
                    # Multi-dim array: strip first dimension, keep rest
                    return TypeSpec(base=arr_type.base, pointer_depth=arr_type.pointer_depth,
                                    struct_def=arr_type.struct_def,
                                    is_unsigned=arr_type.is_unsigned,
                                    array_sizes=arr_type.array_sizes[1:])
                elif arr_type.is_ptr_array and arr_type.array_sizes and len(arr_type.array_sizes) > 1:
                    # Multi-dim pointer array: strip first dimension
                    return TypeSpec(base=arr_type.base, pointer_depth=arr_type.pointer_depth,
                                    struct_def=arr_type.struct_def,
                                    is_unsigned=arr_type.is_unsigned,
                                    array_sizes=arr_type.array_sizes[1:],
                                    is_ptr_array=True)
                elif arr_type.is_ptr_array:
                    # Single-dim pointer array: element is pointer type
                    return TypeSpec(base=arr_type.base, pointer_depth=arr_type.pointer_depth,
                                    struct_def=arr_type.struct_def,
                                    is_unsigned=arr_type.is_unsigned)
                elif arr_type.is_ptr_array:
                    # Pointer array: element is the pointer type
                    return TypeSpec(base=arr_type.base, pointer_depth=arr_type.pointer_depth,
                                    struct_def=arr_type.struct_def,
                                    is_unsigned=arr_type.is_unsigned)
                elif arr_type.is_pointer() and arr_type.array_sizes and len(arr_type.array_sizes) > 0:
                    # Pointer with inner dimensions (e.g., VLA char(*)[15]): strip pointer, keep array
                    return TypeSpec(base=arr_type.base, pointer_depth=arr_type.pointer_depth - 1,
                                    struct_def=arr_type.struct_def,
                                    is_unsigned=arr_type.is_unsigned,
                                    array_sizes=arr_type.array_sizes)
                elif arr_type.is_array() or arr_type.is_pointer():
                    return TypeSpec(base=arr_type.base, pointer_depth=max(arr_type.pointer_depth - 1, 0),
                                    struct_def=arr_type.struct_def,
                                    is_unsigned=arr_type.is_unsigned)
        if isinstance(expr, BinaryOp) and expr.op in (
                "+", "-", "*", "/", "%", "&", "|", "^", "<<", ">>"):
            lt = self.get_expr_type(expr.left)
            rt = self.get_expr_type(expr.right)
            if lt and (lt.is_pointer() or lt.is_array()):
                return TypeSpec(base=lt.base, pointer_depth=lt.pointer_depth + (1 if lt.is_array() else 0),
                                struct_def=lt.struct_def, is_unsigned=lt.is_unsigned)
            if rt and (rt.is_pointer() or rt.is_array()) and expr.op in ("+", "-"):
                return TypeSpec(base=rt.base, pointer_depth=rt.pointer_depth + (1 if rt.is_array() else 0),
                                struct_def=rt.struct_def, is_unsigned=rt.is_unsigned)
            # Float arithmetic returns float or double based on operand types
            l_is_fp = (lt and lt.base in ("float", "double", "long double") and not lt.is_array()) or isinstance(expr.left, FloatLiteral)
            r_is_fp = (rt and rt.base in ("float", "double", "long double") and not rt.is_array()) or isinstance(expr.right, FloatLiteral)
            if l_is_fp or r_is_fp:
                # Both float -> float; otherwise double
                l_single = (lt and lt.base == "float" and not lt.is_pointer() and not lt.is_array()) or (isinstance(expr.left, FloatLiteral) and expr.left.is_single)
                r_single = (rt and rt.base == "float" and not rt.is_pointer() and not rt.is_array()) or (isinstance(expr.right, FloatLiteral) and expr.right.is_single)
                if l_single and r_single:
                    return TypeSpec(base="float")
                return TypeSpec(base="double")
            # Shifts: result type is promoted type of LEFT operand only
            if expr.op in ("<<", ">>"):
                if lt:
                    # Integer promotions: unsigned short/char promote to signed int
                    # Only unsigned int/long/long long stay unsigned
                    promoted_unsigned = lt.is_unsigned and lt.size_bytes() >= 4
                    return TypeSpec(base=lt.base if lt.base in ("long", "long long") else "int",
                                   is_unsigned=promoted_unsigned)
            # Usual arithmetic conversions: long long > long > int
            if (lt and lt.base == "long long") or (rt and rt.base == "long long"):
                is_uns = (lt and lt.is_unsigned) or (rt and rt.is_unsigned)
                return TypeSpec(base="long long", is_unsigned=is_uns)
            if (lt and lt.base == "long") or (rt and rt.base == "long"):
                is_uns = (lt and lt.is_unsigned) or (rt and rt.is_unsigned)
                return TypeSpec(base="long", is_unsigned=is_uns)
            # Both int: propagate unsigned only when either is unsigned int
            if lt and rt and not lt.is_pointer() and not rt.is_pointer():
                is_uns = (lt.is_unsigned and lt.size_bytes() >= 4) or \
                         (rt.is_unsigned and rt.size_bytes() >= 4)
                return TypeSpec(base="int", is_unsigned=is_uns)
        if isinstance(expr, FuncCall):
            if isinstance(expr.name, Identifier) and expr.name.name in self.func_return_types:
                return self.func_return_types[expr.name.name]
            # Indirect call through function pointer: return type is one pointer level less
            callee_type = self.get_expr_type(expr.name)
            if callee_type and callee_type.is_pointer() and callee_type.pointer_depth >= 1:
                return TypeSpec(base=callee_type.base,
                                pointer_depth=callee_type.pointer_depth - 1,
                                struct_def=callee_type.struct_def,
                                enum_def=callee_type.enum_def)
        if isinstance(expr, UnaryOp) and expr.op in ("++", "--"):
            return self.get_expr_type(expr.operand)
        if isinstance(expr, Assignment):
            return self.get_expr_type(expr.target)
        if isinstance(expr, CastExpr):
            return expr.target_type
        if isinstance(expr, TernaryOp):
            tt = self.get_expr_type(expr.true_expr)
            ft = self.get_expr_type(expr.false_expr)
            # Prefer float branch type (matches gen_ternary's promotion behavior)
            t_is_float = tt and tt.base in ("float", "double", "long double") and not tt.is_pointer()
            f_is_float = ft and ft.base in ("float", "double", "long double") and not ft.is_pointer()
            if f_is_float and not t_is_float:
                return ft
            return tt
        if isinstance(expr, BuiltinVaArg):
            return expr.target_type
        return None

    def _generic_types_match(self, controlling: TypeSpec, assoc: TypeSpec) -> bool:
        """Check if a controlling expression type matches a _Generic association type.
        Applies lvalue conversion: strips top-level const from non-pointer scalars."""
        # Apply lvalue conversion: strip const from scalar (non-pointer) types
        ctrl_const = controlling.is_const if controlling.pointer_depth > 0 else False
        if controlling.pointer_depth != assoc.pointer_depth:
            return False
        if controlling.is_unsigned != assoc.is_unsigned:
            return False
        if controlling.base != assoc.base:
            return False
        if ctrl_const != assoc.is_const:
            return False
        if controlling.is_array() != assoc.is_array():
            return False
        return True

    def gen_member_addr(self, expr: MemberAccess):
        """Generate address of a struct member into %rax."""
        if expr.arrow:
            # expr->member: obj is a pointer, load it
            self.gen_expr(expr.obj)
        elif isinstance(expr.obj, FuncCall) or isinstance(expr.obj, BuiltinVaArg):
            # Function call returning struct: store to temp, get address
            obj_type = self.get_expr_type(expr.obj) if isinstance(expr.obj, FuncCall) else None
            if isinstance(expr.obj, BuiltinVaArg):
                obj_type = expr.obj.target_type
            if obj_type and self._is_struct_by_value(obj_type):
                size = obj_type.size_bytes()
                alloc = (size + 7) & ~7
                self.stack_offset -= alloc
                temp_off = self.stack_offset
                self.gen_expr(expr.obj)
                # For FuncCall returning struct: result in %rax (and %rdx for 9-16 bytes)
                if isinstance(expr.obj, FuncCall):
                    if size <= 8:
                        self.emit(f"    movq %rax, {temp_off}(%rbp)")
                    elif size <= 16:
                        self.emit(f"    movq %rax, {temp_off}(%rbp)")
                        self.emit(f"    movq %rdx, {temp_off + 8}(%rbp)")
                    else:
                        # >16 bytes: %rax has pointer
                        self._emit_memcpy_from_rax(temp_off, size)
                else:
                    # BuiltinVaArg returns address in %rax
                    self._emit_memcpy_from_rax(temp_off, size)
                self.emit(f"    leaq {temp_off}(%rbp), %rax")
            else:
                self.gen_lvalue_addr(expr.obj)
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
        # Determine member type for load size
        obj_type = self.get_expr_type(expr.obj)
        sdef = obj_type.struct_def if obj_type else None
        mem_type = sdef.member_type(expr.member) if sdef else None

        # Bitfield read: load storage unit, shift, mask
        if sdef:
            bf = sdef.bitfield_info(expr.member)
            if bf:
                unit_off, unit_size, bit_start, bit_width = bf
                self.gen_member_addr(expr)  # addr of storage unit
                if unit_size == 4:
                    self.emit("    movl (%rax), %eax")
                elif unit_size == 8:
                    self.emit("    movq (%rax), %rax")
                elif unit_size == 2:
                    self.emit("    movzwl (%rax), %eax")
                else:
                    self.emit("    movzbl (%rax), %eax")
                if bit_start > 0:
                    if unit_size == 8:
                        self.emit(f"    shrq ${bit_start}, %rax")
                    else:
                        self.emit(f"    shrl ${bit_start}, %eax")
                mask = (1 << bit_width) - 1
                if unit_size == 8:
                    self.emit(f"    movq ${mask}, %rcx")
                    self.emit(f"    andq %rcx, %rax")
                else:
                    self.emit(f"    andl ${mask}, %eax")
                return

        self.gen_member_addr(expr)

        if mem_type and (mem_type.is_array() or mem_type.is_ptr_array):
            # Array member: return address (don't dereference)
            pass  # address already in %rax from gen_member_addr
        elif mem_type is None:
            self.emit("    movl (%rax), %eax")
        elif mem_type.base == "float" and not mem_type.is_pointer():
            # Load 32-bit float, convert to 64-bit double, store in %rax
            self.emit("    movss (%rax), %xmm0")
            self.emit("    cvtss2sd %xmm0, %xmm0")
            self.emit("    movq %xmm0, %rax")
        elif mem_type.base == "double" and not mem_type.is_pointer():
            # Load 64-bit double into %rax
            self.emit("    movsd (%rax), %xmm0")
            self.emit("    movq %xmm0, %rax")
        elif mem_type.base == "long double" and not mem_type.is_pointer():
            # Long double: 80-bit x87 value stored in 16 bytes
            # Load the raw 16 bytes into rax (first 8 bytes).
            # The full 16-byte value is at (%rax) before we load.
            # For proper long double handling, we copy the full 16 bytes to a temp.
            self.stack_offset -= 16
            temp_off = self.stack_offset
            self.emit(f"    movq (%rax), %rcx")
            self.emit(f"    movq %rcx, {temp_off}(%rbp)")
            self.emit(f"    movq 8(%rax), %rcx")
            self.emit(f"    movq %rcx, {temp_off + 8}(%rbp)")
            # Store temp offset for long double push path
            self.emit(f"    movq {temp_off}(%rbp), %rax")
        elif mem_type.is_pointer() or mem_type.size_bytes() == 8:
            self.emit("    movq (%rax), %rax")
        elif mem_type.size_bytes() == 1 and not mem_type.is_pointer():
            if mem_type.is_unsigned:
                self.emit("    movzbl (%rax), %eax")
            else:
                self.emit("    movsbl (%rax), %eax")
        elif mem_type.size_bytes() == 2 and not mem_type.is_pointer():
            if mem_type.is_unsigned:
                self.emit("    movzwl (%rax), %eax")
            else:
                self.emit("    movswl (%rax), %eax")
        else:
            self.emit("    movl (%rax), %eax")

    def _is_float_type(self, expr):
        """Check if expression has float/double type."""
        et = self.get_expr_type(expr)
        return et and et.base in ("float", "double", "long double") and not et.is_pointer() and not et.is_array()

    def _is_single_float(self, expr):
        """Check if expression has specifically 'float' (single-precision) type."""
        et = self.get_expr_type(expr)
        return et and et.base == "float" and not et.is_pointer() and not et.is_array()

    def _gen_float_operands(self, expr, use_single=False):
        """Load binary op operands into xmm0 (left) and xmm1 (right).
        If use_single is True, operands are kept/converted to single precision."""
        lt = self.get_expr_type(expr.left)
        if lt and lt.base in ("float", "double", "long double") and not lt.is_pointer() and not lt.is_array():
            self.gen_expr(expr.left)
            self.emit("    movq %rax, %xmm0")
            # gen_load_var promotes float->double; convert back if we need single
            if use_single and lt.base != "float":
                self.emit("    cvtsd2ss %xmm0, %xmm0")
            elif use_single and lt.base == "float":
                # Value was promoted to double by gen_load_var; convert back to single
                self.emit("    cvtsd2ss %xmm0, %xmm0")
        elif isinstance(expr.left, FloatLiteral):
            self.gen_expr(expr.left)
            # FloatLiteral codegen loads as double into xmm0
            if use_single:
                self.emit("    cvtsd2ss %xmm0, %xmm0")
        else:
            self.gen_expr(expr.left)
            if use_single:
                self.emit("    cvtsi2ss %eax, %xmm0")
            else:
                self.emit("    cvtsi2sd %eax, %xmm0")
        self.emit("    subq $8, %rsp")
        if use_single:
            self.emit("    movss %xmm0, (%rsp)")  # save left (single)
        else:
            self.emit("    movsd %xmm0, (%rsp)")  # save left

        rt = self.get_expr_type(expr.right)
        if rt and rt.base in ("float", "double", "long double") and not rt.is_pointer() and not rt.is_array():
            self.gen_expr(expr.right)
            self.emit("    movq %rax, %xmm1")
            if use_single:
                self.emit("    cvtsd2ss %xmm1, %xmm1")
        elif isinstance(expr.right, FloatLiteral):
            self.gen_expr(expr.right)
            if use_single:
                self.emit("    cvtsd2ss %xmm0, %xmm1")
            else:
                self.emit("    movsd %xmm0, %xmm1")
        else:
            self.gen_expr(expr.right)
            if use_single:
                self.emit("    cvtsi2ss %eax, %xmm1")
            else:
                self.emit("    cvtsi2sd %eax, %xmm1")

        if use_single:
            self.emit("    movss (%rsp), %xmm0")  # restore left (single)
        else:
            self.emit("    movsd (%rsp), %xmm0")  # restore left
        self.emit("    addq $8, %rsp")

    def gen_binary_op(self, expr: BinaryOp):
        # Float operations: arithmetic and comparison
        is_float_op = (self._is_float_type(expr.left) or self._is_float_type(expr.right) or
                        isinstance(expr.left, FloatLiteral) or isinstance(expr.right, FloatLiteral))
        if is_float_op and expr.op in ("+", "-", "*", "/", "<", ">", "<=", ">=", "==", "!="):
            # Use single-precision when BOTH operands are float (not double)
            both_single = (self._is_single_float(expr.left) or (isinstance(expr.left, FloatLiteral) and expr.left.is_single)) and \
                          (self._is_single_float(expr.right) or (isinstance(expr.right, FloatLiteral) and expr.right.is_single))
            self._gen_float_operands(expr, use_single=both_single)

            if expr.op in ("+", "-", "*", "/"):
                if both_single:
                    sse_ops = {"+": "addss", "-": "subss", "*": "mulss", "/": "divss"}
                    self.emit(f"    {sse_ops[expr.op]} %xmm1, %xmm0")
                    # Convert back to double for storage in %rax (codegen convention)
                    self.emit("    cvtss2sd %xmm0, %xmm0")
                else:
                    sse_ops = {"+": "addsd", "-": "subsd", "*": "mulsd", "/": "divsd"}
                    self.emit(f"    {sse_ops[expr.op]} %xmm1, %xmm0")
                self.emit(f"    movq %xmm0, %rax")  # result in rax for push/pop
                return
            else:
                # Comparison
                if both_single:
                    self.emit("    ucomiss %xmm1, %xmm0")
                else:
                    self.emit("    ucomisd %xmm1, %xmm0")
                if expr.op == "==":
                    # NaN-aware: equal only if ZF=1 AND PF=0 (ordered)
                    self.emit("    sete %al")
                    self.emit("    setnp %cl")
                    self.emit("    andb %cl, %al")
                elif expr.op == "!=":
                    # NaN-aware: not-equal if ZF=0 OR PF=1 (unordered)
                    self.emit("    setne %al")
                    self.emit("    setp %cl")
                    self.emit("    orb %cl, %al")
                else:
                    cond_map = {
                        "<": "setb", ">": "seta",
                        "<=": "setbe", ">=": "setae",
                    }
                    self.emit(f"    {cond_map[expr.op]} %al")
            self.emit("    movzbl %al, %eax")
            return

        # Short-circuit for && and ||
        if expr.op == "&&":
            false_label = self.new_label("and_false")
            end_label = self.new_label("and_end")
            self.gen_expr(expr.left)
            self._emit_cond_test(expr.left)
            self.emit(f"    je {false_label}")
            self.gen_expr(expr.right)
            self._emit_cond_test(expr.right)
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
            self._emit_cond_test(expr.left)
            self.emit(f"    jne {true_label}")
            self.gen_expr(expr.right)
            self._emit_cond_test(expr.right)
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
        is_ptr_op = ((left_type and (left_type.is_pointer() or left_type.is_array())) or
                      (right_type and (right_type.is_pointer() or right_type.is_array())))

        # Check for 64-bit operations (long, long long, unsigned long)
        is_64bit = (is_ptr_op or
                    (left_type and left_type.base in ("long", "long long") and not left_type.is_pointer()) or
                    (right_type and right_type.base in ("long", "long long") and not right_type.is_pointer()))

        if is_ptr_op or is_64bit:
            # Sign-extend right operand if it's a narrower type
            right_is_narrow = (right_type is None or
                               (right_type.base not in ("long", "long long") and
                                not right_type.is_pointer() and
                                not right_type.is_array()))
            if right_is_narrow:
                if right_type and right_type.is_unsigned:
                    self.emit("    movl %eax, %eax")  # zero-extend
                else:
                    self.emit("    cltq")  # sign-extend eax to rax
            self.emit("    movq %rax, %rcx")   # right operand in rcx (64-bit)
            self.emit("    popq %rax")          # left operand in rax
            # Sign-extend left operand if narrower (int in a long/ptr context)
            left_is_narrow = (left_type is not None and
                              left_type.base not in ("long", "long long") and
                              not left_type.is_pointer())
            if left_is_narrow and not is_ptr_op:
                if left_type.is_unsigned:
                    self.emit("    movl %eax, %eax")  # zero-extend
                else:
                    self.emit("    cltq")  # sign-extend eax to rax
        else:
            self.emit("    movl %eax, %ecx")   # right operand in ecx (32-bit for ints)
            self.emit("    popq %rax")          # left operand in eax

        if expr.op == "+" and left_type and (left_type.is_pointer() or left_type.is_array()):
            # pointer/array + int: scale int by element size, result in rax
            elem_size = TypeSpec(base=left_type.base, pointer_depth=max(left_type.pointer_depth - 1, 0),
                                  struct_def=left_type.struct_def).size_bytes()
            if left_type.is_array() and left_type.struct_def:
                elem_size = left_type.struct_def.size_bytes()
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
        elif expr.op == "+" and is_64bit:
            self.emit("    addq %rcx, %rax")
        elif expr.op == "+":
            self.emit("    addl %ecx, %eax")
        elif expr.op == "-" and left_type and (left_type.is_pointer() or left_type.is_array()):
            # pointer - int: scale int by element size
            right_is_ptr = right_type and (right_type.is_pointer() or right_type.is_array())
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
                elem_size = TypeSpec(base=left_type.base, pointer_depth=left_type.pointer_depth - 1,
                                     struct_def=left_type.struct_def).size_bytes()
                if elem_size > 1:
                    self.emit("    cqo")
                    self.emit(f"    movq ${elem_size}, %rcx")
                    self.emit("    idivq %rcx")
        elif expr.op == "-" and is_64bit:
            self.emit("    subq %rcx, %rax")
        elif expr.op == "-":
            self.emit("    subl %ecx, %eax")
        elif expr.op == "*" and is_64bit:
            self.emit("    imulq %rcx, %rax")
        elif expr.op == "*":
            self.emit("    imull %ecx, %eax")
        elif expr.op == "/" and is_64bit:
            if left_type and left_type.is_unsigned:
                self.emit("    xorq %rdx, %rdx")
                self.emit("    divq %rcx")
            else:
                self.emit("    cqo")
                self.emit("    idivq %rcx")
        elif expr.op == "/":
            if left_type and left_type.is_unsigned:
                self.emit("    xorl %edx, %edx")
                self.emit("    divl %ecx")
            else:
                self.emit("    cdq")
                self.emit("    idivl %ecx")
        elif expr.op == "%" and is_64bit:
            if left_type and left_type.is_unsigned:
                self.emit("    xorq %rdx, %rdx")
                self.emit("    divq %rcx")
            else:
                self.emit("    cqo")
                self.emit("    idivq %rcx")
            self.emit("    movq %rdx, %rax")
        elif expr.op == "%":
            if left_type and left_type.is_unsigned:
                self.emit("    xorl %edx, %edx")
                self.emit("    divl %ecx")
            else:
                self.emit("    cdq")
                self.emit("    idivl %ecx")
            self.emit("    movl %edx, %eax")
        elif expr.op == "&":
            if is_64bit:
                self.emit("    andq %rcx, %rax")
            else:
                self.emit("    andl %ecx, %eax")
        elif expr.op == "|":
            if is_64bit:
                self.emit("    orq %rcx, %rax")
            else:
                self.emit("    orl %ecx, %eax")
        elif expr.op == "^":
            if is_64bit:
                self.emit("    xorq %rcx, %rax")
            else:
                self.emit("    xorl %ecx, %eax")
        elif expr.op == "<<":
            if is_64bit:
                self.emit("    shlq %cl, %rax")
            else:
                self.emit("    shll %cl, %eax")
        elif expr.op == ">>":
            if is_64bit:
                if left_type and left_type.is_unsigned:
                    self.emit("    shrq %cl, %rax")
                else:
                    self.emit("    sarq %cl, %rax")
            else:
                if left_type and left_type.is_unsigned:
                    self.emit("    shrl %cl, %eax")
                else:
                    self.emit("    sarl %cl, %eax")
        elif expr.op in ("==", "!=", "<", ">", "<=", ">="):
            if is_64bit or is_ptr_op:
                self.emit("    cmpq %rcx, %rax")
            else:
                self.emit("    cmpl %ecx, %eax")
            # Use unsigned comparison when either operand is unsigned int/long
            either_unsigned = ((left_type and left_type.is_unsigned and left_type.size_bytes() >= 4) or
                              (right_type and right_type.is_unsigned and right_type.size_bytes() >= 4))
            if either_unsigned and expr.op not in ("==", "!="):
                cond_map = {
                    "<": "setb", ">": "seta",
                    "<=": "setbe", ">=": "setae",
                }
            else:
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
            if self._is_float_type(expr.operand) or isinstance(expr.operand, FloatLiteral):
                self.gen_expr(expr.operand)
                self.emit("    movq %rax, %xmm0")
                # Negate by XOR with sign bit
                self.emit("    movabsq $0x8000000000000000, %rax")
                self.emit("    movq %rax, %xmm1")
                self.emit("    xorpd %xmm1, %xmm0")
                self.emit("    movq %xmm0, %rax")
            else:
                self.gen_expr(expr.operand)
                op_type = self.get_expr_type(expr.operand)
                if op_type and (op_type.base in ("long", "long long") or op_type.is_pointer()):
                    self.emit("    negq %rax")
                else:
                    self.emit("    negl %eax")
        elif expr.op == "~":
            self.gen_expr(expr.operand)
            op_type = self.get_expr_type(expr.operand)
            if op_type and (op_type.base in ("long", "long long") or op_type.is_pointer()):
                self.emit("    notq %rax")
            else:
                self.emit("    notl %eax")
        elif expr.op == "!":
            self.gen_expr(expr.operand)
            self._emit_cond_test(expr.operand)
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
                self.emit("    movq (%rax), %rax")
            elif inner_type and inner_type.base == "char" and inner_type.pointer_depth == 1:
                if inner_type.is_unsigned:
                    self.emit("    movzbl (%rax), %eax")
                else:
                    self.emit("    movsbl (%rax), %eax")
            elif inner_type and inner_type.base == "short" and inner_type.pointer_depth == 1:
                if inner_type.is_unsigned:
                    self.emit("    movzwl (%rax), %eax")
                else:
                    self.emit("    movswl (%rax), %eax")
            elif inner_type and inner_type.base == "float" and inner_type.pointer_depth == 1:
                # Load float and convert to double (our float convention uses double internally)
                self.emit("    movss (%rax), %xmm0")
                self.emit("    cvtss2sd %xmm0, %xmm0")
                self.emit("    movq %xmm0, %rax")
            elif inner_type and inner_type.pointer_depth == 1 and (inner_type.base in ("long", "long long", "double") or inner_type.struct_def):
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
            elif operand_type and operand_type.base in ("float", "double") and not operand_type.is_pointer():
                # Float/double increment/decrement
                self.emit("    movsd (%rax), %xmm0")
                if not is_prefix:
                    self.emit("    movsd %xmm0, %xmm1")  # save old value
                # Load 1.0 constant
                self.emit("    movl $1, %eax")
                self.emit("    cvtsi2sd %eax, %xmm2")
                op = "addsd" if is_inc else "subsd"
                self.emit(f"    {op} %xmm2, %xmm0")
                self.emit("    popq %rcx")
                self.emit("    movsd %xmm0, (%rcx)")
                if is_prefix:
                    self.emit("    movq %xmm0, %rax")
                else:
                    self.emit("    movq %xmm1, %rax")
            else:
                store_size = self._type_store_size(operand_type)
                self._emit_load("%rax", store_size, operand_type)
                use_q = store_size == 8
                if not is_prefix:
                    if use_q:
                        self.emit("    movq %rax, %rdx")
                    else:
                        self.emit("    movl %eax, %edx")
                if use_q:
                    op = "addq" if is_inc else "subq"
                    self.emit(f"    {op} ${elem_size}, %rax")
                else:
                    op = "addl" if is_inc else "subl"
                    self.emit(f"    {op} ${elem_size}, %eax")
                self.emit("    popq %rcx")
                self._emit_store("%rcx", store_size)
                if not is_prefix:
                    if use_q:
                        self.emit("    movq %rdx, %rax")
                    else:
                        self.emit("    movl %edx, %eax")
                elif store_size == 1:
                    # Truncate to byte for char/unsigned char prefix inc/dec
                    if operand_type and operand_type.is_unsigned:
                        self.emit("    movzbl %al, %eax")
                    else:
                        self.emit("    movsbl %al, %eax")
        else:
            self.error(f"unhandled unary operator '{expr.op}'", expr.line, expr.col)

    def _emit_cond_test(self, expr):
        """Emit a condition test — uses testq for pointers, cmpl for ints."""
        et = self.get_expr_type(expr) if expr else None
        if et and (et.is_pointer() or et.size_bytes() == 8):
            self.emit("    testq %rax, %rax")
        else:
            self.emit("    cmpl $0, %eax")

    def _target_is_ptr_array_element(self, expr):
        """Check if expr is indexing into a pointer array member (e.g., a->p[0] where p is T*[N])."""
        if not isinstance(expr, ArrayAccess):
            return False
        arr = expr.array
        arr_type = self.get_expr_type(arr)
        # Check if the array expression is a pointer type with array dimensions
        if arr_type and arr_type.is_pointer() and arr_type.pointer_depth >= 1 and arr_type.array_sizes:
            return True
        if arr_type and arr_type.is_ptr_array:
            return True
        return False

    def _type_store_size(self, ts):
        """Return the store/load size in bytes for a type."""
        if not ts:
            return 4
        if ts.is_pointer() or ts.size_bytes() == 8 or ts.base in ("float", "double", "long double"):
            return 8
        if ts.size_bytes() == 2:
            return 2
        if ts.size_bytes() == 1:
            return 1
        return 4

    def _emit_load(self, addr_reg, size, ts=None):
        """Emit a load from (addr_reg) into %rax with correct width."""
        if size == 8:
            self.emit(f"    movq ({addr_reg}), %rax")
        elif size == 2:
            if ts and ts.is_unsigned:
                self.emit(f"    movzwl ({addr_reg}), %eax")
            else:
                self.emit(f"    movswl ({addr_reg}), %eax")
        elif size == 1:
            if ts and ts.is_unsigned:
                self.emit(f"    movzbl ({addr_reg}), %eax")
            else:
                self.emit(f"    movsbl ({addr_reg}), %eax")
        else:
            self.emit(f"    movl ({addr_reg}), %eax")

    def _emit_store(self, addr_reg, size):
        """Emit a store from %rax/%eax/%ax/%al to (addr_reg)."""
        if size == 8:
            self.emit(f"    movq %rax, ({addr_reg})")
        elif size == 2:
            self.emit(f"    movw %ax, ({addr_reg})")
        elif size == 1:
            self.emit(f"    movb %al, ({addr_reg})")
        else:
            self.emit(f"    movl %eax, ({addr_reg})")

    def gen_assignment(self, expr: Assignment):
        # Bitfield write: target is MemberAccess to a bitfield member
        if expr.op == "=" and isinstance(expr.target, MemberAccess):
            obj_type = self.get_expr_type(expr.target.obj)
            sdef = obj_type.struct_def if obj_type else None
            if sdef:
                bf = sdef.bitfield_info(expr.target.member)
                if bf:
                    unit_off, unit_size, bit_start, bit_width = bf
                    # Evaluate value into %rax
                    self.gen_expr(expr.value)
                    self.emit("    pushq %rax")
                    # Get storage unit address
                    self.gen_member_addr(expr.target)
                    self.emit("    movq %rax, %rcx")  # rcx = addr of storage unit
                    # Load current storage unit
                    if unit_size == 4:
                        self.emit("    movl (%rcx), %edx")
                    elif unit_size == 8:
                        self.emit("    movq (%rcx), %rdx")
                    elif unit_size == 2:
                        self.emit("    movzwl (%rcx), %edx")
                    else:
                        self.emit("    movzbl (%rcx), %edx")
                    # Clear the bitfield bits
                    mask = (1 << bit_width) - 1
                    clear_mask = (~(mask << bit_start)) & ((1 << (unit_size * 8)) - 1)
                    if unit_size == 8:
                        self.emit(f"    movabsq ${clear_mask}, %r11")
                        self.emit(f"    andq %r11, %rdx")
                    else:
                        self.emit(f"    andl ${clear_mask}, %edx")
                    # Pop new value, mask and shift
                    self.emit("    popq %rax")
                    if unit_size == 8:
                        self.emit(f"    movq ${mask}, %r11")
                        self.emit(f"    andq %r11, %rax")
                        if bit_start > 0:
                            self.emit(f"    shlq ${bit_start}, %rax")
                        self.emit(f"    orq %rdx, %rax")
                        self.emit(f"    movq %rax, (%rcx)")
                    else:
                        self.emit(f"    andl ${mask}, %eax")
                        if bit_start > 0:
                            self.emit(f"    shll ${bit_start}, %eax")
                        self.emit(f"    orl %edx, %eax")
                        if unit_size == 4:
                            self.emit(f"    movl %eax, (%rcx)")
                        elif unit_size == 2:
                            self.emit(f"    movw %ax, (%rcx)")
                        else:
                            self.emit(f"    movb %al, (%rcx)")
                    return

        if expr.op == "=":
            target_type = self.get_expr_type(expr.target)
            value_type = self.get_expr_type(expr.value)
            target_is_float = target_type and target_type.base in ("float", "double", "long double") and not target_type.is_pointer() and not target_type.is_array()
            value_is_float = (value_type and value_type.base in ("float", "double", "long double") and not value_type.is_pointer() and not value_type.is_array()) or isinstance(expr.value, FloatLiteral)

            # Struct assignment: copy all bytes (but NOT for pointers or pointer arrays)
            # Also skip when the target is an array access into a pointer-with-array member
            # (e.g., a->p[0] where p is patch_t*[3] — element is a pointer, not struct)
            target_is_ptr_element = (isinstance(expr.target, ArrayAccess) and
                                     target_type and target_type.struct_def and
                                     target_type.pointer_depth == 0 and
                                     self._target_is_ptr_array_element(expr.target))
            if target_type and self._is_struct_by_value(target_type) and \
               not target_type.is_pointer() and not target_type.is_ptr_array and \
               not target_is_ptr_element:
                struct_size = target_type.struct_def.size_bytes()
                # Get source address (value is a struct, gen_expr puts address in rax)
                # If value is a bare InitList (compound literal without cast), wrap it
                # with the target's type so gen_lvalue_addr knows the struct layout
                src_value = expr.value
                if isinstance(src_value, InitList) and target_type.struct_def:
                    src_value = CastExpr(target_type=target_type, operand=src_value,
                                        line=getattr(src_value, 'line', 0),
                                        col=getattr(src_value, 'col', 0))
                self.gen_lvalue_addr(src_value)
                self.emit("    pushq %rax")     # source address
                self.gen_lvalue_addr(expr.target)
                self.emit("    movq %rax, %rdi") # dest
                self.emit("    popq %rsi")       # source
                # Copy using rep movsb
                self.emit(f"    movl ${struct_size}, %ecx")
                self.emit("    pushq %rdi")      # save dest before rep movsb advances it
                self.emit("    rep movsb")
                self.emit("    popq %rax")        # return dest address (for chained assignment)
                return

            self.gen_expr(expr.value)

            # _Bool truncation: any non-zero value becomes 1
            if target_type and target_type.base == "_Bool" and not target_type.is_pointer():
                self.emit("    testl %eax, %eax")
                self.emit("    setne %al")
                self.emit("    movzbl %al, %eax")

            # Int-to-float or float-to-int conversion
            if target_is_float and not value_is_float:
                self.emit("    cvtsi2sd %eax, %xmm0")
                if target_type and target_type.base == "float":
                    self.emit("    cvtsd2ss %xmm0, %xmm0")
                    self.emit("    movd %xmm0, %eax")
                else:
                    self.emit("    movq %xmm0, %rax")
            elif not target_is_float and value_is_float:
                self.emit("    movq %rax, %xmm0")
                self.emit("    cvttsd2si %xmm0, %eax")
            elif target_is_float and value_is_float and target_type and target_type.base == "float":
                # double value → float target: truncate to float precision
                self.emit("    movq %rax, %xmm0")
                self.emit("    cvtsd2ss %xmm0, %xmm0")
                self.emit("    movd %xmm0, %eax")

            self.emit("    pushq %rax")
            self.gen_lvalue_addr(expr.target)
            self.emit("    movq %rax, %rcx")
            self.emit("    popq %rax")

            # Determine store size
            store_size = 4
            if target_is_ptr_element:
                store_size = 8  # pointer array element
            elif target_type:
                if target_type.base == "float" and target_is_float:
                    store_size = 4  # float is 4 bytes
                elif target_is_float or target_type.is_pointer() or target_type.size_bytes() == 8:
                    store_size = 8
                elif target_type.size_bytes() == 2:
                    store_size = 2
                elif target_type.base in ("char", "_Bool") and not target_type.is_pointer():
                    store_size = 1
            elif isinstance(expr.target, Identifier):
                _, ts = self.get_var_location(expr.target.name)
                if ts and (ts.is_pointer() or ts.size_bytes() == 8):
                    store_size = 8
            # Fallback for nested array access: infer from root type
            if store_size == 4 and isinstance(expr.target, ArrayAccess):
                root = expr.target
                while isinstance(root, ArrayAccess):
                    root = root.array
                if isinstance(root, Identifier):
                    _, root_ts = self.get_var_location(root.name)
                    if root_ts and root_ts.base in ("long", "long long", "double"):
                        store_size = 8
                    elif root_ts and root_ts.base == "char":
                        store_size = 1
                    elif root_ts and root_ts.base == "short":
                        store_size = 2
                elif isinstance(root, MemberAccess):
                    root_type = self.get_expr_type(root)
                    if root_type and root_type.base in ("long", "long long", "double"):
                        store_size = 8
                    elif root_type and root_type.base == "char":
                        store_size = 1
                    elif root_type and root_type.base == "short":
                        store_size = 2

            if store_size == 1:
                self.emit("    movb %al, (%rcx)")
            elif store_size == 2:
                self.emit("    movw %ax, (%rcx)")
            elif store_size == 8:
                self.emit("    movq %rax, (%rcx)")
            else:
                self.emit("    movl %eax, (%rcx)")
        else:
            # Compound assignment: +=, -=, etc.
            op = expr.op[:-1]  # strip '='
            target_type = self.get_expr_type(expr.target)
            is_ptr = target_type and target_type.is_pointer()
            is_float_target = target_type and target_type.base in ("float", "double", "long double") and not is_ptr

            if is_float_target and op in ("+", "-", "*", "/"):
                # Float compound assignment: a += 1.0
                is_float32 = target_type and target_type.base == "float"
                self.gen_lvalue_addr(expr.target)
                self.emit("    pushq %rax")          # save address
                if is_float32:
                    self.emit("    movss (%rax), %xmm0")  # load 4-byte float
                    self.emit("    cvtss2sd %xmm0, %xmm0")  # promote to double
                else:
                    self.emit("    movsd (%rax), %xmm0")  # load 8-byte double
                self.emit("    subq $8, %rsp")
                self.emit("    movsd %xmm0, (%rsp)") # save current value
                self.gen_expr(expr.value)             # evaluate RHS
                value_is_float = self._is_float_type(expr.value) or isinstance(expr.value, FloatLiteral)
                if value_is_float:
                    self.emit("    movq %rax, %xmm1")
                else:
                    self.emit("    cvtsi2sd %eax, %xmm1")
                self.emit("    movsd (%rsp), %xmm0") # restore current
                self.emit("    addq $8, %rsp")
                sse_ops = {"+": "addsd", "-": "subsd", "*": "mulsd", "/": "divsd"}
                self.emit(f"    {sse_ops[op]} %xmm1, %xmm0")
                self.emit("    popq %rcx")            # restore address
                if is_float32:
                    self.emit("    cvtsd2ss %xmm0, %xmm0")
                    self.emit(f"    movss %xmm0, (%rcx)")
                else:
                    self.emit(f"    movsd %xmm0, (%rcx)")
                self.emit("    movq %xmm0, %rax")    # result in rax
                return

            store_size = self._type_store_size(target_type)
            is_long = store_size == 8 and not is_ptr

            self.gen_lvalue_addr(expr.target)
            self.emit("    pushq %rax")
            self._emit_load("%rax", store_size, target_type)
            self.emit("    pushq %rax")
            self.gen_expr(expr.value)
            if is_long or is_ptr:
                self.emit("    movq %rax, %rcx")
            else:
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
            elif is_long:
                # 64-bit operations for long/long long
                q_ops = {"+": "addq", "-": "subq", "&": "andq", "|": "orq", "^": "xorq"}
                if op in q_ops:
                    self.emit(f"    {q_ops[op]} %rcx, %rax")
                elif op == "<<":
                    self.emit("    shlq %cl, %rax")
                elif op == ">>":
                    if target_type and target_type.is_unsigned:
                        self.emit("    shrq %cl, %rax")
                    else:
                        self.emit("    sarq %cl, %rax")
                elif op == "*":
                    self.emit("    imulq %rcx, %rax")
                elif op == "/":
                    if target_type and target_type.is_unsigned:
                        self.emit("    xorq %rdx, %rdx")
                        self.emit("    divq %rcx")
                    else:
                        self.emit("    cqo")
                        self.emit("    idivq %rcx")
                elif op == "%":
                    if target_type and target_type.is_unsigned:
                        self.emit("    xorq %rdx, %rdx")
                        self.emit("    divq %rcx")
                    else:
                        self.emit("    cqo")
                        self.emit("    idivq %rcx")
                    self.emit("    movq %rdx, %rax")
            elif op == "+":
                self.emit("    addl %ecx, %eax")
            elif op == "-":
                self.emit("    subl %ecx, %eax")
            elif op == "*":
                self.emit("    imull %ecx, %eax")
            elif op == "/":
                if target_type and target_type.is_unsigned:
                    self.emit("    xorl %edx, %edx")
                    self.emit("    divl %ecx")
                else:
                    self.emit("    cdq")
                    self.emit("    idivl %ecx")
            elif op == "%":
                if target_type and target_type.is_unsigned:
                    self.emit("    xorl %edx, %edx")
                    self.emit("    divl %ecx")
                else:
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
                if target_type and target_type.is_unsigned:
                    self.emit("    shrl %cl, %eax")
                else:
                    self.emit("    sarl %cl, %eax")

            self.emit("    popq %rcx")
            self._emit_store("%rcx", store_size)

    def gen_func_call(self, expr: FuncCall):
        func_name = expr.name.name if isinstance(expr.name, Identifier) else None

        # Handle __builtin_alloca: inline stack allocation
        if func_name in ("__builtin_alloca", "alloca"):
            if expr.args:
                self.gen_expr(expr.args[0])             # size in %rax
                self.emit("    addq $15, %rax")          # align up to 16
                self.emit("    andq $-16, %rax")
                self.emit("    subq %rax, %rsp")         # allocate on stack
                self.emit("    movq %rsp, %rax")         # return pointer
                self.emit("    pushq %rax")              # push result
            else:
                self.emit("    pushq $0")
            return

        # Handle va_start/va_end/va_copy builtins
        if func_name == "__builtin_va_start":
            self._gen_va_start(expr)
            return
        if func_name == "__builtin_va_end":
            # va_end is a no-op
            return
        if func_name == "__builtin_va_copy":
            self._gen_va_copy(expr)
            return

        # __builtin_constant_p: always return 0 (conservative)
        if func_name == "__builtin_constant_p":
            if expr.args:
                self.gen_expr(expr.args[0])  # evaluate for side effects
            self.emit("    xorl %eax, %eax")  # return 0
            return

        # __builtin_bswap16/32/64: byte-swap intrinsics
        if func_name == "__builtin_bswap16" and expr.args:
            self.gen_expr(expr.args[0])
            self.emit("    rolw $8, %ax")  # swap bytes of 16-bit value
            self.emit("    movzwl %ax, %eax")
            return
        if func_name == "__builtin_bswap32" and expr.args:
            self.gen_expr(expr.args[0])
            self.emit("    bswap %eax")
            return
        if func_name == "__builtin_bswap64" and expr.args:
            self.gen_expr(expr.args[0])
            self.emit("    bswap %rax")
            return

        # __builtin_popcount/popcountl/popcountll: count set bits
        if func_name == "__builtin_popcount" and expr.args:
            self.gen_expr(expr.args[0])
            self.emit("    popcntl %eax, %eax")
            return
        if func_name in ("__builtin_popcountl", "__builtin_popcountll") and expr.args:
            self.gen_expr(expr.args[0])
            self.emit("    popcntq %rax, %rax")
            return

        # __builtin_clz/ctz: count leading/trailing zeros
        if func_name == "__builtin_clz" and expr.args:
            self.gen_expr(expr.args[0])
            self.emit("    bsrl %eax, %eax")
            self.emit("    xorl $31, %eax")
            return
        if func_name in ("__builtin_clzl", "__builtin_clzll") and expr.args:
            self.gen_expr(expr.args[0])
            self.emit("    bsrq %rax, %rax")
            self.emit("    xorq $63, %rax")
            return
        if func_name == "__builtin_ctz" and expr.args:
            self.gen_expr(expr.args[0])
            self.emit("    bsfl %eax, %eax")
            return
        if func_name in ("__builtin_ctzl", "__builtin_ctzll") and expr.args:
            self.gen_expr(expr.args[0])
            self.emit("    bsfq %rax, %rax")
            return

        is_indirect = not isinstance(expr.name, Identifier)
        is_fptr = False
        if isinstance(expr.name, Identifier):
            loc, ts = self.get_var_location(expr.name.name)
            if loc is not None and ts and ts.is_pointer():
                is_fptr = True

        num_args = len(expr.args)

        # Classify args as int, float, or struct (using param types and expr types)
        param_types = self.func_param_types.get(func_name, []) if func_name else []
        arg_is_float = []
        arg_is_struct = []  # True if arg is a struct passed by value
        arg_struct_size = []  # size of struct arg (0 if not struct)
        arg_needs_convert = []
        arg_is_long_double = []  # long double: stays on stack, not in registers

        for i, arg in enumerate(expr.args):
            at = self.get_expr_type(arg)
            # Check if param type or arg type is struct
            pt = param_types[i] if i < len(param_types) else None
            is_struct = False
            struct_size = 0
            if pt and self._is_struct_by_value(pt):
                is_struct = True
                struct_size = pt.size_bytes()
            elif at and self._is_struct_by_value(at):
                is_struct = True
                struct_size = at.size_bytes()

            if is_struct:
                arg_is_float.append(False)
                arg_is_struct.append(True)
                arg_struct_size.append(struct_size)
                arg_needs_convert.append(False)
                arg_is_long_double.append(False)
                continue

            # Check if long double: needs 16 bytes on stack (X87 class in ABI)
            is_long_dbl = (at and at.base == "long double" and not at.is_pointer())
            if not is_long_dbl and pt and pt.base == "long double" and not pt.is_pointer():
                is_long_dbl = True
            if is_long_dbl:
                # Treat like a 16-byte struct for passing purposes
                # But must stay on stack (X87 class), never in GP registers
                arg_is_float.append(False)
                arg_is_struct.append(True)
                arg_struct_size.append(16)
                arg_needs_convert.append(False)
                arg_is_long_double.append(True)
                continue

            is_flt = (at and at.base in ("float", "double") and
                      not at.is_pointer() and not at.is_array() and not (at.struct_def and at.pointer_depth == 0))
            if isinstance(arg, FloatLiteral):
                is_flt = True
            needs_conv = False
            if pt:
                param_is_float = (pt.base in ("float", "double")
                                  and not pt.is_pointer() and not pt.is_array()
                                  and not (pt.struct_def and pt.pointer_depth == 0))
                if param_is_float and not is_flt:
                    needs_conv = True
                    is_flt = True
                elif not param_is_float and is_flt:
                    needs_conv = True
                    is_flt = False
            arg_is_float.append(is_flt)
            arg_is_struct.append(False)
            arg_struct_size.append(0)
            arg_needs_convert.append(needs_conv)
            arg_is_long_double.append(False)

        # Count actual pushes and how many will be popped to registers.
        # This determines how many 8-byte words remain on the stack for the call.
        total_pushes = 0  # non-long-double pushes
        ld_pushes = 0  # long double pushes (always stay on stack)
        pop_count = 0  # how many words will be popped to registers
        int_idx_sim = 0  # simulate int register assignment
        xmm_idx_sim = 0
        for i in range(num_args):
            if arg_is_long_double[i]:
                ld_pushes += 2  # 16 bytes = 2 pushes
            elif arg_is_struct[i]:
                sz = arg_struct_size[i]
                if sz <= 8:
                    total_pushes += 1
                elif sz <= 16:
                    total_pushes += 2
                else:
                    total_pushes += 1  # pointer
            elif arg_is_float[i]:
                total_pushes += 1
            else:
                total_pushes += 1

        # Simulate pop to count how many words get popped
        int_idx_sim = 0
        xmm_idx_sim = 0
        for i in range(num_args):
            if arg_is_long_double[i]:
                continue
            elif arg_is_struct[i]:
                sz = arg_struct_size[i]
                if sz <= 8:
                    if int_idx_sim < 6:
                        pop_count += 1; int_idx_sim += 1
                    else:
                        break
                elif sz <= 16:
                    if int_idx_sim + 1 < 6:
                        pop_count += 2; int_idx_sim += 2
                    else:
                        break
                else:
                    if int_idx_sim < 6:
                        pop_count += 1; int_idx_sim += 1
                    else:
                        break
            elif arg_is_float[i]:
                if xmm_idx_sim < 8:
                    pop_count += 1; xmm_idx_sim += 1
                else:
                    break
            else:
                if int_idx_sim < 6:
                    pop_count += 1; int_idx_sim += 1
                else:
                    break

        remaining_on_stack = total_pushes - pop_count + ld_pushes
        if remaining_on_stack > 0 and remaining_on_stack % 2 != 0:
            self.emit("    subq $8, %rsp")

        # For indirect calls, save function pointer
        if is_indirect or is_fptr:
            if is_indirect:
                call_target = expr.name
                # Strip ONE level of * (C: *funcptr == funcptr)
                if isinstance(call_target, UnaryOp) and call_target.op == "*":
                    inner = call_target.operand
                    inner_type = self.get_expr_type(inner)
                    if (inner_type and inner_type.is_pointer() and inner_type.pointer_depth >= 2
                            and not inner_type.is_func_ptr):
                        # Pointer-to-function-pointer: need full dereference
                        self.gen_expr(call_target)
                    else:
                        # Function pointer (possibly typedef'd): *fp == fp, just load it
                        self.gen_expr(inner)
                else:
                    self.gen_expr(call_target)
            else:
                self.gen_load_var(func_name, expr.line, expr.col)
            self.emit("    pushq %rax")

        # Phase 1: Push long double args (they stay on the stack, last-to-first order)
        for idx in range(num_args - 1, -1, -1):
            if not arg_is_long_double[idx]:
                continue
            arg = expr.args[idx]
            self._push_struct_arg(arg, 16)

        # Phase 2: Push non-long-double args (will be popped to registers or stay as stack args)
        for idx in range(num_args - 1, -1, -1):
            if arg_is_long_double[idx]:
                continue  # already pushed
            arg = expr.args[idx]
            if arg_is_struct[idx]:
                self._push_struct_arg(arg, arg_struct_size[idx])
            else:
                self.gen_expr(arg)
                arg_type = self.get_expr_type(arg)
                pt = param_types[idx] if idx < len(param_types) else None
                if arg_needs_convert[idx]:
                    arg_actually_float = (arg_type and arg_type.base in ("float", "double", "long double")) or isinstance(arg, FloatLiteral)
                    if arg_actually_float and not arg_is_float[idx]:
                        # Float -> int: convert. Use 64-bit destination if param is wide.
                        self.emit("    movq %rax, %xmm0")
                        param_is_wide = (pt and (pt.base in ("long", "long long") or pt.is_pointer()))
                        if param_is_wide:
                            self.emit("    cvttsd2siq %xmm0, %rax")
                        else:
                            self.emit("    cvttsd2si %xmm0, %eax")
                            self.emit("    cltq")
                    elif not arg_actually_float and arg_is_float[idx]:
                        # Int -> float: convert. Use 64-bit source if arg is wide.
                        arg_is_wide = (arg_type and (arg_type.base in ("long", "long long") or arg_type.is_pointer()))
                        if arg_is_wide:
                            self.emit("    cvtsi2sdq %rax, %xmm0")
                        else:
                            self.emit("    cvtsi2sd %eax, %xmm0")
                        self.emit("    movq %xmm0, %rax")
                else:
                    # No float<->int convert needed, but may still need int width extension.
                    arg_is_narrow_int = (arg_type and not arg_is_float[idx] and not arg_is_struct[idx] and
                                         arg_type.base not in ("long", "long long") and
                                         not arg_type.is_pointer() and
                                         not arg_type.is_array())
                    param_is_wide_int = (pt and (pt.base in ("long", "long long") or pt.is_pointer()) and
                                         not (pt.base in ("float", "double", "long double") and not pt.is_pointer()))
                    if arg_is_narrow_int and param_is_wide_int:
                        if arg_type.is_unsigned:
                            self.emit("    movl %eax, %eax")  # zero-extend
                        else:
                            self.emit("    cltq")  # sign-extend
                self.emit("    pushq %rax")

        # Pop into registers (long doubles stay on stack)
        int_idx = 0
        xmm_idx = 0
        for i in range(num_args):
            if arg_is_long_double[i]:
                # Long double stays on stack - don't pop
                continue
            elif arg_is_struct[i]:
                sz = arg_struct_size[i]
                if sz <= 8:
                    if int_idx < 6:
                        self.emit(f"    popq {self.ARG_REGS_64[int_idx]}")
                        int_idx += 1
                elif sz <= 16:
                    if int_idx + 1 < 6:
                        self.emit(f"    popq {self.ARG_REGS_64[int_idx]}")
                        self.emit(f"    popq {self.ARG_REGS_64[int_idx + 1]}")
                        int_idx += 2
                    else:
                        break  # stays on stack
                else:
                    # >16 bytes: pointer in one int reg
                    if int_idx < 6:
                        self.emit(f"    popq {self.ARG_REGS_64[int_idx]}")
                        int_idx += 1
                    else:
                        break
            elif arg_is_float[i]:
                if xmm_idx < 8:
                    self.emit(f"    popq %rax")
                    self.emit(f"    movq %rax, %xmm{xmm_idx}")
                    xmm_idx += 1
                else:
                    break
            else:
                if int_idx < 6:
                    self.emit(f"    popq {self.ARG_REGS_64[int_idx]}")
                    int_idx += 1
                else:
                    break

        # For functions returning struct > 16 bytes, pass hidden pointer in %rdi
        # Shift other int args to the right
        ret_type = self.func_return_types.get(func_name) if func_name else None
        if ret_type is None:
            # Try to infer return type from function pointer type
            callee_type = self.get_expr_type(expr.name)
            if callee_type and callee_type.is_pointer():
                ret_type = TypeSpec(base=callee_type.base,
                                   pointer_depth=callee_type.pointer_depth - 1,
                                   is_unsigned=callee_type.is_unsigned,
                                   struct_def=callee_type.struct_def,
                                   enum_def=callee_type.enum_def)
        needs_hidden_ret_ptr = (ret_type and self._is_struct_by_value(ret_type)
                                and ret_type.size_bytes() > 16)
        hidden_ret_off = None
        if needs_hidden_ret_ptr:
            # Shift existing int regs: rdi->rsi, rsi->rdx, etc.
            for ri in range(min(int_idx, 5), 0, -1):
                self.emit(f"    movq {self.ARG_REGS_64[ri - 1]}, {self.ARG_REGS_64[ri]}")
            # If caller has reserved a destination for the struct return, use it
            preset_dest = getattr(self, '_struct_ret_dest', None)
            if preset_dest is not None:
                hidden_ret_off = preset_dest
                self._struct_ret_dest = None  # consume
            else:
                # Allocate temp space for the returned struct
                ret_size = ret_type.size_bytes()
                alloc = (ret_size + 15) & ~15
                self.stack_offset -= alloc
                hidden_ret_off = self.stack_offset
            self.emit(f"    leaq {hidden_ret_off}(%rbp), %rdi")

        # Set %al to number of xmm registers used (required for variadic calls)
        self.emit(f"    movl ${xmm_idx}, %eax")

        # For indirect calls, pop function pointer before alignment
        if is_indirect or is_fptr:
            self.emit("    popq %r11")

        # Align stack for call:
        # - For calls with stack args, use static alignment (padding before args)
        # - For calls with no stack args, dynamically align with andq
        use_dynamic_align = (remaining_on_stack == 0)
        if use_dynamic_align:
            self.emit("    movq %rsp, %rbx")
            self.emit("    andq $-16, %rsp")

        if is_indirect or is_fptr:
            self.emit("    call *%r11")
        else:
            self.emit(f"    call {func_name}")

        if use_dynamic_align:
            self.emit("    movq %rbx, %rsp")

        # If function returns float/double, move xmm0 to rax
        if ret_type and ret_type.base in ("float", "double", "long double") and not ret_type.is_pointer():
            if not (ret_type.struct_def and ret_type.pointer_depth == 0):
                self.emit("    movq %xmm0, %rax")

        # Clean up stack args and alignment padding
        if remaining_on_stack > 0:
            cleanup = remaining_on_stack * 8
            if remaining_on_stack % 2 != 0:
                cleanup += 8  # alignment padding
            self.emit(f"    addq ${cleanup}, %rsp")

    def _push_struct_arg(self, arg, sz):
        """Push a struct (or long double) argument onto the stack for a function call.
        Gets the address of the argument, then pushes sz bytes."""
        if isinstance(arg, Identifier):
            loc, vts = self.get_var_location(arg.name)
            if vts and vts.is_array():
                self.gen_lvalue_addr(arg)
            elif arg.name in self.locals or arg.name in self.params:
                offset = (self.locals.get(arg.name) or self.params.get(arg.name))[0]
                self.emit(f"    leaq {offset}(%rbp), %rax")
            elif arg.name in self.static_locals:
                mangled = self.static_locals[arg.name]
                self.emit(f"    leaq {mangled}(%rip), %rax")
            else:
                self.emit(f"    leaq {arg.name}(%rip), %rax")
        elif isinstance(arg, MemberAccess):
            # Member access (e.g., accessing a.a where a is a struct with long double)
            self.gen_member_addr(arg)
        else:
            self.gen_lvalue_addr(arg)

        if sz > 16:
            # Pass by hidden pointer
            self.emit(f"    pushq %rax")
        elif sz <= 8:
            self.emit(f"    movq (%rax), %rcx")
            self.emit(f"    pushq %rcx")
        else:
            # 9-16 bytes: push high word first (so low word ends up on top)
            self.emit(f"    movq 8(%rax), %rcx")
            self.emit(f"    pushq %rcx")
            self.emit(f"    movq (%rax), %rcx")
            self.emit(f"    pushq %rcx")

    def _gen_va_start(self, expr: FuncCall):
        """Generate code for __builtin_va_start(ap, last_named_param).
        AMD64 ABI va_list is an array of 1 struct (24 bytes):
          [0]  gp_offset (uint32) - offset in reg save area for next int arg
          [4]  fp_offset (uint32) - offset for next float arg (always 48 = no floats)
          [8]  overflow_arg_area (void*) - pointer to stack overflow args
          [16] reg_save_area (void*) - pointer to register save area
        va_list is passed as pointer to this struct (array decays to pointer).
        """
        if len(expr.args) < 2:
            return
        ap_arg = expr.args[0]

        if self.current_func and hasattr(self, '_va_area_offset'):
            named_int_slots = 0
            named_fp_slots = 0
            for p in self.current_func.params:
                if self._is_struct_by_value(p.type_spec):
                    sz = p.type_spec.size_bytes()
                    if sz <= 8: named_int_slots += 1
                    elif sz <= 16: named_int_slots += 2
                    else: named_int_slots += 1
                elif (p.type_spec.base in ("float", "double")
                      and not p.type_spec.is_pointer()):
                    named_fp_slots += 1
                elif (p.type_spec.base == "long double"
                      and not p.type_spec.is_pointer()):
                    pass  # long double is on stack, doesn't affect fp/gp
                else:
                    named_int_slots += 1

            # ap points to a 24-byte struct (va_list[0])
            # Get address of ap (which IS the struct, since va_list is array)
            self.gen_lvalue_addr(ap_arg)
            self.emit("    pushq %rax")  # save ap address

            # gp_offset = named_int_slots * 8 (offset into reg_save_area)
            gp_off = min(named_int_slots, 6) * 8
            self.emit("    popq %rcx")   # ap address
            self.emit("    pushq %rcx")  # save again
            self.emit(f"    movl ${gp_off}, (%rcx)")          # gp_offset

            # fp_offset = 48 + named_fp_slots * 16 (xmm portion starts at 48)
            fp_off = 48 + min(named_fp_slots, 8) * 16
            self.emit(f"    movl ${fp_off}, 4(%rcx)")         # fp_offset

            # overflow_arg_area = 16(%rbp) (first stack arg)
            self.emit(f"    leaq 16(%rbp), %rax")
            self.emit(f"    movq %rax, 8(%rcx)")              # overflow_arg_area

            # reg_save_area = va_area base
            self.emit(f"    leaq {self._va_area_offset}(%rbp), %rax")
            self.emit(f"    movq %rax, 16(%rcx)")             # reg_save_area

            self.emit("    popq %rcx")  # clean up
        else:
            self.gen_lvalue_addr(ap_arg)
            self.emit("    leaq 16(%rbp), %rcx")
            self.emit("    movq %rcx, (%rax)")

    def _gen_va_copy(self, expr: FuncCall):
        """Generate code for __builtin_va_copy(dest, src).
        Copy 24 bytes of AMD64 va_list struct from src to dest."""
        if len(expr.args) < 2:
            return

        # Get dest address
        self.gen_lvalue_addr(expr.args[0])
        self.emit("    pushq %rax")  # save dest

        # Get src address
        self.gen_lvalue_addr(expr.args[1])
        self.emit("    movq %rax, %rsi")  # src

        self.emit("    popq %rdi")        # dest
        # Copy 24 bytes
        self.emit("    movq (%rsi), %rcx")
        self.emit("    movq %rcx, (%rdi)")
        self.emit("    movq 8(%rsi), %rcx")
        self.emit("    movq %rcx, 8(%rdi)")
        self.emit("    movq 16(%rsi), %rcx")
        self.emit("    movq %rcx, 16(%rdi)")

    def _gen_builtin_va_arg(self, expr):
        """Generate code for __builtin_va_arg(ap, type).
        AMD64 ABI va_list struct:
          [0]  gp_offset (uint32) - current offset into reg_save_area
          [4]  fp_offset (uint32) - current offset for floats (unused)
          [8]  overflow_arg_area (void*) - next stack arg
          [16] reg_save_area (void*) - base of saved registers
        For each integer arg:
          if gp_offset < 48: read from reg_save_area + gp_offset, gp_offset += 8
          else: read from overflow_arg_area, overflow_arg_area += 8
        """
        target_type = expr.target_type
        size = target_type.size_bytes()
        aligned_size = (size + 7) & ~7
        is_struct = self._is_struct_by_value(target_type)
        is_fp = (target_type.base in ("float", "double") and
                 not target_type.is_pointer() and not target_type.is_array())
        slot_size = 8 if (is_struct and size > 16) else aligned_size

        # ap is va_list. For local va_list ap;, ap IS the struct (array decay).
        # For parameter va_list ap, ap is a pointer to the struct (param array decay).
        is_param_ap = (isinstance(expr.ap, Identifier) and
                       expr.ap.name in self.params)
        if is_param_ap:
            self.gen_expr(expr.ap)
            self.emit("    movq %rax, %r10")
        else:
            self.gen_lvalue_addr(expr.ap)
            self.emit("    movq %rax, %r10")

        use_overflow = self.new_label("va_overflow")
        va_done = self.new_label("va_done")

        if is_fp:
            # float/double: use fp_offset (limit 176 = 48 + 8*16)
            # fp_offset is at offset 4 in va_list struct
            self.emit(f"    movl 4(%r10), %eax")     # fp_offset
            self.emit(f"    cmpl $176, %eax")
            self.emit(f"    jae {use_overflow}")

            # Read from reg_save_area + fp_offset
            self.emit(f"    movl 4(%r10), %eax")
            self.emit(f"    movslq %eax, %rax")
            self.emit(f"    addq 16(%r10), %rax")
            self.emit(f"    pushq %rax")              # source address
            # Advance fp_offset by 16 (xmm slots are 16 bytes apart)
            self.emit(f"    movl 4(%r10), %eax")
            self.emit(f"    addl $16, %eax")
            self.emit(f"    movl %eax, 4(%r10)")
            self.emit(f"    jmp {va_done}")

            # Overflow: doubles on stack take 8 bytes
            self.label(use_overflow)
            self.emit(f"    movq 8(%r10), %rax")
            self.emit(f"    pushq %rax")
            self.emit(f"    addq $8, %rax")
            self.emit(f"    movq %rax, 8(%r10)")
            self.label(va_done)
            self.emit(f"    popq %r11")
            # Load double value
            if target_type.base == "float":
                self.emit("    movss (%r11), %xmm0")
                self.emit("    cvtss2sd %xmm0, %xmm0")
                self.emit("    movq %xmm0, %rax")
            else:
                self.emit("    movq (%r11), %rax")
            return

        # Integer/pointer/struct path
        gp_limit = 48 - slot_size + 8  # overflow when gp_offset >= this
        self.emit(f"    movl (%r10), %eax")
        self.emit(f"    cmpl ${gp_limit}, %eax")
        self.emit(f"    jae {use_overflow}")

        self.emit(f"    movl (%r10), %eax")
        self.emit(f"    movslq %eax, %rax")
        self.emit(f"    addq 16(%r10), %rax")
        self.emit(f"    pushq %rax")
        self.emit(f"    movl (%r10), %eax")
        self.emit(f"    addl ${slot_size}, %eax")
        self.emit(f"    movl %eax, (%r10)")
        self.emit(f"    jmp {va_done}")

        self.label(use_overflow)
        self.emit(f"    movq 8(%r10), %rax")
        self.emit(f"    pushq %rax")
        self.emit(f"    addq ${slot_size}, %rax")
        self.emit(f"    movq %rax, 8(%r10)")

        self.label(va_done)
        self.emit(f"    popq %r11")

        if is_struct:
            if size > 16:
                # >16 byte struct: source contains a pointer to the actual struct
                self.emit("    movq (%r11), %rax")
            else:
                # Struct <= 16 bytes: copy from source to temp
                alloc = (size + 7) & ~7
                self.stack_offset -= alloc
                temp_off = self.stack_offset
                for off in range(0, size, 8):
                    if off + 8 <= size:
                        self.emit(f"    movq {off}(%r11), %rax")
                        self.emit(f"    movq %rax, {temp_off + off}(%rbp)")
                    else:
                        for b in range(off, size):
                            self.emit(f"    movb {b}(%r11), %al")
                            self.emit(f"    movb %al, {temp_off + b}(%rbp)")
                self.emit(f"    leaq {temp_off}(%rbp), %rax")
        else:
            # Scalar type
            if size <= 4:
                self.emit("    movl (%r11), %eax")
            else:
                self.emit("    movq (%r11), %rax")

    def gen_ternary(self, expr: TernaryOp):
        false_label = self.new_label("tern_f")
        end_label = self.new_label("tern_e")

        # Check if one branch is float and the other is int (need promotion)
        true_type = self.get_expr_type(expr.true_expr)
        false_type = self.get_expr_type(expr.false_expr)
        true_is_float = (true_type and true_type.base in ("float", "double") and not true_type.is_pointer()) or isinstance(expr.true_expr, FloatLiteral)
        false_is_float = (false_type and false_type.base in ("float", "double") and not false_type.is_pointer()) or isinstance(expr.false_expr, FloatLiteral)
        needs_promote = true_is_float != false_is_float

        self.gen_expr(expr.condition)
        self._emit_cond_test(expr.condition)
        self.emit(f"    je {false_label}")
        self.gen_expr(expr.true_expr)
        if needs_promote and not true_is_float:
            # int -> double promotion for true branch
            self.emit("    cvtsi2sd %eax, %xmm0")
            self.emit("    movq %xmm0, %rax")
        self.emit(f"    jmp {end_label}")
        self.label(false_label)
        self.gen_expr(expr.false_expr)
        if needs_promote and not false_is_float:
            # int -> double promotion for false branch
            self.emit("    cvtsi2sd %eax, %xmm0")
            self.emit("    movq %xmm0, %rax")
        self.label(end_label)
