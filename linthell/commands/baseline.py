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
    '--lint-format',
    '--format',
    '-f',
    'lint_format',
    help='Regex to parse your linter output.',
    default=None,
    cls=Mutex,
    not_required_if=['plugin_name'],
)
@click.option(
    '--plugin-name',
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
    if plugin_name:
        plugin = load_plugin_by_name(plugin_name)
    elif lint_format:
        plugin = LinthellRegexPlugin(lint_format)
    else:
        raise click.BadOptionUsage('lint_format | plugin_name', 'Provide either lint_format or plugin_name')

    linter_output = sys.stdin.read()
    id_lines = generate_baseline(linter_output, plugin)
    save_baseline(Path(baseline_file), id_lines)
