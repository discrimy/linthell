import sys
from pathlib import Path
from typing import List

import click

from linthell.defaults import FLAKE8_REGEX
from linthell.utils.id_lines import get_id_lines


def baseline(linter_output: str, lint_format: str) -> List[str]:
    return get_id_lines(linter_output, lint_format)


def save_baseline(baseline_file: Path, id_lines: List[str]) -> None:
    baseline_file.write_text('\n'.join(sorted(id_lines)))


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
    linter_output = sys.stdin.read()
    id_lines = baseline(linter_output, lint_format)
    save_baseline(Path(baseline_file), id_lines)
