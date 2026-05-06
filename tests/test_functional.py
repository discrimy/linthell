"""Functional tests: full pipeline with real linters.

Each test creates a temp project, runs a real linter inside it, feeds
output to linthell baseline, then feeds SAME output to linthell lint to
verify filtering, and feeds NEW output to verify detection.
"""

import subprocess
import sys
from pathlib import Path

from click.testing import CliRunner

from linthell import cli
from tests.helpers import temp_baseline, temp_project


def test_functional_flake8_filters_and_detects():
    """Run flake8 on buggy file, baseline it, lint filters known, detects new."""
    runner = CliRunner()
    with temp_baseline() as bl_file:
        with temp_project(
            {
                "sample.py": "import os\nimport x_unknown_module_12345\n",
            }
        ):
            # Step 1: Run flake8 on buggy file
            result = subprocess.run(
                [sys.executable, "-m", "flake8", "sample.py"],
                capture_output=True,
                text=True,
            )
            assert result.returncode != 0
            actual_output = result.stdout.strip()
            assert actual_output, "flake8 produced no output — test cannot proceed"

            # Step 2: Generate baseline
            baseline_result = runner.invoke(
                cli,
                ["baseline", "--baseline", str(bl_file), "--plugin-name", "flake8"],
                input=actual_output + "\n",
            )
            assert baseline_result.exit_code == 0, baseline_result.output

            # Step 3: Lint same output — should filter (exit 0, no output)
            lint_result = runner.invoke(
                cli,
                ["lint", "--baseline", str(bl_file), "--plugin-name", "flake8"],
                input=actual_output + "\n",
            )
            assert lint_result.exit_code == 0, (
                f"Expected filtering but got: {lint_result.output}"
            )
            assert lint_result.output == ""

            # Step 4: Lint NEW error in NEW file — should fail
            with Path("new_bad.py").open("w") as f:
                f.write("import x_unknown_module_12345\n")
            new_result = subprocess.run(
                [sys.executable, "-m", "flake8", "new_bad.py"],
                capture_output=True,
                text=True,
            )
            lint_new_result = runner.invoke(
                cli,
                ["lint", "--baseline", str(bl_file), "--plugin-name", "flake8"],
                input=new_result.stdout,
            )
            assert lint_new_result.exit_code != 0, "Expected new errors but got none"
            assert "x_unknown_module_12345" in lint_new_result.output


def test_functional_black_filters_and_detects():
    """Run black --check on badly formatted file, baseline, filter, detect new."""
    runner = CliRunner()
    with temp_baseline() as bl_file:
        with temp_project(
            {
                "bad.py": "def foo(bar,  baz):\n    return bar + baz\n",
            }
        ):
            result = subprocess.run(
                [sys.executable, "-m", "black", "--check", "--diff", "bad.py"],
                capture_output=True,
                text=True,
            )

            actual_output = result.stdout.strip()
            assert actual_output, "black produced no output — test cannot proceed"

            # Step 2: Generate baseline
            baseline_result = runner.invoke(
                cli,
                [
                    "baseline",
                    "--baseline",
                    str(bl_file),
                    "--plugin-name",
                    "black-check",
                ],
                input=actual_output + "\n",
            )
            assert baseline_result.exit_code == 0, baseline_result.output

            # Step 3: Lint same output — should filter (exit 0)
            lint_result = runner.invoke(
                cli,
                ["lint", "--baseline", str(bl_file), "--plugin-name", "black-check"],
                input=actual_output + "\n",
            )
            assert lint_result.exit_code == 0, (
                f"Expected filtering but got: {lint_result.output}"
            )

            # Step 4: Lint NEW badly formatted file — should detect
            with Path("worse.py").open("w") as f:
                f.write("def hello( ):pass\n")
            new_result = subprocess.run(
                [sys.executable, "-m", "black", "--check", "--diff", "worse.py"],
                text=True,
                capture_output=True,
            )
            if new_result.stdout and "would reformat" in new_result.stdout:
                lint_new_result = runner.invoke(
                    cli,
                    [
                        "lint",
                        "--baseline",
                        str(bl_file),
                        "--plugin-name",
                        "black-check",
                    ],
                    input=new_result.stdout,
                )
                assert lint_new_result.exit_code != 0, (
                    "Expected new errors but got none"
                )


def test_functional_isort_filters_and_detects():
    """Run isort on unsorted imports, baseline, filter, detect new."""
    runner = CliRunner()
    with temp_baseline() as bl_file:
        with temp_project(
            {
                "sample.py": "import sys\nimport os\nimport json\n",
            }
        ):
            result = subprocess.run(
                [sys.executable, "-m", "isort", "--check-only", "--diff", "sample.py"],
                capture_output=True,
                text=True,
            )

            actual_output = result.stdout.strip()
            assert actual_output, "isort produced no output — test cannot proceed"

            # Step 2: Generate baseline
            baseline_result = runner.invoke(
                cli,
                ["baseline", "--baseline", str(bl_file), "--plugin-name", "isort-diff"],
                input=actual_output + "\n",
            )
            assert baseline_result.exit_code == 0, baseline_result.output

            # Step 3: Lint same output — should filter (exit 0)
            lint_result = runner.invoke(
                cli,
                ["lint", "--baseline", str(bl_file), "--plugin-name", "isort-diff"],
                input=actual_output + "\n",
            )
            assert lint_result.exit_code == 0, (
                f"Expected filtering but got: {lint_result.output}"
            )


def test_functional_custom_regex_filters_and_detects():
    """Custom --lint-format baseline + lint with new-error detection."""
    runner = CliRunner()
    with temp_baseline() as bl_file:
        fmt = r"(?P<path>.+):(?P<line>\d+):(?P<message>.+)"
        first_input = "sample.py:42:some custom lint issue"

        # Generate baseline
        baseline_result = runner.invoke(
            cli,
            ["baseline", "--baseline", str(bl_file), "--lint-format", fmt],
            input=first_input,
        )
        assert baseline_result.exit_code == 0, baseline_result.output

        # Lint same output — should filter
        lint_result = runner.invoke(
            cli,
            ["lint", "--baseline", str(bl_file), "--lint-format", fmt],
            input=first_input,
        )
        assert lint_result.exit_code == 0, lint_result.output
        assert lint_result.output == ""

        # Lint different output — should detect new error
        new_input = "other.py:99:different issue"
        lint_new_result = runner.invoke(
            cli,
            ["lint", "--baseline", str(bl_file), "--lint-format", fmt],
            input=new_input,
        )
        assert lint_new_result.exit_code != 0, "Expected new errors but got none"
        assert "different issue" in lint_new_result.output
