"""Tests for doctor.core."""

from __future__ import annotations

import dataclasses
import os
from pathlib import Path

import pytest

from doctor.core import (
    CheckResult,
    check_caches,
    check_orphan_bak,
    check_precommit_cache,
    check_python_version,
    check_uv_lock,
    run_all,
)


@pytest.fixture
def healthy_root(tmp_path: Path) -> Path:
    """A temp root simulating a healthy project."""
    lock = tmp_path / "uv.lock"
    pyproj = tmp_path / "pyproject.toml"
    lock.write_text("version = 1\n")
    pyproj.write_text("[project]\nname = 'x'\n")
    # lock must be newer than pyproject
    os.utime(pyproj, (1000, 1000))
    os.utime(lock, (2000, 2000))
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
    """Tests for check_uv_lock."""

    def test_ok_when_lock_is_newer(self, healthy_root: Path) -> None:
        """uv.lock newer than pyproject.toml -> OK."""
        result = check_uv_lock(healthy_root)
        assert result.status == "OK"

    def test_error_when_lock_missing(self, tmp_path: Path) -> None:
        """Missing uv.lock -> ERROR."""
        (tmp_path / "pyproject.toml").write_text("x")
        result = check_uv_lock(tmp_path)
        assert result.status == "ERROR"
        assert "uv.lock" in result.detail.lower()

    def test_stale_when_pyproject_newer(self, tmp_path: Path) -> None:
        """pyproject newer than uv.lock -> STALE."""
        lock = tmp_path / "uv.lock"
        pyproj = tmp_path / "pyproject.toml"
        lock.write_text("x")
        pyproj.write_text("y")
        os.utime(lock, (1000, 1000))
        os.utime(pyproj, (2000, 2000))
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
