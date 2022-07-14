"""Thin wrapper around `linthell lint` command with embedded linter execution."""
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
)
@click.option(
    '--format',
    '-f',
    'lint_format',
    help='Regex to parse your linter output.',
)
@click.option('--linter-command', type=click.STRING, help='Linter command with options to execute.')
@click.argument('files', nargs=-1, type=click.Path())
def cli(baseline_file: str, lint_format: str, linter_command: str, files: Tuple[str, ...]) -> None:
    """Linthell with embedded linter executing.

    The purpose of this command is to be the thin wrapper around `linthell lint` command,
    but linter is called inside command. Such behavior is required by `pre-commit` hook definition.

    A linter is called in format `<linter-command> <files to proceed separated with ' '>`, its return code is ignored.
    After the output of linter is passed to `linthell lint` command alongside with basefile location and lint format.

    pre-commit hook requires to pass options `--baseline`, `--format` and `--linter-command` in `args` section.
    Also linter mentioned in `--linter-command` must present inside venv of hook, so include it and its dependencies
    in `additional_dependencies` section. See `.pre-commit-config.example.yaml` for the reference.
    """
    linter_process = subprocess.run(
        [*shlex.split(linter_command), *files],
        text=True,
        stdout=subprocess.PIPE,
        check=False,
    )
    process = subprocess.run(
        ['linthell', 'lint', '-b', baseline_file, '-f', lint_format],
        text=True,
        input=linter_process.stdout,
        stdout=subprocess.PIPE,
    )
    print(process.stdout, end='')
    if process.returncode:
        exit(process.returncode)


if __name__ == '__main__':
    cli()

