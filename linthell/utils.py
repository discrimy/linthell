import hashlib
import re
import shlex
import subprocess
from configparser import ConfigParser
from pathlib import Path
from typing import Dict, List, Tuple

from typing_extensions import Literal


def get_id_line(path: str, line: str, message: str) -> str:
    """Convert path, line and message to id line (path:code_line:message)."""
    if not line:
        code = ''
    else:
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


def get_dict_or_empty(config: ConfigParser, section: str) -> Dict[str, str]:
    """Return dict of section or empty dict if section is missing."""
    try:
        return dict(config[section])
    except KeyError:
        return {}


def run_linter_and_get_output(
    linter_command: str,
    files: Tuple[str, ...],
    linter_output: Literal['stdout', 'stderr'],
) -> str:
    linter_process = subprocess.run(
        [*shlex.split(linter_command), *files],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        check=False,
    )
    if linter_output == 'stdout':
        output = linter_process.stdout
    else:
        output = linter_process.stderr
    return output
