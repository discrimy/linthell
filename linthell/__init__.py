"""Universal flakehell replacement for almost any linter you like."""

import re
import hashlib
import sys
from pathlib import Path
from typing import List

import click

FLAKE8_REGEX = r'(?P<path>[a-zA-Z0-9\._-]+(?:[\\/][a-zA-Z0-9\._-]+)*):(?P<line>\d+):\d+: (?P<message>[^\n]+)'  # noqa E501


def get_id_line(path: str, line: str, message: str) -> str:
    """Convert path, line and message to id line (path:code_line:message)."""
    lines = Path(path).read_text().splitlines()
    if not lines:
        code = ''
    else:
        code = lines[int(line) - 1]
    normalized_path = Path(path).as_posix()
    return f'{normalized_path}:{code}:{message}'


def get_id_lines(lint_output: str, regex: str) -> List[str]:
    """Search id lines from lint output via provided regex."""
    return [
        get_id_line(
            match.groupdict()['path'],
            match.groupdict()['line'],
            match.groupdict()['message'],
        )
        for match in re.finditer(regex, lint_output)
    ]


def id_line_to_digest(id_line: str) -> str:
    """Convert MD5 hash as hex from utf-8 id line."""
    return hashlib.md5(id_line.encode('utf-8')).hexdigest()


@click.group()
def cli() -> None:
    """Universal flakehell replacement for almost any linter you like.

    Workflow looks like this: at first, create baseline for each linter
    you use. Then replace calls your linter with piping their results
    to `linthell lint` command.
    """
    pass


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
    default=FLAKE8_REGEX,
    help='Regex to parse your linter output.',
    required=True,
)
def baseline(baseline_file: str, lint_format: str) -> None:
    """Create baseline file from your linter output.

    Linter output is provided via stdin.
    """
    id_lines = get_id_lines(sys.stdin.read(), lint_format)
    Path(baseline_file).write_text('\n'.join(sorted(id_lines)))


@cli.command()
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
    default=FLAKE8_REGEX,
    help='Regex to parse your linter output.',
)
@click.option(
    '--check-outdated',
    is_flag=True,
    default=False,
    help='Return non-zero status if there are unused ignores in baseline.',
)
def lint(baseline_file: str, lint_format: str, check_outdated: bool) -> None:
    """Filter your linter output against baseline file.

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


if __name__ == '__main__':
    cli()
