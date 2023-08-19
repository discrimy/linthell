"""Lint CLI with pre-commit integration."""

import sys
from pathlib import Path
from typing import Optional, Tuple

import click
from typing_extensions import Literal

from linthell.commands.lint import lint, get_digests_from_baseline
from linthell.plugins.base import get_available_plugins, load_plugin_by_name
from linthell.plugins.regex import LinthellRegexPlugin
from linthell.utils.click import Mutex
from linthell.utils.linters import run_linter_and_get_output


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
@click.option(
    '--linter-command',
    type=click.STRING,
    help='Linter command with options to execute.',
    required=True,
)
@click.option(
    '--linter-output',
    type=click.Choice(('stdout', 'stderr')),
    help='Where linter outputs his errors',
    default='stdout',
    show_default=True,
)
@click.argument('files', nargs=-1, type=click.Path())
def lint_cli(
    baseline_file: str,
            lint_format: Optional[str],
    plugin_name: Optional[str],
    linter_command: str,
    linter_output: Literal['stdout', 'stderr'],
    files: Tuple[str, ...],
) -> None:
    """Linthell lint command for pre-commit workflow.

    The purpose of this command is to be the thin wrapper around
    `linthell lint` command, but linter is called inside command. Such behavior
     is required by `pre_commit` hook definition.

    A linter is called in format `<linter-command> <files to proceed separated
    with ' '>`, its return code is ignored. After the output of linter is
    passed to `linthell lint` command alongside with basefile location and lint
    format. The hook requires to pass `--baseline`, `--format` and
    `--linter-command` in `args` section.

    There are two ways to adapt linthell as pre_commit hook:

    1. As python linter: if your linter is python-based (flake8, pydocstyle)
    then you can use default `language` and `entrypoint` configuration of hook.

    2. As system linter: if your linter is not python-based (or requires to be
    installed inside venv of your project like pylint do) then you must set
    `language: system` and
    `entrypoint: <command to launch linthell-pre_commit>`. pre_commit runs
    hooks outside venv, so you should adapt hook config to run the command
    inside it. For example, pylint with poetry as venv manager can be launched
    via `entrypoint: poetry run pylint ...`.

    Usage:
    Create a pre-commit hook with entry like: `linthell pre-commit lint`.
    """
    if plugin_name is not None:
        plugin = load_plugin_by_name(plugin_name)
    else:
        if not lint_format:
            raise ValueError('lint_format must be present if there is no plugin_name')
        plugin = LinthellRegexPlugin(lint_format)
    
    output = run_linter_and_get_output(linter_command, files, linter_output)

    digests = get_digests_from_baseline(Path(baseline_file))
    report = lint(digests, output, plugin)
    if report.errors:
        for error_message in report.errors:
            print(error_message)
        sys.exit(1)
