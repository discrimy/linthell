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
    """Lint provided linter output and returns report with found errors.

    :param digests: digests of already known errors
    :param linter_output: whole output of linter
    :param plugin: plugin to use, depends on linter
    :return: report with errors, which wasn't found in digests
    """
    errors = []
    for linter_error in plugin.parse(linter_output):
        digest = id_line_to_digest(linter_error.id_line)
        if digest not in digests:
            errors.append(linter_error.error_message)
    return LintReport(errors)
