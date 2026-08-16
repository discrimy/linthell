"""Tests for run_linter_and_get_output with real subprocesses."""

import sys

from linthell.utils.linters import run_linter_and_get_output


def _python_command(code: str) -> str:
    return f'"{sys.executable}" -c "{code}"'


def test_returns_stdout():
    output = run_linter_and_get_output(
        _python_command("import sys; sys.stdout.write('hello')"),
        (),
        "stdout",
    )
    assert output == "hello"


def test_returns_stderr():
    output = run_linter_and_get_output(
        _python_command("import sys; sys.stderr.write('boom')"),
        (),
        "stderr",
    )
    assert output == "boom"


def test_files_are_appended_to_command():
    output = run_linter_and_get_output(
        _python_command("import sys; sys.stdout.write(' '.join(sys.argv[1:]))"),
        ("a.py", "b.py"),
        "stdout",
    )
    assert output == "a.py b.py"
