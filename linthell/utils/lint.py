from dataclasses import dataclass
from typing import List, Set

from linthell.plugins.base import LinthellPlugin
from linthell.utils.id_lines import id_line_to_digest


@dataclass
class LintReport:
    """Report from linting."""

    errors: List[str]


def lint(
    digests: Set[str], linter_output: str, plugin: LinthellPlugin
) -> LintReport:
    errors = []
    for linter_error in plugin.parse(linter_output):
        digest = id_line_to_digest(linter_error.id_line)
        if digest not in digests:
            errors.append(linter_error.error_message)
    return LintReport(errors)
