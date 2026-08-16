"""End-to-end tests for the pre-commit commands.

Builds a real git repo with a real pre-commit config and runs the
pre-commit baseline/lint commands against a real flake8 invocation.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

from linthell import cli

HOOK_NAME = "linthell-flake8"


@pytest.fixture
def precommit_repo(tmp_path: Path):
    (tmp_path / "sample.py").write_text("import x_unknown_module_12345\n")
    (tmp_path / ".pre-commit-config.yaml").write_text(
        "repos:\n"
        "  - repo: local\n"
        "    hooks:\n"
        f"      - id: {HOOK_NAME}\n"
        f"        name: {HOOK_NAME}\n"
        "        language: system\n"
        "        entry: flake8\n"
        "        types: [python]\n"
    )
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=linthell-test",
            "-c",
            "user.email=t@t",
            "commit",
            "-m",
            "init",
        ],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    original_dir = os.getcwd()
    os.chdir(tmp_path)
    try:
        yield tmp_path
    finally:
        os.chdir(original_dir)


def _linter_command() -> str:
    return f'"{sys.executable}" -m flake8'


def test_precommit_baseline_e2e(precommit_repo: Path):
    bl_file = precommit_repo / "baseline.txt"
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "pre-commit",
            "baseline",
            "--baseline",
            str(bl_file),
            "--plugin-name",
            "flake8",
            "--linter-command",
            _linter_command(),
            "--hook-name",
            HOOK_NAME,
        ],
    )
    assert result.exit_code == 0, result.output
    assert bl_file.exists()
    assert "F401" in bl_file.read_text()


def test_precommit_lint_filters_known_error(precommit_repo: Path):
    bl_file = precommit_repo / "baseline.txt"
    runner = CliRunner()
    runner.invoke(
        cli,
        [
            "pre-commit",
            "baseline",
            "--baseline",
            str(bl_file),
            "--plugin-name",
            "flake8",
            "--linter-command",
            _linter_command(),
            "--hook-name",
            HOOK_NAME,
        ],
    )
    result = runner.invoke(
        cli,
        [
            "pre-commit",
            "lint",
            "--baseline",
            str(bl_file),
            "--plugin-name",
            "flake8",
            "--linter-command",
            _linter_command(),
            "sample.py",
        ],
    )
    assert result.exit_code == 0, result.output
    assert result.output == ""


def test_precommit_lint_detects_new_error(precommit_repo: Path):
    bl_file = precommit_repo / "baseline.txt"
    runner = CliRunner()
    runner.invoke(
        cli,
        [
            "pre-commit",
            "baseline",
            "--baseline",
            str(bl_file),
            "--plugin-name",
            "flake8",
            "--linter-command",
            _linter_command(),
            "--hook-name",
            HOOK_NAME,
        ],
    )
    (precommit_repo / "new_bad.py").write_text("import y_unknown_module_99999\n")
    result = runner.invoke(
        cli,
        [
            "pre-commit",
            "lint",
            "--baseline",
            str(bl_file),
            "--plugin-name",
            "flake8",
            "--linter-command",
            _linter_command(),
            "new_bad.py",
        ],
    )
    assert result.exit_code != 0
    assert "F401" in result.output
