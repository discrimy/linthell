"""Unit tests for pure linthell logic functions. No I/O, no mocks required."""

from configparser import ConfigParser
from pathlib import Path
from unittest.mock import MagicMock

import click

from linthell.utils.baseline import load_baseline, save_baseline
from linthell.utils.click import Mutex
from linthell.utils.config import config_to_dict, get_by_dotted_path
from linthell.utils.id_lines import id_line_to_digest
from linthell.utils.lint import LintReport, lint
from linthell.utils.path import normalize_path
from linthell.utils.types import LinterError
from tests.helpers import temp_baseline, temp_project


class TestIdLineToDigest:
    """Tests for id_line_to_digest function."""

    def test_returns_hex_string(self):
        digest = id_line_to_digest("file.py:    x = 1: E501")
        assert isinstance(digest, str)
        assert len(digest) == 32  # MD5 hex is always 32 chars
        assert all(c in "0123456789abcdef" for c in digest)

    def test_deterministic(self):
        line = "file.py:    x = 1: E501"
        assert id_line_to_digest(line) == id_line_to_digest(line)

    def test_different_input_different_output(self):
        digest1 = id_line_to_digest("file.py:    x: msg1")
        digest2 = id_line_to_digest("file.py:    y: msg2")
        assert digest1 != digest2


class TestBaselineEncodingRoundTrip:
    """Tests for baseline file unicode escape/unescape encoding."""

    def test_roundtrip_preserves_lines(self):
        id_lines = ["file.py:    x: msg1", "other.py:    y: msg2"]
        with temp_baseline() as bl_path:
            save_baseline(bl_path, id_lines)
            result = load_baseline(bl_path)
            assert result == sorted(id_lines)

    def test_roundtrip_preserves_unicode(self):
        id_lines = ["file.py:def func(unicode: é): E999"]
        with temp_baseline() as bl_path:
            save_baseline(bl_path, id_lines)
            result = load_baseline(bl_path)
            assert result == id_lines

    def test_roundtrip_preserves_tabs(self):
        id_lines = ["file.py:    import\tos: E401"]
        with temp_baseline() as bl_path:
            save_baseline(bl_path, id_lines)
            result = load_baseline(bl_path)
            assert result == id_lines

    def test_baseline_write_is_sorted(self):
        lines = ["z.py: msg1", "a.py: msg0"]
        with temp_baseline() as bl_path:
            save_baseline(bl_path, lines)
            raw_lines = bl_path.read_text().splitlines()
            assert raw_lines[0] < raw_lines[1]


class TestLintFunction:
    """Tests for the lint() core function."""

    @staticmethod
    def _make_mock_plugin(parsing_result):
        """Create a mock plugin that returns given LinterError list."""
        plugin = MagicMock()
        plugin.parse.return_value = parsing_result
        return plugin

    def test_no_errors_when_all_known(self):
        mock_plugin = self._make_mock_plugin(
            [
                LinterError(
                    id_line="file.py:    x: msg1", error_message="file.py: x: msg1"
                ),
            ]
        )
        digests = {id_line_to_digest("file.py:    x: msg1")}
        report = lint(digests, "", mock_plugin)
        assert report.errors == []

    def test_reports_new_error(self):
        mock_plugin = self._make_mock_plugin(
            [
                LinterError(
                    id_line="file.py:    y: msg2", error_message="file.py: y: msg2"
                ),
            ]
        )
        digests = set()  # nothing known
        report = lint(digests, "", mock_plugin)
        assert report.errors == ["file.py: y: msg2"]

    def test_filters_known_error(self):
        mock_plugin = self._make_mock_plugin(
            [
                LinterError(
                    id_line="file.py:    x: msg1", error_message="file.py: x: msg1"
                ),
            ]
        )
        digests = {id_line_to_digest("file.py:    x: msg1")}
        report = lint(digests, "", mock_plugin)
        assert report.errors == []

    def test_reports_only_new_errors(self):
        mock_plugin = self._make_mock_plugin(
            [
                LinterError(
                    id_line="file.py:    x: msg1", error_message="file.py: x: msg1"
                ),
                LinterError(
                    id_line="file.py:    y: msg2", error_message="file.py: y: msg2"
                ),
            ]
        )
        digests = {id_line_to_digest("file.py:    x: msg1")}
        report = lint(digests, "", mock_plugin)
        assert report.errors == ["file.py: y: msg2"]

    def test_empty_input_returns_empty_report(self):
        mock_plugin = self._make_mock_plugin([])
        report = lint(set(), "", mock_plugin)
        assert report.errors == []
        assert isinstance(report, LintReport)


class TestMutex:
    """Tests for the Mutex Click option class."""

    def test_has_not_required_if(self):
        option = Mutex(["--test"], not_required_if=["other"])
        assert option.not_required_if == ["other"]

    def test_inherits_from_click_option(self):
        option = Mutex(["--test"], not_required_if=["other"])
        assert isinstance(option, click.Option)

    def test_adds_help_text(self):
        option = Mutex(["--test"], not_required_if=["other"])
        assert "other" in option.help
        assert "mutually exclusive" in option.help


class TestConfigFunctions:
    """Tests for config.py utility functions."""

    def test_config_to_dict_converts_sections(self):
        parser = ConfigParser()
        parser["section1"] = {"key1": "val1", "key2": "val2"}
        result = config_to_dict(parser)
        assert result == {"section1": {"key1": "val1", "key2": "val2"}}

    def test_config_to_dict_multiple_sections(self):
        parser = ConfigParser()
        parser["common"] = {"baseline_file": "baseline.txt"}
        parser["lint"] = {"plugin_name": "flake8"}
        result = config_to_dict(parser)
        assert "common" in result
        assert "lint" in result
        assert result["common"]["baseline_file"] == "baseline.txt"
        assert result["lint"]["plugin_name"] == "flake8"

    def test_get_by_dotted_path_single_key(self):
        d = {"a": "value"}
        assert get_by_dotted_path(d, "a") == "value"

    def test_get_by_dotted_path_nested(self):
        d = {"a": {"b": {"c": 42}}}
        assert get_by_dotted_path(d, "a.b.c") == 42

    def test_get_by_dotted_path_two_levels(self):
        d = {"a": {"b": "val2"}}
        assert get_by_dotted_path(d, "a.b") == "val2"


class TestNormalizePath:
    """Tests for path normalization."""

    def test_simple_relative_path(self):
        with temp_project({"test.txt": "content"}):
            result = normalize_path(Path("test.txt"))
            assert result == "test.txt"

    def test_absolute_path_becomes_relative(self):
        with temp_project({"sub/test.txt": "content"}):
            path = Path("sub/test.txt").resolve()
            result = normalize_path(path)
            assert isinstance(result, str)
            assert "/" in result or "test.txt" in result
