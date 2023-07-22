"""Utilities for config files."""

from configparser import ConfigParser
from typing import Dict, Any

from click import Group, Command


def config_to_dict(config_parser: ConfigParser) -> Dict[str, Dict[str, str]]:
    """Convert parser ConfigParser to dict.

    Output format: {<section>: {<key>: <string value>}}
    """
    return {
        section: dict(**config_parser[section])
        for section in config_parser.sections()
    }


def get_by_dotted_path(d: Dict[str, Any], path: str) -> Any:
    """Get a nested dict element by dotted path.

    Example:
    d = {'a': {'b': {'c': 42}}}
    get_by_dotted_path(d, 'a.b.c')  # 42
    """
    keys = path.split('.')
    rv = d
    for key in keys:
        rv = rv[key]
    return rv


ConfigMap = Dict[str, 'ConfigMap']


def create_default_map(
    common: Dict[str, str], commands: Dict[str, Command]
) -> ConfigMap:
    """Create a config dict with default values."""
    return {
        command_name: create_default_map(common, command.commands)
        if isinstance(command, Group)
        else {**common}
        for command_name, command in commands.items()
    }


def create_config_dict(
    config_parser: ConfigParser,
    commands: Dict[str, Command],
):
    """Create config to be used as click.Context.default_map values.

    Supports nested groups.

    Top element 'common' will be used as default for all commands.
    """
    sections = config_to_dict(config_parser)
    common = sections.pop('common', {})
    config = create_default_map(common, commands)
    for path, values in sorted(sections.items(), key=lambda pair: pair[0]):
        get_by_dotted_path(config, path).update(**values)
    return config
