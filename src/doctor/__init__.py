"""Doctor: environment health diagnostics."""

from doctor.core import (
    CheckResult,
    check_caches,
    check_orphan_bak,
    check_precommit_cache,
    check_python_version,
    check_uv_lock,
    cleanup_caches,
    format_report,
    run_all,
)

__all__ = [
    "CheckResult",
    "check_caches",
    "check_orphan_bak",
    "check_precommit_cache",
    "check_python_version",
    "check_uv_lock",
    "cleanup_caches",
    "format_report",
    "run_all",
]
