import re
import hashlib
import sys
from pathlib import Path
from typing import List

import click

FLAKE8_REGEX = r'(.+\/[^\/]+):(\d+):\d+: ([^\n]+)'
PYDOCSTYLE_REGEX = r'(.+\/[^\/]+):(\d+).+\n\s+([^\n]+)'
PYLINT_REGEX = r'(.+\/[^\/]+):(\d+):\d+: ([^\n]+)'


def get_id_line(path: str, line: str, message: str) -> str:
    lines = Path(path).read_text().splitlines()
    if not lines:
        code = ''
    else:
        code = lines[int(line) - 1]

    return f'{path}:{code}:{message}'


def get_id_lines(lint_output: str, regex: str) -> List[str]:
    return [
        get_id_line(path, line, message)
        for path, line, message
        in re.findall(regex, lint_output)
    ]


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
    digests = {hashlib.md5(id_line.encode('utf-8')).hexdigest() for id_line in id_lines}
    for path, line, message in re.findall(lint_format, sys.stdin.read()):
        id_line = get_id_line(path, line, message)
        digest = hashlib.md5(id_line.encode('utf-8')).hexdigest()
        if digest not in digests:
            print(id_line)
            has_errors = True
    if has_errors:
        sys.exit(1)


if __name__ == '__main__':
    cli()
