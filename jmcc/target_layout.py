"""Target-dependent layout and ABI facts."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TargetLayout:
    """Basic target-dependent type and ABI properties."""

    pointer_size: int
    enum_size: int
    long_double_size: int
    max_scalar_align: int
    stack_alignment: int
    global_symbol_prefix: str = ""


X86_64_LINUX_LAYOUT = TargetLayout(
    pointer_size=8,
    enum_size=4,
    long_double_size=16,
    max_scalar_align=8,
    stack_alignment=16,
    global_symbol_prefix="",
)

ARM64_APPLE_DARWIN_LAYOUT = TargetLayout(
    pointer_size=8,
    enum_size=4,
    long_double_size=8,
    max_scalar_align=8,
    stack_alignment=16,
    global_symbol_prefix="_",
)
