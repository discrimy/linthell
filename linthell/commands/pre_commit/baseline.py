"""linthell baseline alternative for pre_commit"""

import subprocess
from pathlib import Path
from typing import Tuple, Optional

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
    help='Linter output',
    default='stdout',
)
@click.option(
    '--hook-name',
    type=click.STRING,
    help='Update baseline based on all files from pre_commit hook',
    required=False,
)
@click.argument('files', nargs=-1, type=click.Path())
def baseline_cli(
    baseline_file: str,
    lint_format: str,
    linter_command: str,
    linter_output: Literal['stdout', 'stderr'],
    hook_name: Optional[str],
    files: Tuple[str, ...],
) -> None:
    """"""
    # files and hook_name are exclusive
    if files and hook_name:
        print('files arguments and --hook-name are exclusive')
        exit(1)

    if not files and hook_name:
        files = get_all_files_by_hook('.pre-commit-config.yaml', hook_name)

    output = run_linter_and_get_output(linter_command, files, linter_output)

    id_lines = baseline(output, lint_format)
    save_baseline(Path(baseline_file), id_lines)
