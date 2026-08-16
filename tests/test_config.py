"""Tests for config dict creation (create_config_dict)."""

from configparser import ConfigParser

from click.testing import CliRunner

from linthell import cli
from linthell.utils.config import create_config_dict


class TestCreateConfigDict:
    def test_common_applies_to_all_commands(self):
        parser = ConfigParser()
        parser["common"] = {"baseline_file": "b.txt"}
        config = create_config_dict(parser, cli.commands)
        assert config["lint"]["baseline_file"] == "b.txt"
        assert config["baseline"]["baseline_file"] == "b.txt"
        assert config["pre-commit"]["lint"]["baseline_file"] == "b.txt"
        assert config["pre-commit"]["baseline"]["baseline_file"] == "b.txt"

    def test_command_section_does_not_leak_to_other_commands(self):
        parser = ConfigParser()
        parser["common"] = {"baseline_file": "b.txt"}
        parser["lint"] = {"plugin_name": "flake8"}
        config = create_config_dict(parser, cli.commands)
        assert config["lint"]["plugin_name"] == "flake8"
        assert "plugin_name" not in config["baseline"]
        assert "plugin_name" not in config["pre-commit"]["lint"]

    def test_nested_group_section(self):
        parser = ConfigParser()
        parser["pre-commit.lint"] = {"linter_command": "flake8"}
        config = create_config_dict(parser, cli.commands)
        assert config["pre-commit"]["lint"]["linter_command"] == "flake8"
        assert "linter_command" not in config["lint"]
        assert "linter_command" not in config["pre-commit"]["baseline"]


class TestConfigOption:
    def test_config_file_common_section(self, tmp_path):
        bl_file = tmp_path / "baseline.txt"
        config_file = tmp_path / "linthell.ini"
        config_file.write_text(f"[common]\nbaseline_file={bl_file}\n")
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["--config", str(config_file), "baseline", "--plugin-name", "flake8"],
            input="test.py:10:5: E501 line too long\n",
        )
        assert result.exit_code == 0, result.output
        assert bl_file.exists()

    def test_config_file_command_section(self, tmp_path):
        bl_file = tmp_path / "baseline.txt"
        config_file = tmp_path / "linthell.ini"
        config_file.write_text(f"[baseline]\nbaseline_file={bl_file}\n")
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["--config", str(config_file), "baseline", "--plugin-name", "flake8"],
            input="test.py:10:5: E501 line too long\n",
        )
        assert result.exit_code == 0, result.output
        assert bl_file.exists()
