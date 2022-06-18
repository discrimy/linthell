import re
import hashlib
import sys
from pathlib import Path

import click

FLAKE8_REGEX = r'(?P<path>[a-zA-Z0-9\._-]+(?:[\\/][a-zA-Z0-9\._-]+)*):(?P<line>\d+):\d+: (?P<message>[^\n]+)'
PYDOCSTYLE_REGEX = r'(?P<path>[a-zA-Z0-9\._-]+(?:[\\/][a-zA-Z0-9\._-]+)*):(?P<line>\d+).+\n\s+(?P<message>[^\n]+)'
PYLINT_REGEX = r'(?P<path>[a-zA-Z0-9\._-]+(?:[\\/][a-zA-Z0-9\._-]+)*):(?P<line>\d+):\d+: (?P<message>[^\n]+)'


def get_id_line(path: str, line: str, message: str) -> str:
    lines = Path(path).read_text().splitlines()
    if not lines:
        code = ''
    else:
        code = lines[int(line) - 1]
    normalized_path = Path(path).as_posix()
    return f'{normalized_path}:{code}:{message}'


def get_id_lines(lint_output: str, regex: str) -> list[str]:
    return [
        get_id_line(
            match.groupdict()['path'],
            match.groupdict()['line'],
            match.groupdict()['message'],
        )
        for match
        in re.finditer(regex, lint_output)
    ]


def id_line_to_digest(id_line: str) -> str:
    return hashlib.md5(id_line.encode('utf-8')).hexdigest()


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.option('--baseline', '-b', 'baseline_file')
@click.option('--format', '-f', 'lint_format', default=FLAKE8_REGEX)
def baseline(baseline_file: str, lint_format: str) -> None:
    id_lines = get_id_lines(sys.stdin.read(), lint_format)
    Path(baseline_file).write_text('\n'.join(sorted(id_lines)))


@cli.command()
@click.option('--baseline', '-b', 'baseline_file', type=click.Path())
@click.option('--format', '-f', 'lint_format', default=FLAKE8_REGEX)
def lint(baseline_file: str, lint_format: str) -> None:
    has_errors = False
    id_lines = Path(baseline_file).read_text().splitlines()
    digests = {id_line_to_digest(id_line) for id_line in id_lines}
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
    if has_errors:
        sys.exit(1)


if __name__ == '__main__':
    cli()
