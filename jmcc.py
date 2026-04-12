#!/usr/bin/env python3
"""JMCC - A C11 compiler targeting x86-64 Linux."""

import sys
import os
import argparse
from jmcc.lexer import Lexer
from jmcc.parser import Parser
from jmcc.codegen import CodeGen
from jmcc.preprocessor import Preprocessor, Macro
from jmcc.errors import JMCCError


def compile_file(source_path: str, output_path: str, defines: list = None, include_paths: list = None) -> bool:
    """Compile a C source file to x86-64 assembly."""
    try:
        with open(source_path, "r") as f:
            source = f.read()
    except FileNotFoundError:
        print(f"jmcc: error: no such file: '{source_path}'", file=sys.stderr)
        return False

    try:
        # Preprocessing
        source_dir = os.path.dirname(os.path.abspath(source_path))
        inc_paths = [source_dir]
        # Also search helpers/ subdirectory if it exists
        helpers_dir = os.path.join(source_dir, "helpers")
        if os.path.isdir(helpers_dir):
            inc_paths.append(helpers_dir)
        # Add user-specified include paths
        for p in (include_paths or []):
            abs_p = os.path.abspath(p)
            if abs_p not in inc_paths:
                inc_paths.append(abs_p)
        include_paths = inc_paths
        pp = Preprocessor(filename=source_path, include_paths=include_paths)
        # Apply -D defines
        for d in (defines or []):
            if '=' in d:
                name, value = d.split('=', 1)
                pp.macros[name] = Macro(name, body=value)
            else:
                pp.macros[d] = Macro(d, body="1")
        source = pp.preprocess(source, filename=source_path)

        # Lexing
        lexer = Lexer(source, filename=source_path)
        tokens = lexer.tokenize()

        # Parsing
        parser = Parser(tokens, filename=source_path)
        program = parser.parse_program()

        # Code generation
        codegen = CodeGen()
        assembly = codegen.generate(program)

        # Write output
        with open(output_path, "w") as f:
            f.write(assembly)

        return True

    except JMCCError as e:
        print(e.format(), file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="JMCC C Compiler")
    parser.add_argument("input", help="Input C source file")
    parser.add_argument("-o", "--output", default="output.s",
                        help="Output assembly file (default: output.s)")
    parser.add_argument("-D", action="append", default=[], dest="defines",
                        help="Define preprocessor macro (-DNAME or -DNAME=VALUE)")
    parser.add_argument("-I", action="append", default=[], dest="include_paths",
                        help="Add directory to include search path")
    args = parser.parse_args()

    success = compile_file(args.input, args.output, defines=args.defines,
                           include_paths=args.include_paths)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
