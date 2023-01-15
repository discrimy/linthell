import sys
from pathlib import Path

import click

from linthell.defaults import FLAKE8_REGEX
from linthell.utils.id_lines import get_id_lines


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
    default=FLAKE8_REGEX,
    help='Regex to parse your linter output.',
    required=True,
)
def baseline_cli(baseline_file: str, lint_format: str) -> None:
    """Create baseline file from your linter output.

    Linter output is provided via stdin.
    """
    id_lines = get_id_lines(sys.stdin.read(), lint_format)
    Path(baseline_file).write_text('\n'.join(sorted(id_lines)))
