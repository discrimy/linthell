"""Utilities for ID Lines and digests conversions."""

import hashlib
import re
from pathlib import Path
from typing import List


def get_id_line(path: str, line: str, message: str) -> str:
    """Convert path, line and message to id line (path:code_line:message)."""
    code = ''
    if line:
        lines = Path(path).read_text().splitlines()
        if lines:
            try:
                code = lines[int(line) - 1]
            except IndexError:
                # https://github.com/discrimy/linthell/issues/2
                code = lines[-1]
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
