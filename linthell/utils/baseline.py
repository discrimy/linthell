from pathlib import Path
from typing import List, Set
from linthell.plugins.base import LinthellPlugin

from linthell.utils.id_lines import id_line_to_digest
from linthell.utils.types import IdLine


def get_digests_from_baseline(baseline_file: Path) -> Set[str]:
    """Get digests from provided baseline file."""
    id_lines = load_baseline(baseline_file)
    digests = {id_line_to_digest(id_line) for id_line in id_lines}
    return digests


def generate_baseline(
    linter_output: str, plugin: LinthellPlugin
) -> List[IdLine]:
    """Generate id lines based on linter output."""
    return [
        linter_error.id_line for linter_error in plugin.parse(linter_output)
    ]


def load_baseline(baseline_file: Path) -> List[IdLine]:
    """Load id lines from baseline file. Handles special characters."""
    id_lines_raw = Path(baseline_file).read_text().splitlines()
    id_lines = [
        id_line.encode('utf-8').decode('unicode_escape')
        for id_line in id_lines_raw
    ]
    return id_lines


def save_baseline(baseline_file: Path, id_lines: List[IdLine]) -> None:
    """Save id lines into baseline file. Handles special characters."""
    id_lines_raw = [
        id_line.encode('unicode_escape').decode('utf-8')
        for id_line in id_lines
    ]
    baseline_file.write_text('\n'.join(sorted(id_lines_raw)))
