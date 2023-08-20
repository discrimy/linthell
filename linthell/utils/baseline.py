from pathlib import Path
from typing import List, Set
from linthell.plugins.base import LinthellPlugin

from linthell.utils.id_lines import id_line_to_digest
from linthell.utils.types import IdLine


def get_digests_from_baseline(baseline_file: Path) -> Set[str]:
    """Get digests from provided baseline file."""
    id_lines = Path(baseline_file).read_text().splitlines()
    digests = {id_line_to_digest(id_line) for id_line in id_lines}
    return digests


def generate_baseline(
    linter_output: str, plugin: LinthellPlugin
) -> List[IdLine]:
    """Generate id lines based on linter output."""
    return [
        linter_error.id_line for linter_error in plugin.parse(linter_output)
    ]


def save_baseline(baseline_file: Path, id_lines: List[IdLine]) -> None:
    """Save id lines into baseline file."""
    baseline_file.write_text('\n'.join(sorted(id_lines)))
