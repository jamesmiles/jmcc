"""Backend dispatch for JMCC code generation."""

from typing import Optional

from .codegen_arm64_apple import Arm64AppleCodeGen
from .codegen_x86_64_linux import X86_64LinuxCodeGen
from .errors import CodeGenError
from .targets import TargetSpec, resolve_target


class CodeGen:
    """Dispatch to the selected backend implementation."""

    def __init__(self, target: Optional[TargetSpec | str] = None):
        self.target = resolve_target(target)
        backend = self.target.backend_name
        if backend == "x86_64_linux":
            self._backend = X86_64LinuxCodeGen(self.target)
        elif backend == "arm64_apple_darwin":
            self._backend = Arm64AppleCodeGen(self.target)
        else:
            raise CodeGenError(f"code generation for target '{self.target.triple}' is not implemented")

    def generate(self, program):
        return self._backend.generate(program)
