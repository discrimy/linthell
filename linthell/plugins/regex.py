import linecache
import re
from pathlib import Path
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
    """Linthell plugin which uses regex to extract errors.

    Regex must contains named groups:
    - path - path to file relative to project root
    - line - line number of code inside file
    - message - error message, provided by linter, usually
    some code or explanation

    Also whole regex match should match to whole error message of linter
    and will be returned as LinterError.error_message
    """

    def __init__(self, lint_format: str) -> None:  # noqa: D107
        super().__init__()
        self.lint_format = lint_format

    def parse(self, linter_output: str) -> List[LinterError]:
        """Parse linter output to list of linter errors."""
        errors = []
        for match in re.finditer(self.lint_format, linter_output):
            path = match.groupdict()['path']
            line = match.groupdict()['line']
            message = match.groupdict()['message']
            lint_message = match.group(0)
            id_line = get_id_line(path, line, message)
            errors.append(LinterError(id_line, lint_message))
        return errors
