"""linthell lint alternative for pre_commit"""

import shlex
import subprocess
from typing import Tuple

import click


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
    '--update-baseline-file',
    type=click.BOOL,
    help=(
        'Update baseline file to be consistent with current code. '
        'Useful when you need to update baseline based on pre_commit filters'
    ),
    is_flag=True,
    default=False,
)
@click.argument('files', nargs=-1, type=click.Path())
def lint_cli(
    baseline_file: str,
    lint_format: str,
    linter_command: str,
    linter_output: str,
    update_baseline_file: bool,
    files: Tuple[str, ...],
) -> None:
    """Linthell with embedded linter executing.

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
    """
    linter_process = subprocess.run(
        [*shlex.split(linter_command), *files],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if linter_output == 'stdout':
        output = linter_process.stdout
    else:
        output = linter_process.stderr
    process = subprocess.run(
        ['linthell', 'lint', '-b', baseline_file, '-f', lint_format],
        text=True,
        input=output,
        stdout=subprocess.PIPE,
    )
    print(process.stdout, end='')

    if update_baseline_file:
        subprocess.run(
            ['linthell', 'baseline', '-b', baseline_file, '-f', lint_format],
            text=True,
            input=output,
            check=True,
        )

    if process.returncode:
        exit(process.returncode)
