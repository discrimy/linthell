"""Baseline CLI with pre-commit integration."""

from pathlib import Path
from typing import Optional

import click
from typing_extensions import Literal

from linthell.commands.baseline import baseline, save_baseline
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
    '--format',
    '-f',
    'lint_format',
    help='Regex to parse your linter output.',
    required=True,
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
    lint_format: str,
    linter_command: str,
    linter_output: Literal['stdout', 'stderr'],
    hook_name: Optional[str],
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
    files = get_all_files_by_hook('.pre-commit-config.yaml', hook_name)
    output = run_linter_and_get_output(linter_command, files, linter_output)

    id_lines = baseline(output, lint_format)
    save_baseline(Path(baseline_file), id_lines)
