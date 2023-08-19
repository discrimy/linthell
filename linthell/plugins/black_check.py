import re
from typing import List
from linthell.plugins.base import LinthellPlugin
from linthell.utils.types import LinterError


class LinthellBlackCheckPlugin(LinthellPlugin):
    def parse(self, linter_output: str) -> List[LinterError]:
        errors = []
        for match in re.finditer(r'would reformat (.+)', linter_output):
            id_line = match.group(1)
            message = match.group(0)
            errors.append(LinterError(id_line, message))
        return errors
