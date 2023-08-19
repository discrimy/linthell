"""Baseline CLI with pre-commit integration."""

from pathlib import Path
from typing import Optional

import click
from typing_extensions import Literal

from linthell.commands.baseline import generate_baseline, save_baseline
from linthell.plugins.base import get_available_plugins, load_plugin_by_name
from linthell.plugins.regex import LinthellRegexPlugin
from linthell.utils.click import Mutex
from linthell.utils.linters import run_linter_and_get_output
from linthell.utils.pre_commit import get_all_files_by_hook


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
@click.option(
    '--hook-name',
    type=click.STRING,
    help='Update baseline based on all files from pre-commit hook',
    required=True,
)
def baseline_cli(
    baseline_file: str,
    lint_format: Optional[str],
    plugin_name: Optional[str],
    linter_command: str,
    linter_output: Literal['stdout', 'stderr'],
    hook_name: str,
) -> None:
    """Linthell baseline command for pre-commit workflow.

    Algorithm is same as regular `linthell baseline`, but it uses pre-commit
    features:
    - List of files is extracted from pre-commit config based on hook name.
    - Executes linter command embedded, so you can set it inside linthell
    config file.

    Usage:
    $ linthell pre-commit baseline --hook-name <linthell hook name>
    """
    if plugin_name:
        plugin = load_plugin_by_name(plugin_name)
    elif lint_format:
        plugin = LinthellRegexPlugin(lint_format)
    else:
        raise click.BadOptionUsage(
            'lint_format | plugin_name',
            'Provide either lint_format or plugin_name',
        )

    files = get_all_files_by_hook('.pre-commit-config.yaml', hook_name)
    output = run_linter_and_get_output(linter_command, files, linter_output)

    id_lines = generate_baseline(output, plugin)
    save_baseline(Path(baseline_file), id_lines)
