"""Security and determinism tests for the change-archive generator."""

from __future__ import annotations

import shutil
import subprocess

import pytest

from scripts import update_change_archive as archive


def test_git_uses_resolved_executable_argument_vector_and_fixed_root(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Git is invoked as an argument vector without a shell."""
    captured: dict[str, object] = {}
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/git")

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        captured["command"] = command
        captured.update(kwargs)
        return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    archive.git("log", "--format=%s", "; echo should-not-run")

    assert captured["command"] == [
        "/usr/bin/git",
        "log",
        "--format=%s",
        "; echo should-not-run",
    ]
    assert captured["cwd"] == archive.ROOT
    assert captured["shell"] is False
    assert captured["check"] is True
    assert captured["capture_output"] is True
    assert captured["text"] is True


def test_git_fails_closed_when_executable_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(shutil, "which", lambda name: None)

    with pytest.raises(RuntimeError, match="git executable not found"):
        archive.git("status")


def test_git_propagates_nonzero_exit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/git")

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        raise subprocess.CalledProcessError(1, command)

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(subprocess.CalledProcessError):
        archive.git("status")


def test_archive_is_deterministic_and_excludes_archive_commits(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw_history = (
        "abc123\t2026-10-20\tAlice\tfeat: add a feature\n"
        "def456\t2026-10-20\tBot\tdocs: update automated change archive\n"
    )

    def fake_git(*args: str) -> str:
        if args[0] == "log":
            return raw_history
        if args[0] == "show" and args[-1] == "abc123":
            return "M\tsrc/example.py\n"
        raise AssertionError(f"Unexpected Git invocation: {args!r}")

    monkeypatch.setattr(archive, "git", fake_git)

    first = archive.build_archive()
    second = archive.build_archive()

    assert first == second
    assert "feat: add a feature" in first
    assert "src/example.py" in first
    assert "def456" not in first
    assert "docs: update automated change archive" not in first


def test_empty_history_has_explicit_placeholder(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(archive, "git", lambda *args: "")

    assert "No non-archive commits" in archive.build_archive()
