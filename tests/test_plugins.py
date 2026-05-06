"""Tests for plugin parse() methods with real linter output strings."""

import linthell.plugins.flake8 as flake8_mod
import linthell.plugins.black_check as black_check_mod
import linthell.plugins.black_diff as black_diff_mod
import linthell.plugins.isort_diff as isort_diff_mod
import linthell.plugins.mypy as mypy_mod
import linthell.plugins.pylint as pylint_mod
import linthell.plugins.pydocstyle as pydocstyle_mod
from linthell.plugins.regex import LinthellRegexPlugin


class TestFlake8Plugin:
    def test_parse_single_error(self):
        plugin = flake8_mod.LinthellFlake8Plugin()
        output = "test.py:10:5: E501 line too long"
        errors = plugin.parse(output)
        assert len(errors) == 1
        assert "E501 line too long" in errors[0].error_message

    def test_parse_multiple_errors(self):
        plugin = flake8_mod.LinthellFlake8Plugin()
        output = "test.py:10:5: E501 line too long\nother.py:20:1: F401 unused import"
        errors = plugin.parse(output)
        assert len(errors) == 2


class TestMypyPlugin:
    def test_parse_single_error(self):
        plugin = mypy_mod.LinthellMypyPlugin()
        output = "test.py:10: error: Incompatible types in assignment"
        errors = plugin.parse(output)
        assert len(errors) == 1
        assert "Incompatible types in assignment" in errors[0].error_message

    def test_parse_error_with_note(self):
        plugin = mypy_mod.LinthellMypyPlugin()
        output = 'test.py:10: error: Incompatible types in assignment\ntest.py:10: note: Revealed type is "builtins.str"'
        errors = plugin.parse(output)
        assert len(errors) == 1

    def test_parse_no_match(self):
        plugin = mypy_mod.LinthellMypyPlugin()
        output = "test.py:10: warning: something"
        errors = plugin.parse(output)
        assert errors == []


class TestPylintPlugin:
    def test_parse_single_error(self):
        plugin = pylint_mod.LinthellPylintPlugin()
        output = "test.py:10:10: C0301 line too long: C0301"
        errors = plugin.parse(output)
        assert len(errors) == 1
        assert "too long" in errors[0].error_message

    def test_parse_multiple_errors(self):
        plugin = pylint_mod.LinthellPylintPlugin()
        output = "test.py:10:10: C0301 line too long: C0301\nbar.py:5:5: W0613 unused argument: W0613"
        errors = plugin.parse(output)
        assert len(errors) == 2


class TestPydocstylePlugin:
    def test_parse_single_error(self):
        plugin = pydocstyle_mod.LinthellPydocstylePlugin()
        output = (
            "test.py:1: no public method D102\n    Missing docstring in public method"
        )
        errors = plugin.parse(output)
        assert len(errors) == 1
        assert errors[0].error_message.startswith("test.py:1:")

    def test_parse_no_match(self):
        plugin = pydocstyle_mod.LinthellPydocstylePlugin()
        output = "test.py:1: something\nsomething"
        errors = plugin.parse(output)
        assert errors == []


class TestRegexPlugin:
    def test_custom_format_single_match(self):
        regex = r"(?P<path>.+):(?P<line>\d+):(?P<message>.+)"
        plugin = LinthellRegexPlugin(lint_format=regex)
        output = "foo/bar.py:42:something wrong"
        errors = plugin.parse(output)
        assert len(errors) == 1
        assert errors[0].error_message == "foo/bar.py:42:something wrong"

    def test_custom_format_no_match(self):
        regex = r"(?P<path>nonexistent\.py):(?P<line>\d+):"
        plugin = LinthellRegexPlugin(lint_format=regex)
        output = "no match here"
        errors = plugin.parse(output)
        assert errors == []

    def test_custom_format_multiple_matches(self):
        regex = r"(?P<path>.+):(?P<line>\d+): (?P<message>.+)"
        plugin = LinthellRegexPlugin(lint_format=regex)
        output = "a.py:1: err1\na.py:2: err2\nb.py:3: err3"
        errors = plugin.parse(output)
        assert len(errors) == 3


class TestBlackCheckPlugin:
    def test_parse_single_file(self):
        plugin = black_check_mod.LinthellBlackCheckPlugin()
        output = "would reformat test.py\n\nAll done! \U0001f389 1 file would be reformatted."
        errors = plugin.parse(output)
        assert len(errors) == 1
        assert "test.py" in errors[0].id_line

    def test_parse_multiple_files(self):
        plugin = black_check_mod.LinthellBlackCheckPlugin()
        output = "would reformat file1.py\nwould reformat file2.py"
        errors = plugin.parse(output)
        assert len(errors) == 2

    def test_parse_no_files_to_reformat(self):
        plugin = black_check_mod.LinthellBlackCheckPlugin()
        output = "All done! \U0001f389 1 file would be left unchanged."
        errors = plugin.parse(output)
        assert errors == []


class TestBlackDiffPlugin:
    def test_parse_single_file_diff(self):
        plugin = black_diff_mod.LinthellBlackDiffPlugin()
        output = (
            "--- package/module.py\t2023-08-24 18:03:29.245834 +0000\n"
            "+++ package/module.py\t2023-08-24 18:03:30.951316 +0000\n"
            "@@ -1,3 +1,7 @@\n"
            " import re\n"
            "\n"
            "-def func(*args,):\n"
            "\n"
            "+\n"
            "+def func(\n"
            "+    *args,\n"
            "+):\n"
            "     pass"
        )
        errors = plugin.parse(output)
        assert len(errors) > 0

    def test_parse_empty_no_diff(self):
        plugin = black_diff_mod.LinthellBlackDiffPlugin()
        output = "No errors, no diff!"
        errors = plugin.parse(output)
        assert errors == []


class TestIsortDiffPlugin:
    def test_parse_single_file_diff(self):
        plugin = isort_diff_mod.LinthellIsortDiffPlugin()
        output = (
            "--- package/module.py:before\t2023-08-27 19:16:45.692641\n"
            "+++ package/module.py:after\t2023-08-27 19:16:53.009897\n"
            "@@ -1,3 +1,3 @@\n"
            "+import a\n"
            " import b\n"
            "-import a"
        )
        errors = plugin.parse(output)
        assert len(errors) > 0

    def test_parse_empty_no_diff(self):
        plugin = isort_diff_mod.LinthellIsortDiffPlugin()
        output = "Skipped 2 files"
        errors = plugin.parse(output)
        assert errors == []
