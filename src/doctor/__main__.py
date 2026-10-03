"""CLI entry point: uv run python -m doctor."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from doctor.core import cleanup_caches, format_report, run_all


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="doctor",
        description="Diagnose AI Defense System environment health.",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Remove stale caches after diagnosis.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Project root (default: current directory).",
    )
    args = parser.parse_args(argv)

    results = run_all(args.root)
    print(format_report(results))

    if args.fix:
        removed = cleanup_caches(args.root)
        print()
        label = "directory" if removed == 1 else "directories"
        print(f"CLEANUP: removed {removed} cache {label}")

    errors = sum(1 for r in results if r.status == "ERROR")
    return 1 if errors > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
