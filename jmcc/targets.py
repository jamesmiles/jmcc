"""Target selection and metadata for JMCC."""

from dataclasses import dataclass
from .target_layout import ARM64_APPLE_DARWIN_LAYOUT, X86_64_LINUX_LAYOUT, TargetLayout


@dataclass(frozen=True)
class TargetSpec:
    """Describes a compiler target."""

    triple: str
    arch: str
    vendor: str
    system: str
    abi: str
    object_format: str
    backend_name: str
    is_implemented: bool
    layout: TargetLayout


DEFAULT_TARGET_TRIPLE = "x86_64-linux"

_SUPPORTED_TARGETS = {
    "x86_64-linux": TargetSpec(
        triple="x86_64-linux",
        arch="x86_64",
        vendor="unknown",
        system="linux",
        abi="sysv",
        object_format="elf",
        backend_name="x86_64_linux",
        is_implemented=True,
        layout=X86_64_LINUX_LAYOUT,
    ),
    "arm64-apple-darwin": TargetSpec(
        triple="arm64-apple-darwin",
        arch="arm64",
        vendor="apple",
        system="darwin",
        abi="aapcs64",
        object_format="macho",
        backend_name="arm64_apple_darwin",
        is_implemented=True,
        layout=ARM64_APPLE_DARWIN_LAYOUT,
    ),
}

_TARGET_ALIASES = {
    "amd64-linux": "x86_64-linux",
    "x86_64-linux-gnu": "x86_64-linux",
    "x86_64-unknown-linux-gnu": "x86_64-linux",
    "aarch64-apple-darwin": "arm64-apple-darwin",
    "arm64-darwin": "arm64-apple-darwin",
}


def supported_target_names() -> list[str]:
    """Return the supported canonical target names."""
    return sorted(_SUPPORTED_TARGETS.keys())


def resolve_target(target: TargetSpec | str | None) -> TargetSpec:
    """Resolve a target name or alias to a canonical target spec."""
    if isinstance(target, TargetSpec):
        return target
    if target is None:
        canonical = DEFAULT_TARGET_TRIPLE
    else:
        normalized = target.strip().lower()
        canonical = _TARGET_ALIASES.get(normalized, normalized)

    if canonical not in _SUPPORTED_TARGETS:
        supported = ", ".join(supported_target_names())
        raise ValueError(f"unknown target '{target}' (supported targets: {supported})")

    return _SUPPORTED_TARGETS[canonical]
