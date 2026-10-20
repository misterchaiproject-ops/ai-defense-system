"""Core diagnostics for environment health."""

from __future__ import annotations

import os
import shutil
import subprocess  # nosec B404
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

Status = Literal["OK", "STALE", "ERROR"]

_EXPECTED_PYTHON = (3, 12)
_WATCHED_DIRS = ("src", "tests", "scripts")
_CACHE_DIRS = (".pytest_cache", ".hypothesis", ".mypy_cache", ".ruff_cache")


@dataclass(frozen=True, slots=True)
class CheckResult:
    """Immutable result of a single doctor check."""

    name: str
    status: Status
    detail: str


def check_python_version() -> CheckResult:
    """Verify running interpreter matches project baseline."""
    current = sys.version_info[:2]
    detail = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if current == _EXPECTED_PYTHON:
        return CheckResult("python_version", "OK", detail)
    expected = f"{_EXPECTED_PYTHON[0]}.{_EXPECTED_PYTHON[1]}"
    return CheckResult(
        "python_version",
        "ERROR",
        f"expected {expected}, got {detail}",
    )


def _uv_lock_is_synced(root: Path) -> bool:
    """Run 'uv lock --check' and return True if in sync.

    Fail-Closed: any subprocess error is treated as out-of-sync (STALE).
    """
    uv = shutil.which("uv")
    if uv is None:
        return False
    try:
        # S603: args is a fixed list (no shell), uv resolved via shutil.which.
        result = subprocess.run(  # nosec B603
            [uv, "lock", "--check"],
            cwd=root,
            capture_output=True,
            timeout=10,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


def check_uv_lock(root: Path) -> CheckResult:
    """Verify uv.lock exists and is in sync with pyproject.toml."""
    lock = root / "uv.lock"

    if not lock.exists():
        return CheckResult("uv_lock", "ERROR", "uv.lock not found")

    if _uv_lock_is_synced(root):
        return CheckResult("uv_lock", "OK", "lock is in sync")

    return CheckResult(
        "uv_lock",
        "STALE",
        "lock is out of sync (run: uv lock)",
    )


def check_precommit_cache() -> CheckResult:
    """Verify pre-commit cache directory exists."""
    home = Path(os.environ.get("HOME", str(Path.home())))
    cache = home / ".cache" / "pre-commit"
    if cache.is_dir():
        return CheckResult("precommit_cache", "OK", "cache present")
    return CheckResult(
        "precommit_cache",
        "ERROR",
        "cache missing (run: pre-commit install)",
    )


def check_caches(root: Path) -> CheckResult:
    """Report presence of local build caches."""
    stale = [d for d in _CACHE_DIRS if (root / d).is_dir()]
    if not stale:
        return CheckResult("caches", "OK", "no stale caches")
    return CheckResult(
        "caches",
        "STALE",
        f"{len(stale)} stale cache(s): {', '.join(stale)}",
    )


def check_orphan_bak(root: Path) -> CheckResult:
    """Detect orphan .bak files in watched source directories."""
    found: list[Path] = []
    for sub in _WATCHED_DIRS:
        watched = root / sub
        if watched.is_dir():
            found.extend(watched.rglob("*.bak"))
    if not found:
        return CheckResult("orphan_bak", "OK", "no orphan .bak files")
    return CheckResult(
        "orphan_bak",
        "ERROR",
        f"{len(found)} orphan .bak file(s) found",
    )


def run_all(root: Path) -> list[CheckResult]:
    """Run all checks in a fixed order."""
    return [
        check_python_version(),
        check_uv_lock(root),
        check_precommit_cache(),
        check_caches(root),
        check_orphan_bak(root),
    ]


def cleanup_caches(root: Path) -> int:
    """Remove stale cache directories. Returns count removed."""
    removed = 0
    for d in _CACHE_DIRS:
        target = root / d
        if target.is_dir():
            shutil.rmtree(target)
            removed += 1
    return removed


def format_report(results: list[CheckResult]) -> str:
    """Format check results as a human-readable report."""
    lines: list[str] = []
    lines.append("=== AI Defense System: Environment Doctor ===")
    lines.append("")

    total = len(results)
    for i, r in enumerate(results, 1):
        lines.append(f"[{i}/{total}] {r.name:<20} {r.status} ({r.detail})")

    ok = sum(1 for r in results if r.status == "OK")
    stale = sum(1 for r in results if r.status == "STALE")
    errors = sum(1 for r in results if r.status == "ERROR")

    lines.append("")
    lines.append(f"SUMMARY: {ok} OK, {stale} STALE, {errors} ERRORS")
    return "\n".join(lines)
