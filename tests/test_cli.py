"""CLI integration tests using click.testing.CliRunner."""

from click.testing import CliRunner

from linthell import cli
from tests.helpers import temp_baseline


def test_lint_help():
    """Lint command shows help with options."""
    runner = CliRunner()
    result = runner.invoke(cli, ["lint", "--help"])
    assert result.exit_code == 0
    assert "--baseline" in result.output
    assert "--lint-format" in result.output
    assert "--plugin-name" in result.output


def test_baseline_help():
    """Baseline command shows help with options."""
    runner = CliRunner()
    result = runner.invoke(cli, ["baseline", "--help"])
    assert result.exit_code == 0
    assert "--baseline" in result.output
    assert "--lint-format" in result.output
    assert "--plugin-name" in result.output


def test_lint_requires_baseline_file():
    """Lint command fails without --baseline option."""
    runner = CliRunner()
    result = runner.invoke(cli, ["lint", "--plugin-name", "flake8"])
    assert result.exit_code != 0


def test_baseline_requires_baseline_file():
    """Baseline command fails without --baseline option."""
    runner = CliRunner()
    result = runner.invoke(cli, ["baseline"])
    assert result.exit_code != 0


def test_lint_format_and_plugin_name_mutually_exclusive():
    """Lint command fails if both --lint-format and --plugin-name are provided."""
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "baseline",
            "--baseline",
            "dummy.txt",
            "--lint-format",
            "test",
            "--plugin-name",
            "flake8",
        ],
    )
    assert result.exit_code != 0
    assert "mutually exclusive" in result.output.lower() or "Error" in result.output


def test_lint_format_and_plugin_name_neither_provided():
    """Lint command fails if neither --lint-format nor --plugin-name is provided."""
    runner = CliRunner()
    with temp_baseline() as bl_file:
        result = runner.invoke(cli, ["lint", f"--baseline={bl_file}"])
        assert result.exit_code != 0


def test_baseline_creates_file_with_plugin():
    """Baseline command creates a file when given plugin name."""
    runner = CliRunner()
    with temp_baseline() as bl_file:
        result = runner.invoke(
            cli,
            ["baseline", "--baseline", str(bl_file), "--plugin-name", "flake8"],
            input="test.py:10:5: E501 line too long\n",
        )
        assert result.exit_code == 0
        assert bl_file.exists()
        content = bl_file.read_text()
        assert "E501" in content


def test_baseline_creates_file_with_format():
    """Baseline command creates a file when given --lint-format."""
    runner = CliRunner()
    with temp_baseline() as bl_file:
        result = runner.invoke(
            cli,
            [
                "baseline",
                "--baseline",
                str(bl_file),
                "--lint-format",
                r"(?P<path>.+):(?P<line>\d+):\d+: (?P<message>.+)",
            ],
            input="test.py:10:5: E501 line too long\n",
        )
        assert result.exit_code == 0
        assert bl_file.exists()
        content = bl_file.read_text()
        assert "E501" in content


def test_lint_filters_known_errors():
    """Lint command filters errors that are in the baseline."""
    runner = CliRunner()
    with temp_baseline() as bl_file:
        # Generate baseline first
        runner.invoke(
            cli,
            ["baseline", "--baseline", str(bl_file), "--plugin-name", "flake8"],
            input="test.py:10:5: E501 line too long\n",
        )
        # Lint the same output — should filter and exit 0
        result = runner.invoke(
            cli,
            ["lint", "--baseline", str(bl_file), "--plugin-name", "flake8"],
            input="test.py:10:5: E501 line too long\n",
        )
        assert result.exit_code == 0
        assert result.output == ""


def test_lint_detects_new_errors():
    """Lint command fails and shows output when new errors are found."""
    runner = CliRunner()
    with temp_baseline() as bl_file:
        # Baseline has only error line 10
        runner.invoke(
            cli,
            ["baseline", "--baseline", str(bl_file), "--plugin-name", "flake8"],
            input="test.py:10:5: E501 line too long\n",
        )
        # Lint with a new error on line 20
        result = runner.invoke(
            cli,
            ["lint", "--baseline", str(bl_file), "--plugin-name", "flake8"],
            input="test.py:20:1: F401 unused import\n",
        )
        assert result.exit_code != 0
        assert "F401" in result.output


def test_lint_format_custom_regex_filters():
    """Custom --lint-format works the same as plugin-name for filtering."""
    runner = CliRunner()
    with temp_baseline() as bl_file:
        fmt = r"(?P<path>.+):(?P<line>\d+):(?P<message>.+)"

        first_input = "sample.py:42:some lint issue"

        runner.invoke(
            cli,
            ["baseline", "--baseline", str(bl_file), "--lint-format", fmt],
            input=first_input,
        )

        result = runner.invoke(
            cli,
            ["lint", "--baseline", str(bl_file), "--lint-format", fmt],
            input=first_input,
        )
        assert result.exit_code == 0
