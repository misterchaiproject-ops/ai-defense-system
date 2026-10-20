"""Tests for doctor.core."""

from __future__ import annotations

import dataclasses
import os
from pathlib import Path

import pytest

from doctor.__main__ import main
from doctor.core import (
    CheckResult,
    check_caches,
    check_orphan_bak,
    check_precommit_cache,
    check_python_version,
    check_uv_lock,
    cleanup_caches,
    run_all,
)


@pytest.fixture
def healthy_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A temp root simulating a healthy project."""
    lock = tmp_path / "uv.lock"
    pyproj = tmp_path / "pyproject.toml"
    lock.write_text("version = 1\n")
    pyproj.write_text("[project]\nname = 'x'\n")
    # Keep the fixture deterministic: the Doctor's external checks are
    # represented as healthy without depending on the host environment.
    os.utime(pyproj, (1000, 1000))
    os.utime(lock, (2000, 2000))
    monkeypatch.setattr("doctor.core._uv_lock_is_synced", lambda root: True)
    monkeypatch.setenv("HOME", str(tmp_path))
    (tmp_path / ".cache" / "pre-commit").mkdir(parents=True)
    return tmp_path


class TestCheckPythonVersion:
    """Tests for check_python_version."""

    def test_ok_on_python_312(self) -> None:
        """Current interpreter is 3.12 -> OK."""
        result = check_python_version()
        assert result.name == "python_version"
        assert result.status == "OK"
        assert "3.12" in result.detail

    def test_check_result_is_frozen(self) -> None:
        """CheckResult is immutable."""
        r = CheckResult(name="x", status="OK", detail="y")
        with pytest.raises(dataclasses.FrozenInstanceError):
            r.name = "z"  # type: ignore[misc]


class TestCheckUvLock:
    """Tests for check_uv_lock (subprocess-based, no mtime)."""

    def test_ok_when_lock_is_synced(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """In-sync lock returns OK."""
        (tmp_path / "uv.lock").write_text("version = 1\n")
        monkeypatch.setattr(
            "doctor.core._uv_lock_is_synced",
            lambda root: True,
        )
        result = check_uv_lock(tmp_path)
        assert result.name == "uv_lock"
        assert result.status == "OK"

    def test_error_when_lock_missing(self, tmp_path: Path) -> None:
        """Missing uv.lock -> ERROR."""
        (tmp_path / "pyproject.toml").write_text("x")
        result = check_uv_lock(tmp_path)
        assert result.status == "ERROR"
        assert "uv.lock" in result.detail.lower()

    def test_stale_when_out_of_sync(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Out-of-sync lock (subprocess returns non-zero) -> STALE."""
        (tmp_path / "uv.lock").write_text("version = 1\n")
        monkeypatch.setattr(
            "doctor.core._uv_lock_is_synced",
            lambda root: False,
        )
        result = check_uv_lock(tmp_path)
        assert result.status == "STALE"
        assert "uv lock" in result.detail.lower()

    def test_stale_when_uv_missing(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """uv not found in PATH -> STALE (fail-closed)."""
        (tmp_path / "uv.lock").write_text("version = 1\n")

        monkeypatch.setattr("doctor.core.shutil.which", lambda name: None)
        result = check_uv_lock(tmp_path)
        assert result.status == "STALE"

    def test_stale_when_uv_timeout(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """TimeoutExpired from subprocess -> STALE (fail-closed)."""
        import subprocess

        (tmp_path / "uv.lock").write_text("version = 1\n")

        def raise_timeout(*args: object, **kwargs: object) -> None:
            raise subprocess.TimeoutExpired(cmd="uv", timeout=10)

        monkeypatch.setattr("doctor.core.subprocess.run", raise_timeout)
        result = check_uv_lock(tmp_path)
        assert result.status == "STALE"


class TestCheckPrecommitCache:
    """Tests for check_precommit_cache."""

    def test_error_when_cache_missing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Missing pre-commit cache -> ERROR."""
        monkeypatch.setenv("HOME", str(tmp_path))
        result = check_precommit_cache()
        assert result.status == "ERROR"

    def test_ok_when_cache_exists(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Existing pre-commit cache -> OK."""
        monkeypatch.setenv("HOME", str(tmp_path))
        (tmp_path / ".cache" / "pre-commit").mkdir(parents=True)
        result = check_precommit_cache()
        assert result.status == "OK"


class TestCheckCaches:
    """Tests for check_caches."""

    def test_ok_when_no_cache_dirs(self, tmp_path: Path) -> None:
        """No cache dirs -> OK."""
        result = check_caches(tmp_path)
        assert result.status == "OK"

    def test_stale_when_pytest_cache_exists(self, tmp_path: Path) -> None:
        """pytest_cache present -> STALE."""
        (tmp_path / ".pytest_cache").mkdir()
        result = check_caches(tmp_path)
        assert result.status == "STALE"

    def test_stale_reports_count(self, tmp_path: Path) -> None:
        """STALE detail reports number of stale caches."""
        (tmp_path / ".pytest_cache").mkdir()
        (tmp_path / ".hypothesis").mkdir()
        (tmp_path / ".mypy_cache").mkdir()
        result = check_caches(tmp_path)
        assert result.status == "STALE"
        assert "3" in result.detail


class TestCheckOrphanBak:
    """Tests for check_orphan_bak."""

    def test_ok_when_no_bak(self, tmp_path: Path) -> None:
        """Clean src/ -> OK."""
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "x.py").write_text("x")
        result = check_orphan_bak(tmp_path)
        assert result.status == "OK"

    def test_error_when_bak_in_src(self, tmp_path: Path) -> None:
        """.bak in src/ -> ERROR."""
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "x.py.bak").write_text("x")
        result = check_orphan_bak(tmp_path)
        assert result.status == "ERROR"

    def test_ignores_bak_outside_watched_dirs(self, tmp_path: Path) -> None:
        """.bak in docs/ is ignored."""
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "x.md.bak").write_text("x")
        result = check_orphan_bak(tmp_path)
        assert result.status == "OK"


class TestRunAll:
    """Tests for run_all."""

    def test_returns_five_results(self, tmp_path: Path) -> None:
        """run_all returns exactly 5 CheckResult items."""
        results = run_all(tmp_path)
        assert len(results) == 5

    def test_returns_check_result_instances(self, tmp_path: Path) -> None:
        """Every result is a CheckResult."""
        results = run_all(tmp_path)
        assert all(isinstance(r, CheckResult) for r in results)


class TestDoctorCLI:
    """Tests for doctor.__main__ CLI entry point."""

    def test_main_healthy_root_returns_zero(self, healthy_root: Path) -> None:
        """A healthy root exits with code 0."""
        assert main(["--root", str(healthy_root)]) == 0

    def test_main_missing_lock_returns_one(self, tmp_path: Path) -> None:
        """Missing uv.lock causes non-zero exit."""
        assert main(["--root", str(tmp_path)]) == 1

    def test_main_output_contains_report_header(
        self, healthy_root: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """CLI prints the report header."""
        main(["--root", str(healthy_root)])
        out = capsys.readouterr().out
        assert "AI Defense System: Environment Doctor" in out
        assert "SUMMARY:" in out

    def test_main_fix_triggers_cleanup(
        self, healthy_root: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """--fix removes stale caches and prints CLEANUP line."""
        (healthy_root / ".pytest_cache").mkdir()
        (healthy_root / ".mypy_cache").mkdir()
        main(["--root", str(healthy_root), "--fix"])
        out = capsys.readouterr().out
        assert "CLEANUP:" in out
        assert not (healthy_root / ".pytest_cache").exists()
        assert not (healthy_root / ".mypy_cache").exists()

    def test_main_no_fix_does_not_cleanup(self, healthy_root: Path) -> None:
        """Without --fix, caches are preserved."""
        (healthy_root / ".pytest_cache").mkdir()
        main(["--root", str(healthy_root)])
        assert (healthy_root / ".pytest_cache").exists()

    def test_main_fix_reports_singular(
        self, healthy_root: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """--fix reports '1 cache directory' (singular)."""
        (healthy_root / ".pytest_cache").mkdir()
        main(["--root", str(healthy_root), "--fix"])
        out = capsys.readouterr().out
        assert "1 cache directory" in out
        assert "directories" not in out.split("CLEANUP:")[1].split("\n")[0]

    def test_main_fix_reports_plural(
        self, healthy_root: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """--fix reports 'N cache directories' (plural)."""
        (healthy_root / ".pytest_cache").mkdir()
        (healthy_root / ".mypy_cache").mkdir()
        main(["--root", str(healthy_root), "--fix"])
        out = capsys.readouterr().out
        assert "2 cache directories" in out

    def test_main_help_raises_system_exit(self) -> None:
        """--help triggers argparse SystemExit(0)."""
        with pytest.raises(SystemExit) as exc:
            main(["--help"])
        assert exc.value.code == 0


def test_check_orphan_bak_detected(tmp_path: Path) -> None:
    src_dir = tmp_path / "src"
    src_dir.mkdir(parents=True, exist_ok=True)
    bak_file = src_dir / "vulnerable_code.py.bak"
    bak_file.touch()
    result = check_orphan_bak(tmp_path)
    assert result.status == "ERROR"
    assert "orphan .bak file" in result.detail


def test_check_orphan_bak_clean(tmp_path: Path) -> None:
    src_dir = tmp_path / "src"
    src_dir.mkdir(parents=True, exist_ok=True)
    result = check_orphan_bak(tmp_path)
    assert result.status == "OK"
    assert "no orphan .bak files" in result.detail


def test_cleanup_caches_removes_stale_folders(tmp_path: Path) -> None:
    pytest_cache = tmp_path / ".pytest_cache"
    mypy_cache = tmp_path / ".mypy_cache"
    pytest_cache.mkdir()
    mypy_cache.mkdir()
    removed_count = cleanup_caches(tmp_path)
    assert removed_count >= 2
    assert not pytest_cache.exists()
    assert not mypy_cache.exists()
