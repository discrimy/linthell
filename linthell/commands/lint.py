"""CLI that lints linter output based on baseline file."""

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Set

import click

from linthell.utils.id_lines import id_line_to_digest, get_id_line


@dataclass
class LintReport:
    """Report from linting."""

    errors: List[str]


def lint(
    digests: Set[str], linter_output: str, lint_format: str
) -> LintReport:
    """Lint linter output based on known errors' digests."""
    errors = []

    for match in re.finditer(lint_format, linter_output):
        path = match.groupdict()['path']
        line = match.groupdict()['line']
        message = match.groupdict()['message']
        lint_message = match.group(0)
        id_line = get_id_line(path, line, message)
        digest = id_line_to_digest(id_line)
        if digest not in digests:
            errors.append(lint_message)

    return LintReport(errors)


def get_digests_from_baseline(baseline_file: Path) -> Set[str]:
    """Get digests from provided baseline file."""
    id_lines = Path(baseline_file).read_text().splitlines()
    digests = {id_line_to_digest(id_line) for id_line in id_lines}
    return digests


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
def lint_cli(baseline_file: str, lint_format: str) -> None:
    """Filter your linter output against baseline file.

    It scans the linter output against baseline file and filters it. If all
    errors are ignored (or there are no errors), then it prints nothing and
    exits with code 0, otherwise it prints the whole match of format regex
    as error description for each unfiltered error and exists with code 1.

    Linter output is provided via stdin.

    Usage:
    $ <linter command> | linthell lint
    """
    linter_output = sys.stdin.read()
    digests = get_digests_from_baseline(Path(baseline_file))
    report = lint(digests, linter_output, lint_format)

    if report.errors:
        for error_message in report.errors:
            print(error_message)
        sys.exit(1)
