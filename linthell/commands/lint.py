import re
import sys
from pathlib import Path

import click

from linthell.defaults import FLAKE8_REGEX
from linthell.utils.id_lines import id_line_to_digest, get_id_line


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
@click.option(
    '--check-outdated',
    is_flag=True,
    default=False,
    help='Return non-zero status if there are unused ignores in baseline.',
    required=True,
)
def lint_cli(
    baseline_file: str, lint_format: str, check_outdated: bool
) -> None:
    """Filter your linter output against baseline file.

    It scans the linter output against baseline file and filters it. If all
    errors are ignored (or there are no errors), then it prints nothing and
    exits with code 0, otherwise it prints the whole match of format regex
    as error description for each unfiltered error and exists with code 1.

    Linter output is provided via stdin.
    """
    has_errors = False
    id_lines = Path(baseline_file).read_text().splitlines()
    digests = {id_line_to_digest(id_line): False for id_line in id_lines}
    for match in re.finditer(lint_format, sys.stdin.read()):
        path = match.groupdict()['path']
        line = match.groupdict()['line']
        message = match.groupdict()['message']
        lint_message = match.group(0)
        id_line = get_id_line(path, line, message)
        digest = id_line_to_digest(id_line)
        if digest not in digests:
            print(lint_message)
            has_errors = True
        else:
            digests[digest] = True

    if check_outdated and not all(digests.values()):
        print(
            'There are outdated entries in your baseline file. '
            'Consider updating it.'
        )
        has_errors = True

    if has_errors:
        sys.exit(1)
