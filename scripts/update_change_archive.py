#!/usr/bin/env python3
"""Generate the human-readable change archive from Git history.

Git history remains authoritative. This script creates a deterministic Markdown
summary so the project has a searchable engineering/security change record.
Archive commits are excluded to prevent recursive entries.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "CHANGELOG.md"
ARCHIVE_SUBJECT = "docs: update automated change archive"


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def build_archive() -> str:
    raw = git(
        "log",
        "--reverse",
        "--date=short",
        "--format=%H%x09%ad%x09%an%x09%s",
    )
    entries: list[str] = []

    for line in raw.splitlines():
        sha, date, author, subject = line.split("\t", 3)
        if subject == ARCHIVE_SUBJECT or subject.startswith("docs: update automated change archive"):
            continue

        files_raw = git("show", "--format=", "--name-status", sha)
        files = [
            item.strip()
            for item in files_raw.splitlines()
            if item.strip()
        ]

        entries.append(f"### {date} — `{sha[:12]}` — {subject}")
        entries.append(f"- Author: {author}")
        if files:
            entries.append("- Files changed:")
            entries.extend(f"  - `{item}`" for item in files)
        else:
            entries.append("- Files changed: none reported")
        entries.append("")

    history = "\n".join(entries).rstrip()
    if not history:
        history = "_No non-archive commits have been recorded._"

    return f"""# AI Defense System — Change Archive

This file is the canonical human-readable archive of repository changes.

## Archive policy

- Git history is the authoritative immutable record of every commit.
- This file provides a searchable engineering/security summary of the commit history.
- The GitHub Actions workflow regenerates it automatically after pushes to `main`.
- Archive-update commits are excluded to prevent recursive entries.
- Unmerged work remains represented by its branch and pull request until it reaches `main`.

## Change history

{history}
"""


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(build_archive(), encoding="utf-8")


if __name__ == "__main__":
    main()
