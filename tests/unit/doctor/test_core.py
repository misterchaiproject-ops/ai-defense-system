"""Tests for doctor.core."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from doctor.__main__ import main


@pytest.fixture
def healthy_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A temp root simulating a healthy project, isolated from system HOME."""
    fake_home = tmp_path / "fake_home"
    fake_home.mkdir()
    monkeypatch.setenv("HOME", str(fake_home))

    precommit_cache = fake_home / ".cache" / "pre-commit"
    precommit_cache.mkdir(parents=True)

    lock = tmp_path / "uv.lock"
    pyproj = tmp_path / "pyproject.toml"
    lock.write_text("# dummy lock\n")
    pyproj.write_text("[project]\nname = 'x'\n")

    return tmp_path


class TestDoctorCLI:
    """Tests for doctor.__main__ CLI entry point."""

    @patch("doctor.core._uv_lock_is_synced")
    def test_main_healthy_root_returns_zero(self, mock_uv_sync: Mock, healthy_root: Path) -> None:
        """A healthy root exits with code 0."""
        mock_uv_sync.return_value = True
        (healthy_root / ".cache").mkdir(exist_ok=True)
        assert main(["--root", str(healthy_root)]) == 0

    def test_main_missing_lock_returns_one(self, tmp_path: Path) -> None:
        """Missing uv.lock causes non-zero exit."""
        assert main(["--root", str(tmp_path)]) == 1

    def test_main_output_contains_report_header(
        self, healthy_root: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """CLI prints the report header."""
        with patch("doctor.core._uv_lock_is_synced", return_value=True):
            main(["--root", str(healthy_root)])
        out = capsys.readouterr().out
        assert "AI Defense System: Environment Doctor" in out
        assert "SUMMARY:" in out

    def test_main_fix_triggers_cleanup(
        self, healthy_root: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """--fix removes stale caches and prints CLEANUP line."""
        with patch("doctor.core._uv_lock_is_synced", return_value=True):
            (healthy_root / ".pytest_cache").mkdir()
            (healthy_root / ".mypy_cache").mkdir()
            main(["--root", str(healthy_root), "--fix"])
            out = capsys.readouterr().out
            assert "CLEANUP:" in out
            assert not (healthy_root / ".pytest_cache").exists()
            assert not (healthy_root / ".mypy_cache").exists()

    def test_main_no_fix_does_not_cleanup(self, healthy_root: Path) -> None:
        """Without --fix, caches are preserved."""
        with patch("doctor.core._uv_lock_is_synced", return_value=True):
            (healthy_root / ".pytest_cache").mkdir()
            main(["--root", str(healthy_root)])
            assert (healthy_root / ".pytest_cache").exists()
