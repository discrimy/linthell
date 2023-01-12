"""linthell baseline alternative for pre-commit"""

import subprocess
from typing import Tuple, Optional

import click

from linthell import cli
from linthell.utils import run_linter_and_get_output
from linthell.pre_commit import get_all_files_by_hook


@cli.command()
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
    help='Update baseline based on all files from pre-commit hook',
    required=False,
)
@click.argument('files', nargs=-1, type=click.Path())
def pre_commit_baseline(
    baseline_file: str,
    lint_format: str,
    linter_command: str,
    linter_output: str,
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

    baseline_process = subprocess.run(
        ['linthell', 'baseline', '-b', baseline_file, '-f', lint_format],
        text=True,
        input=output,
    )
    exit(baseline_process.returncode)
