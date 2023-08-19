"""CLI that lints linter output based on baseline file."""

import sys
from pathlib import Path
from typing import Optional

import click
from linthell.plugins.base import get_available_plugins, load_plugin_by_name
from linthell.plugins.regex import LinthellRegexPlugin
from linthell.utils.baseline import get_digests_from_baseline
from linthell.utils.click import Mutex
from linthell.utils.lint import lint


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
def lint_cli(
    baseline_file: str, lint_format: Optional[str], plugin_name: Optional[str]
) -> None:
    """Filter your linter output against baseline file.

    It scans the linter output against baseline file and filters it. If all
    errors are ignored (or there are no errors), then it prints nothing and
    exits with code 0, otherwise it prints the whole match of format regex
    as error description for each unfiltered error and exists with code 1.

    Linter output is provided via stdin.

    Usage:
    $ <linter command> | linthell lint
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
    digests = get_digests_from_baseline(Path(baseline_file))
    report = lint(digests, linter_output, plugin)

    if report.errors:
        for error_message in report.errors:
            print(error_message)
        sys.exit(1)
