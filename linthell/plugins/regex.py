import linecache
from pathlib import Path
import re
from typing import List
from linthell.plugins.base import LinthellPlugin
from linthell.utils.types import IdLine, LinterError


def get_id_line(path: str, line: str, message: str) -> IdLine:
    """Convert path, line and message to id line (path:code_line:message)."""
    code = ''
    if line:
        line_int = int(line)
        code = linecache.getline(path, line_int).rstrip('\n')
    normalized_path = Path(path).as_posix()
    return f'{normalized_path}:{code}:{message}'


class LinthellRegexPlugin(LinthellPlugin):
    def __init__(self, lint_format: str) -> None:
        super().__init__()
        self.lint_format = lint_format

    def parse(self, linter_output: str) -> List[LinterError]:
        errors = []
        for match in re.finditer(self.lint_format, linter_output):
            path = match.groupdict()['path']
            line = match.groupdict()['line']
            message = match.groupdict()['message']
            lint_message = match.group(0)
            id_line = get_id_line(path, line, message)
            errors.append(LinterError(id_line, lint_message))
        return errors
