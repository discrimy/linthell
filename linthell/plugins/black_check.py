import re
from pathlib import Path
from typing import List

from linthell.plugins.base import LinthellPlugin
from linthell.utils.path import normalize_path
from linthell.utils.types import LinterError


class LinthellBlackCheckPlugin(LinthellPlugin):
    """Linthell plugin for black with --check option (show files only)."""

    def parse(self, linter_output: str) -> List[LinterError]:  # noqa D102
        errors = []
        for match in re.finditer(r'would reformat (.+)', linter_output):
            file_path = match.group(1)
            message = match.group(0)
            id_line = normalize_path(Path(file_path))
            errors.append(LinterError(id_line, message))
        return errors
