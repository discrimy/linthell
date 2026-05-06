"""Tests for pre-commit subcommands."""

import tempfile
from pathlib import Path

from click.testing import CliRunner

from linthell import cli


def test_precommit_available():
    """Verify pre-commit command exists (pre-commit is a required dev dependency)."""
    runner = CliRunner()
    result = runner.invoke(cli, ["pre-commit", "--help"])
    assert result.exit_code == 0
    assert "lint" in result.output
    assert "baseline" in result.output


def test_precommit_lint_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["pre-commit", "lint", "--help"])
    assert result.exit_code == 0
    assert "--linter-command" in result.output
    assert "--baseline" in result.output


def test_precommit_baseline_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["pre-commit", "baseline", "--help"])
    assert result.exit_code == 0
    assert "--hook-name" in result.output
    assert "--linter-command" in result.output


def test_precommit_lint_requires_linter_command():
    runner = CliRunner()
    bl_file = Path(tempfile.mktemp(suffix=".txt"))
    try:
        result = runner.invoke(
            cli,
            ["pre-commit", "lint", "--baseline", str(bl_file)],
        )
        assert result.exit_code != 0
    finally:
        bl_file.unlink(missing_ok=True)
