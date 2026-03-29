"""JMCC error types and reporting."""


class JMCCError(Exception):
    """Base error for all JMCC errors."""
    def __init__(self, message, filename=None, line=None, col=None):
        self.message = message
        self.filename = filename
        self.line = line
        self.col = col
        super().__init__(self.format())

    def format(self):
        loc = ""
        if self.filename:
            loc = f"{self.filename}:"
        if self.line is not None:
            loc += f"{self.line}:"
        if self.col is not None:
            loc += f"{self.col}:"
        if loc:
            loc += " "
        return f"{loc}error: {self.message}"


class LexError(JMCCError):
    pass


class ParseError(JMCCError):
    pass


class SemanticError(JMCCError):
    pass


class CodeGenError(JMCCError):
    pass
