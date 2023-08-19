"""CLI that generates baseline file."""

import sys
from pathlib import Path
from typing import Optional

import click
from linthell.plugins.base import get_available_plugins, load_plugin_by_name
from linthell.plugins.regex import LinthellRegexPlugin
from linthell.utils.baseline import generate_baseline, save_baseline
from linthell.utils.click import Mutex


@click.command()
@click.option(
    '--baseline',
    '-b',
    'baseline_file',
    type=click.Path(),
    help='Path to baseline file with ignores.',
    required=True,
)
@click.option(
    '--format',
    '-f',
    'lint_format',
    help='Regex to parse your linter output.',
    default=None,
    cls=Mutex,
    not_required_if=['plugin_name'],
)
@click.option(
    '--plugin',
    '-p',
    'plugin_name',
    help='Plugin to use.',
    type=click.Choice(sorted(get_available_plugins().names)),
    default=None,
    cls=Mutex,
    not_required_if=['lint_format'],
)
def baseline_cli(
    baseline_file: str,
    lint_format: Optional[str],
    plugin_name: Optional[str],
) -> None:
    """Create baseline file from your linter output.

    Linter output is provided via stdin.

    Usage:
    $ <linter command> | linthell baseline
    """
    if plugin_name is not None:
        plugin = load_plugin_by_name(plugin_name)
    else:
        if not lint_format:
            raise ValueError(
                'lint_format must be present if there is no plugin_name'
            )
        plugin = LinthellRegexPlugin(lint_format)

    linter_output = sys.stdin.read()
    id_lines = generate_baseline(linter_output, plugin)
    save_baseline(Path(baseline_file), id_lines)
