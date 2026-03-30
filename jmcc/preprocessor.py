"""JMCC Preprocessor - Handles #include, #define, #ifdef, etc."""

import os
import re
from typing import Dict, List, Optional, Set, Tuple
from .errors import JMCCError


class PreprocessorError(JMCCError):
    pass


class Preprocessor:
    """Simple C preprocessor.

    Handles:
    - #include "file" and #include <file> (with search paths)
    - #define NAME value (object-like macros)
    - #define NAME(args) body (function-like macros)
    - #undef NAME
    - #ifdef / #ifndef / #if / #elif / #else / #endif
    - #error
    - #pragma (ignored)
    - #line (ignored)
    - Predefined macros: __LINE__, __FILE__, __DATE__, __TIME__
    - ## (token paste) and # (stringify) in function-like macros
    """

    # Built-in freestanding headers that JMCC provides
    BUILTIN_HEADERS = {
        "stddef.h": """
typedef long ptrdiff_t;
typedef unsigned long size_t;
#define NULL ((void*)0)
#define offsetof(type, member) __builtin_offsetof(type, member)
""",
        "stdint.h": """
typedef signed char int8_t;
typedef short int16_t;
typedef int int32_t;
typedef long int64_t;
typedef unsigned char uint8_t;
typedef unsigned short uint16_t;
typedef unsigned int uint32_t;
typedef unsigned long uint64_t;
typedef long intptr_t;
typedef unsigned long uintptr_t;
typedef long intmax_t;
typedef unsigned long uintmax_t;
#define INT8_MIN (-128)
#define INT8_MAX 127
#define INT16_MIN (-32768)
#define INT16_MAX 32767
#define INT32_MIN (-2147483647-1)
#define INT32_MAX 2147483647
#define INT64_MIN (-9223372036854775807L-1)
#define INT64_MAX 9223372036854775807L
#define UINT8_MAX 255
#define UINT16_MAX 65535
#define UINT32_MAX 4294967295U
#define UINT64_MAX 18446744073709551615UL
""",
        "stdbool.h": """
#define bool _Bool
#define true 1
#define false 0
""",
        "stdarg.h": """
typedef void *va_list;
#define va_start(ap, param) __builtin_va_start(ap, param)
#define va_end(ap) __builtin_va_end(ap)
#define va_arg(ap, type) __builtin_va_arg(ap, type)
#define va_copy(dest, src) __builtin_va_copy(dest, src)
""",
        "limits.h": """
#define CHAR_BIT 8
#define SCHAR_MIN (-128)
#define SCHAR_MAX 127
#define UCHAR_MAX 255
#define CHAR_MIN (-128)
#define CHAR_MAX 127
#define SHRT_MIN (-32768)
#define SHRT_MAX 32767
#define USHRT_MAX 65535
#define INT_MIN (-2147483647-1)
#define INT_MAX 2147483647
#define UINT_MAX 4294967295U
#define LONG_MIN (-9223372036854775807L-1)
#define LONG_MAX 9223372036854775807L
#define ULONG_MAX 18446744073709551615UL
#define LLONG_MIN (-9223372036854775807LL-1)
#define LLONG_MAX 9223372036854775807LL
#define ULLONG_MAX 18446744073709551615ULL
""",
        "stdnoreturn.h": """
#define noreturn _Noreturn
""",
        "stdalign.h": """
#define alignas _Alignas
#define alignof _Alignof
""",
        "float.h": """
#define FLT_RADIX 2
#define FLT_MIN 1.17549435e-38F
#define FLT_MAX 3.40282347e+38F
#define FLT_EPSILON 1.19209290e-07F
#define DBL_MIN 2.2250738585072014e-308
#define DBL_MAX 1.7976931348623157e+308
#define DBL_EPSILON 2.2204460492503131e-16
""",
        "stdio.h": """
#ifndef _JMCC_STDIO_H
#define _JMCC_STDIO_H
typedef void FILE;
#define SEEK_SET 0
#define SEEK_CUR 1
#define SEEK_END 2
#define BUFSIZ 8192
#endif
""",
        "stdlib.h": """
#ifndef _JMCC_STDLIB_H
#define _JMCC_STDLIB_H
#define EXIT_SUCCESS 0
#define EXIT_FAILURE 1
#define RAND_MAX 2147483647
#endif
""",
        "string.h": """
""",
    }

    def __init__(self, filename: str = "<stdin>", include_paths: List[str] = None):
        self.filename = filename
        self.include_paths = include_paths or []
        self.macros: Dict[str, 'Macro'] = {}
        self.included_files: Set[str] = set()

        # Predefined macros
        import time
        now = time.localtime()
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        self.macros["__STDC__"] = Macro("__STDC__", body="1")
        self.macros["__STDC_VERSION__"] = Macro("__STDC_VERSION__", body="201112L")
        self.macros["__STDC_HOSTED__"] = Macro("__STDC_HOSTED__", body="1")
        self.macros["__JMCC__"] = Macro("__JMCC__", body="1")
        self.macros["__x86_64__"] = Macro("__x86_64__", body="1")
        self.macros["__linux__"] = Macro("__linux__", body="1")
        self.macros["NULL"] = Macro("NULL", body="((void*)0)")
        self.macros["EOF"] = Macro("EOF", body="(-1)")
        self.macros["__LP64__"] = Macro("__LP64__", body="1")

    def preprocess(self, source: str, filename: str = None) -> str:
        if filename:
            self.filename = filename
        # Phase 2: splice lines (backslash-newline removal)
        source = source.replace('\\\n', '')
        lines = source.split('\n')
        output = []
        self._process_lines(lines, output, filename or self.filename)
        return '\n'.join(output)

    def _process_lines(self, lines: List[str], output: List[str],
                       filename: str, if_stack: List[dict] = None):
        if if_stack is None:
            if_stack = []

        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # Check if we're in a disabled #if branch
            active = all(frame["active"] for frame in if_stack)

            if stripped.startswith('#'):
                directive = self._parse_directive(stripped)
                cmd = directive[0] if directive else ""

                if cmd in ("ifdef", "ifndef", "if"):
                    if cmd == "ifdef":
                        cond = directive[1] in self.macros if len(directive) > 1 else False
                    elif cmd == "ifndef":
                        cond = directive[1] not in self.macros if len(directive) > 1 else True
                    elif cmd == "if":
                        if active:
                            cond = self._eval_if_expr(' '.join(directive[1:]))
                        else:
                            cond = False
                    if_stack.append({
                        "active": active and cond,
                        "any_taken": cond,
                        "parent_active": active,
                    })
                    output.append("")  # blank line to preserve line numbers
                elif cmd == "elif":
                    if not if_stack:
                        output.append("")
                    else:
                        frame = if_stack[-1]
                        if frame["parent_active"] and not frame["any_taken"]:
                            cond = self._eval_if_expr(' '.join(directive[1:]))
                            frame["active"] = cond
                            if cond:
                                frame["any_taken"] = True
                        else:
                            frame["active"] = False
                    output.append("")
                elif cmd == "else":
                    if if_stack:
                        frame = if_stack[-1]
                        if frame["parent_active"] and not frame["any_taken"]:
                            frame["active"] = True
                            frame["any_taken"] = True
                        else:
                            frame["active"] = False
                    output.append("")
                elif cmd == "endif":
                    if if_stack:
                        if_stack.pop()
                    output.append("")
                elif not active:
                    output.append("")
                elif cmd == "define":
                    self._handle_define(' '.join(directive[1:]), stripped)
                    output.append("")
                elif cmd == "undef":
                    if len(directive) > 1:
                        self.macros.pop(directive[1], None)
                    output.append("")
                elif cmd == "include":
                    included = self._handle_include(stripped, filename)
                    if included:
                        inc_lines = included.split('\n')
                        self._process_lines(inc_lines, output, filename, if_stack)
                    else:
                        output.append("")
                elif cmd == "error":
                    msg = ' '.join(directive[1:])
                    raise PreprocessorError(f"#error {msg}", filename)
                elif cmd in ("pragma", "line"):
                    output.append("")  # ignore
                else:
                    output.append("")
            elif active:
                # Regular line — expand macros
                expanded = self._expand_macros(line)
                output.append(expanded)
            else:
                output.append("")

            i += 1

    def _parse_directive(self, line: str) -> List[str]:
        """Parse a preprocessor directive into parts."""
        # Remove leading #
        line = line.lstrip()
        if line.startswith('#'):
            line = line[1:].strip()
        parts = line.split(None, 1)
        if not parts:
            return [""]
        cmd = parts[0]
        if len(parts) > 1:
            return [cmd] + parts[1].split()
        return [cmd]

    def _handle_define(self, rest: str, full_line: str):
        """Handle #define directive."""
        # Function-like macro: #define NAME(a, b) body
        # Object-like macro: #define NAME value
        rest = rest.strip()
        if not rest:
            return

        # Check for function-like macro (no space before paren)
        match = re.match(r'(\w+)\(([^)]*)\)\s*(.*)', rest)
        if match:
            name = match.group(1)
            params = [p.strip() for p in match.group(2).split(',') if p.strip()]
            body = match.group(3).strip()
            # Handle variadic macros: ... as last param
            is_variadic = False
            if params and params[-1] == '...':
                params.pop()
                is_variadic = True
            elif params and params[-1].endswith('...'):
                params[-1] = params[-1][:-3].strip()
                is_variadic = True
            self.macros[name] = Macro(name, params=params, body=body,
                                       is_func=True, is_variadic=is_variadic)
            return

        # Object-like macro
        parts = rest.split(None, 1)
        name = parts[0]
        body = parts[1].strip() if len(parts) > 1 else ""
        self.macros[name] = Macro(name, body=body)

    def _handle_include(self, line: str, current_file: str) -> Optional[str]:
        """Handle #include directive, return included content."""
        # Extract filename
        match = re.search(r'#\s*include\s*[<"]([^>"]+)[>"]', line)
        if not match:
            return None

        inc_name = match.group(1)
        is_system = '<' in line.split('include')[1]

        # Check builtin headers first
        if inc_name in self.BUILTIN_HEADERS:
            return self.BUILTIN_HEADERS[inc_name]

        # For system headers we don't have, just skip silently
        # (the actual declarations will be provided by the user as forward decls)
        if is_system:
            return ""

        # For quoted includes, search relative to current file
        if current_file and current_file != "<stdin>":
            dir_path = os.path.dirname(current_file)
            full = os.path.join(dir_path, inc_name)
            if os.path.exists(full):
                if full in self.included_files:
                    return ""  # already included
                self.included_files.add(full)
                with open(full) as f:
                    return f.read()

        # Search include paths
        for path in self.include_paths:
            full = os.path.join(path, inc_name)
            if os.path.exists(full):
                if full in self.included_files:
                    return ""
                self.included_files.add(full)
                with open(full) as f:
                    return f.read()

        return ""

    def _expand_macros(self, line: str, depth=0) -> str:
        """Expand macros in a line of text."""
        if not self.macros or depth > 20:
            return line

        # Don't expand inside string literals or comments
        result = []
        i = 0
        in_string = False
        in_char = False
        string_char = None

        while i < len(line):
            ch = line[i]

            # String/char literal passthrough
            if ch == '"' and not in_char:
                if in_string and string_char == '"':
                    in_string = False
                elif not in_string:
                    in_string = True
                    string_char = '"'
                result.append(ch)
                i += 1
                continue
            if ch == "'" and not in_string:
                if in_char:
                    in_char = False
                else:
                    in_char = True
                result.append(ch)
                i += 1
                continue
            if ch == '\\' and (in_string or in_char):
                result.append(ch)
                i += 1
                if i < len(line):
                    result.append(line[i])
                    i += 1
                continue
            if in_string or in_char:
                result.append(ch)
                i += 1
                continue

            # Line comment
            if ch == '/' and i + 1 < len(line) and line[i + 1] == '/':
                result.append(line[i:])
                break

            # Try to match identifier for macro expansion
            if ch.isalpha() or ch == '_':
                j = i
                while j < len(line) and (line[j].isalnum() or line[j] == '_'):
                    j += 1
                word = line[i:j]

                if word in self.macros:
                    macro = self.macros[word]
                    if macro.is_func:
                        # Function-like macro — look for (args)
                        k = j
                        while k < len(line) and line[k] in ' \t':
                            k += 1
                        if k < len(line) and line[k] == '(':
                            args, end = self._parse_macro_args(line, k)
                            # Pre-expand args (unless used with ## in the body)
                            if '##' not in macro.body:
                                args = [self._expand_macros(a) for a in args]
                            expanded = macro.expand(args)
                            expanded = self._expand_macros(expanded)  # recursive
                            result.append(expanded)
                            i = end
                            continue
                        # No parens — don't expand function-like macro
                        result.append(word)
                        i = j
                        continue
                    else:
                        expanded = macro.body
                        expanded = self._expand_macros(expanded)
                        result.append(expanded)
                        i = j
                        continue
                else:
                    result.append(word)
                    i = j
                    continue

            result.append(ch)
            i += 1

        final = ''.join(result)
        # Re-scan: if expansion changed the line and there are still macros, re-expand
        if final != line and depth < 20:
            return self._expand_macros(final, depth + 1)
        return final

    def _parse_macro_args(self, line: str, start: int) -> Tuple[List[str], int]:
        """Parse macro arguments starting from '('. Returns (args, end_pos)."""
        assert line[start] == '('
        i = start + 1
        depth = 1
        args = []
        current = []

        while i < len(line) and depth > 0:
            ch = line[i]
            if ch == '(':
                depth += 1
                current.append(ch)
            elif ch == ')':
                depth -= 1
                if depth == 0:
                    args.append(''.join(current).strip())
                    i += 1
                    break
                current.append(ch)
            elif ch == ',' and depth == 1:
                args.append(''.join(current).strip())
                current = []
            else:
                current.append(ch)
            i += 1

        return args, i

    def _eval_if_expr(self, expr: str) -> bool:
        """Evaluate a simple #if expression."""
        # Handle defined(NAME) and defined NAME
        expr = re.sub(r'defined\s*\(\s*(\w+)\s*\)',
                       lambda m: '1' if m.group(1) in self.macros else '0', expr)
        expr = re.sub(r'defined\s+(\w+)',
                       lambda m: '1' if m.group(1) in self.macros else '0', expr)

        # Expand macros in the expression
        expr = self._expand_macros(expr)

        # Replace remaining identifiers with 0 (per C standard)
        expr = re.sub(r'\b[a-zA-Z_]\w*\b', '0', expr)

        # Simple evaluation
        try:
            # Safe eval with only integer ops
            expr = expr.replace('&&', ' and ').replace('||', ' or ').replace('!', ' not ')
            result = eval(expr, {"__builtins__": {}}, {})
            return bool(result)
        except Exception:
            return False


class Macro:
    def __init__(self, name: str, params: List[str] = None,
                 body: str = "", is_func: bool = False,
                 is_variadic: bool = False):
        self.name = name
        self.params = params or []
        self.body = body
        self.is_func = is_func
        self.is_variadic = is_variadic

    def expand(self, args: List[str] = None) -> str:
        if not self.is_func:
            return self.body

        args = args or []
        result = self.body

        # Build param->arg mapping
        param_map = {}
        for i, param in enumerate(self.params):
            if i < len(args):
                param_map[param] = args[i]

        # Handle __VA_ARGS__ for variadic macros
        if self.is_variadic:
            va_args = ', '.join(args[len(self.params):])
            param_map['__VA_ARGS__'] = va_args

        # First: replace all params with placeholders to avoid partial matches
        markers = {}
        all_params = list(self.params)
        if self.is_variadic:
            all_params.append('__VA_ARGS__')
        for i, param in enumerate(all_params):
            markers[param] = f"\x01PARAM{i}\x02"

        # Replace params with markers (whole word)
        temp = result
        for param, marker in markers.items():
            temp = re.sub(r'\b' + re.escape(param) + r'\b', marker, temp)

        # Handle ## (token paste): remove ## and join adjacent markers
        temp = re.sub(r'\s*##\s*', '', temp)

        # Handle # (stringify): #MARKER -> "arg"
        for param, marker in markers.items():
            if param in param_map:
                arg = param_map[param]
                temp = temp.replace('#' + marker,
                    '"' + arg.replace('\\', '\\\\').replace('"', '\\"') + '"')

        # Replace remaining markers with args
        for param, marker in markers.items():
            if param in param_map:
                temp = temp.replace(marker, param_map[param])

        return temp
