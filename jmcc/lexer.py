"""JMCC Lexer - Tokenizes C11 source code."""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional
from .errors import LexError


class TokenType(Enum):
    # Literals
    INT_LITERAL = auto()
    CHAR_LITERAL = auto()
    STRING_LITERAL = auto()
    FLOAT_LITERAL = auto()

    # Identifiers and keywords
    IDENTIFIER = auto()

    # Keywords
    AUTO = auto()
    BREAK = auto()
    CASE = auto()
    CHAR = auto()
    CONST = auto()
    CONTINUE = auto()
    DEFAULT = auto()
    DO = auto()
    DOUBLE = auto()
    ELSE = auto()
    ENUM = auto()
    EXTERN = auto()
    FLOAT = auto()
    FOR = auto()
    GOTO = auto()
    IF = auto()
    INLINE = auto()
    INT = auto()
    LONG = auto()
    REGISTER = auto()
    RESTRICT = auto()
    RETURN = auto()
    SHORT = auto()
    SIGNED = auto()
    SIZEOF = auto()
    STATIC = auto()
    STRUCT = auto()
    SWITCH = auto()
    TYPEDEF = auto()
    UNION = auto()
    UNSIGNED = auto()
    VOID = auto()
    VOLATILE = auto()
    WHILE = auto()
    # C11 keywords
    ALIGNAS = auto()    # _Alignas
    ALIGNOF = auto()    # _Alignof
    ATOMIC = auto()     # _Atomic
    BOOL = auto()       # _Bool
    COMPLEX = auto()    # _Complex
    GENERIC = auto()    # _Generic
    IMAGINARY = auto()  # _Imaginary
    NORETURN = auto()   # _Noreturn
    STATIC_ASSERT = auto()  # _Static_assert
    THREAD_LOCAL = auto()   # _Thread_local

    # Punctuation
    LPAREN = auto()     # (
    RPAREN = auto()     # )
    LBRACE = auto()     # {
    RBRACE = auto()     # }
    LBRACKET = auto()   # [
    RBRACKET = auto()   # ]
    SEMICOLON = auto()  # ;
    COMMA = auto()      # ,
    DOT = auto()        # .
    ARROW = auto()      # ->
    ELLIPSIS = auto()   # ...

    # Operators
    PLUS = auto()       # +
    MINUS = auto()      # -
    STAR = auto()       # *
    SLASH = auto()      # /
    PERCENT = auto()    # %
    AMP = auto()        # &
    PIPE = auto()       # |
    CARET = auto()      # ^
    TILDE = auto()      # ~
    BANG = auto()        # !
    ASSIGN = auto()     # =
    LT = auto()         # <
    GT = auto()         # >
    QUESTION = auto()   # ?
    COLON = auto()      # :

    # Compound operators
    PLUS_ASSIGN = auto()    # +=
    MINUS_ASSIGN = auto()   # -=
    STAR_ASSIGN = auto()    # *=
    SLASH_ASSIGN = auto()   # /=
    PERCENT_ASSIGN = auto() # %=
    AMP_ASSIGN = auto()     # &=
    PIPE_ASSIGN = auto()    # |=
    CARET_ASSIGN = auto()   # ^=
    LSHIFT_ASSIGN = auto()  # <<=
    RSHIFT_ASSIGN = auto()  # >>=
    EQ = auto()             # ==
    NE = auto()             # !=
    LE = auto()             # <=
    GE = auto()             # >=
    AND = auto()            # &&
    OR = auto()             # ||
    LSHIFT = auto()         # <<
    RSHIFT = auto()         # >>
    INC = auto()            # ++
    DEC = auto()            # --

    # Special
    EOF = auto()
    HASH = auto()       # # (for preprocessor)
    HASH_HASH = auto()  # ## (token paste)


KEYWORDS = {
    "auto": TokenType.AUTO,
    "break": TokenType.BREAK,
    "case": TokenType.CASE,
    "char": TokenType.CHAR,
    "const": TokenType.CONST,
    "continue": TokenType.CONTINUE,
    "default": TokenType.DEFAULT,
    "do": TokenType.DO,
    "double": TokenType.DOUBLE,
    "else": TokenType.ELSE,
    "enum": TokenType.ENUM,
    "extern": TokenType.EXTERN,
    "float": TokenType.FLOAT,
    "for": TokenType.FOR,
    "goto": TokenType.GOTO,
    "if": TokenType.IF,
    "inline": TokenType.INLINE,
    "int": TokenType.INT,
    "long": TokenType.LONG,
    "register": TokenType.REGISTER,
    "restrict": TokenType.RESTRICT,
    "return": TokenType.RETURN,
    "short": TokenType.SHORT,
    "signed": TokenType.SIGNED,
    "sizeof": TokenType.SIZEOF,
    "static": TokenType.STATIC,
    "struct": TokenType.STRUCT,
    "switch": TokenType.SWITCH,
    "typedef": TokenType.TYPEDEF,
    "union": TokenType.UNION,
    "unsigned": TokenType.UNSIGNED,
    "void": TokenType.VOID,
    "volatile": TokenType.VOLATILE,
    "while": TokenType.WHILE,
    "_Alignas": TokenType.ALIGNAS,
    "_Alignof": TokenType.ALIGNOF,
    "_Atomic": TokenType.ATOMIC,
    "_Bool": TokenType.BOOL,
    "_Complex": TokenType.COMPLEX,
    "_Generic": TokenType.GENERIC,
    "_Imaginary": TokenType.IMAGINARY,
    "_Noreturn": TokenType.NORETURN,
    "_Static_assert": TokenType.STATIC_ASSERT,
    "_Thread_local": TokenType.THREAD_LOCAL,
}


@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    col: int
    filename: str = ""

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.col})"


class Lexer:
    def __init__(self, source: str, filename: str = "<stdin>"):
        self.source = source
        self.filename = filename
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens: List[Token] = []

    def error(self, msg):
        raise LexError(msg, self.filename, self.line, self.col)

    def peek(self) -> Optional[str]:
        if self.pos < len(self.source):
            return self.source[self.pos]
        return None

    def peek_ahead(self, n=1) -> Optional[str]:
        pos = self.pos + n
        if pos < len(self.source):
            return self.source[pos]
        return None

    def advance(self) -> str:
        ch = self.source[self.pos]
        self.pos += 1
        if ch == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def match(self, expected: str) -> bool:
        if self.pos < len(self.source) and self.source[self.pos] == expected:
            self.advance()
            return True
        return False

    def skip_whitespace(self):
        while self.pos < len(self.source) and self.source[self.pos] in ' \t\r\n\f\v':
            self.advance()

    def skip_line_comment(self):
        while self.pos < len(self.source) and self.source[self.pos] != '\n':
            self.advance()

    def skip_block_comment(self):
        while self.pos < len(self.source):
            if self.source[self.pos] == '*' and self.peek_ahead() == '/':
                self.advance()  # *
                self.advance()  # /
                return
            self.advance()
        self.error("unterminated block comment")

    def read_string(self) -> str:
        result = []
        while self.pos < len(self.source):
            ch = self.source[self.pos]
            if ch == '"':
                self.advance()
                return ''.join(result)
            if ch == '\\':
                self.advance()
                result.append(self.read_escape())
            elif ch == '\n':
                self.error("unterminated string literal")
            else:
                result.append(ch)
                self.advance()
        self.error("unterminated string literal")

    def read_char(self) -> str:
        if self.pos >= len(self.source):
            self.error("unterminated character literal")
        ch = self.source[self.pos]
        if ch == '\\':
            self.advance()
            val = self.read_escape()
        elif ch == '\'':
            self.error("empty character literal")
        else:
            val = ch
            self.advance()
        if self.pos >= len(self.source) or self.source[self.pos] != '\'':
            self.error("unterminated character literal")
        self.advance()  # closing '
        return val

    def read_escape(self) -> str:
        if self.pos >= len(self.source):
            self.error("unterminated escape sequence")
        ch = self.advance()
        escapes = {
            'n': '\n', 't': '\t', 'r': '\r', '\\': '\\',
            '\'': '\'', '"': '"', '0': '\0', 'a': '\a',
            'b': '\b', 'f': '\f', 'v': '\v', '?': '?',
        }
        if ch in escapes:
            return escapes[ch]
        if ch == 'x':
            # Hex escape
            digits = []
            while self.pos < len(self.source) and self.source[self.pos] in '0123456789abcdefABCDEF':
                digits.append(self.advance())
            if not digits:
                self.error("expected hex digit in escape sequence")
            return chr(int(''.join(digits), 16))
        if ch in '01234567':
            # Octal escape
            digits = [ch]
            for _ in range(2):
                if self.pos < len(self.source) and self.source[self.pos] in '01234567':
                    digits.append(self.advance())
            return chr(int(''.join(digits), 8))
        self.error(f"unknown escape sequence '\\{ch}'")

    def read_number(self, first_char: str) -> Token:
        start_line = self.line
        start_col = self.col - 1  # already advanced past first char
        result = [first_char]
        is_float = False

        # Hex
        if first_char == '0' and self.pos < len(self.source) and self.source[self.pos] in 'xX':
            result.append(self.advance())
            while self.pos < len(self.source) and self.source[self.pos] in '0123456789abcdefABCDEF':
                result.append(self.advance())
        # Octal or decimal
        else:
            while self.pos < len(self.source) and self.source[self.pos] in '0123456789':
                result.append(self.advance())
            # Float: decimal point
            if self.pos < len(self.source) and self.source[self.pos] == '.':
                is_float = True
                result.append(self.advance())
                while self.pos < len(self.source) and self.source[self.pos] in '0123456789':
                    result.append(self.advance())
            # Float: exponent
            if self.pos < len(self.source) and self.source[self.pos] in 'eE':
                is_float = True
                result.append(self.advance())
                if self.pos < len(self.source) and self.source[self.pos] in '+-':
                    result.append(self.advance())
                while self.pos < len(self.source) and self.source[self.pos] in '0123456789':
                    result.append(self.advance())

        # Suffixes
        if is_float:
            if self.pos < len(self.source) and self.source[self.pos] in 'fFlL':
                result.append(self.advance())
            return Token(TokenType.FLOAT_LITERAL, ''.join(result), start_line, start_col, self.filename)
        else:
            while self.pos < len(self.source) and self.source[self.pos] in 'uUlL':
                result.append(self.advance())
            return Token(TokenType.INT_LITERAL, ''.join(result), start_line, start_col, self.filename)

    def read_identifier(self, first_char: str) -> Token:
        start_line = self.line
        start_col = self.col - 1
        result = [first_char]
        while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == '_'):
            result.append(self.advance())
        word = ''.join(result)
        tt = KEYWORDS.get(word, TokenType.IDENTIFIER)
        return Token(tt, word, start_line, start_col, self.filename)

    def tokenize(self) -> List[Token]:
        tokens = []

        while self.pos < len(self.source):
            # Skip whitespace
            if self.source[self.pos] in ' \t\r\n\f\v':
                self.skip_whitespace()
                continue

            # Comments
            if self.source[self.pos] == '/' and self.peek_ahead() == '/':
                self.advance()
                self.advance()
                self.skip_line_comment()
                continue
            if self.source[self.pos] == '/' and self.peek_ahead() == '*':
                self.advance()
                self.advance()
                self.skip_block_comment()
                continue

            start_line = self.line
            start_col = self.col
            ch = self.advance()

            # String literal
            if ch == '"':
                val = self.read_string()
                tokens.append(Token(TokenType.STRING_LITERAL, val, start_line, start_col, self.filename))
                continue

            # Char literal
            if ch == '\'':
                val = self.read_char()
                tokens.append(Token(TokenType.CHAR_LITERAL, val, start_line, start_col, self.filename))
                continue

            # Numbers
            if ch.isdigit():
                tokens.append(self.read_number(ch))
                continue

            # Dot (could be float like .5, or struct member, or ellipsis)
            if ch == '.':
                if self.pos < len(self.source) and self.source[self.pos].isdigit():
                    tokens.append(self.read_number(ch))
                    continue
                if self.match('.'):
                    if self.match('.'):
                        tokens.append(Token(TokenType.ELLIPSIS, "...", start_line, start_col, self.filename))
                    else:
                        self.error("unexpected '..'")
                else:
                    tokens.append(Token(TokenType.DOT, ".", start_line, start_col, self.filename))
                continue

            # Identifiers and keywords
            if ch.isalpha() or ch == '_':
                tokens.append(self.read_identifier(ch))
                continue

            # Operators and punctuation
            def tok(tt, val):
                tokens.append(Token(tt, val, start_line, start_col, self.filename))

            if ch == '(':
                tok(TokenType.LPAREN, "(")
            elif ch == ')':
                tok(TokenType.RPAREN, ")")
            elif ch == '{':
                tok(TokenType.LBRACE, "{")
            elif ch == '}':
                tok(TokenType.RBRACE, "}")
            elif ch == '[':
                tok(TokenType.LBRACKET, "[")
            elif ch == ']':
                tok(TokenType.RBRACKET, "]")
            elif ch == ';':
                tok(TokenType.SEMICOLON, ";")
            elif ch == ',':
                tok(TokenType.COMMA, ",")
            elif ch == '~':
                tok(TokenType.TILDE, "~")
            elif ch == '?':
                tok(TokenType.QUESTION, "?")
            elif ch == ':':
                tok(TokenType.COLON, ":")
            elif ch == '#':
                if self.match('#'):
                    tok(TokenType.HASH_HASH, "##")
                else:
                    tok(TokenType.HASH, "#")
            elif ch == '+':
                if self.match('+'):
                    tok(TokenType.INC, "++")
                elif self.match('='):
                    tok(TokenType.PLUS_ASSIGN, "+=")
                else:
                    tok(TokenType.PLUS, "+")
            elif ch == '-':
                if self.match('-'):
                    tok(TokenType.DEC, "--")
                elif self.match('='):
                    tok(TokenType.MINUS_ASSIGN, "-=")
                elif self.match('>'):
                    tok(TokenType.ARROW, "->")
                else:
                    tok(TokenType.MINUS, "-")
            elif ch == '*':
                if self.match('='):
                    tok(TokenType.STAR_ASSIGN, "*=")
                else:
                    tok(TokenType.STAR, "*")
            elif ch == '/':
                if self.match('='):
                    tok(TokenType.SLASH_ASSIGN, "/=")
                else:
                    tok(TokenType.SLASH, "/")
            elif ch == '%':
                if self.match('='):
                    tok(TokenType.PERCENT_ASSIGN, "%=")
                else:
                    tok(TokenType.PERCENT, "%")
            elif ch == '&':
                if self.match('&'):
                    tok(TokenType.AND, "&&")
                elif self.match('='):
                    tok(TokenType.AMP_ASSIGN, "&=")
                else:
                    tok(TokenType.AMP, "&")
            elif ch == '|':
                if self.match('|'):
                    tok(TokenType.OR, "||")
                elif self.match('='):
                    tok(TokenType.PIPE_ASSIGN, "|=")
                else:
                    tok(TokenType.PIPE, "|")
            elif ch == '^':
                if self.match('='):
                    tok(TokenType.CARET_ASSIGN, "^=")
                else:
                    tok(TokenType.CARET, "^")
            elif ch == '!':
                if self.match('='):
                    tok(TokenType.NE, "!=")
                else:
                    tok(TokenType.BANG, "!")
            elif ch == '=':
                if self.match('='):
                    tok(TokenType.EQ, "==")
                else:
                    tok(TokenType.ASSIGN, "=")
            elif ch == '<':
                if self.match('<'):
                    if self.match('='):
                        tok(TokenType.LSHIFT_ASSIGN, "<<=")
                    else:
                        tok(TokenType.LSHIFT, "<<")
                elif self.match('='):
                    tok(TokenType.LE, "<=")
                else:
                    tok(TokenType.LT, "<")
            elif ch == '>':
                if self.match('>'):
                    if self.match('='):
                        tok(TokenType.RSHIFT_ASSIGN, ">>=")
                    else:
                        tok(TokenType.RSHIFT, ">>")
                elif self.match('='):
                    tok(TokenType.GE, ">=")
                else:
                    tok(TokenType.GT, ">")
            else:
                self.error(f"unexpected character '{ch}'")

        tokens.append(Token(TokenType.EOF, "", self.line, self.col, self.filename))
        return tokens
