#!/usr/bin/env python3
"""JMCC - A C11 compiler targeting x86-64 Linux."""

import sys
import argparse
from jmcc.lexer import Lexer
from jmcc.parser import Parser
from jmcc.codegen import CodeGen
from jmcc.errors import JMCCError


def compile_file(source_path: str, output_path: str) -> bool:
    """Compile a C source file to x86-64 assembly."""
    try:
        with open(source_path, "r") as f:
            source = f.read()
    except FileNotFoundError:
        print(f"jmcc: error: no such file: '{source_path}'", file=sys.stderr)
        return False

    try:
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
    args = parser.parse_args()

    success = compile_file(args.input, args.output)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
