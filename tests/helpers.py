import os
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import List


@contextmanager
def temp_project(files: dict):
    """Create a temporary project directory with specified files.

    files: dict mapping relative file paths to their content strings.
    Creates the directory, writes all files using os.chdir, yields CWD.
    On exit, restores original working directory.

    Usage:
        with temp_project({"foo.py": "import os\\nimport sys\\n"}) as cwd:
            # cwd contains foo.py
            pass
    """
    original_dir = os.getcwd()
    tmpdir = tempfile.mkdtemp()
    tmpdir_path = Path(tmpdir)
    try:
        for rel_path, content in files.items():
            full_path = tmpdir_path / rel_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
        os.chdir(str(tmpdir))
        yield
    finally:
        os.chdir(original_dir)
        # Cleanup the temp directory
        shutil.rmtree(tmpdir, ignore_errors=True)


@contextmanager
def temp_baseline():
    """Create a temp baseline file that auto-cleans up.

    Yields a pathlib.Path to the file.

    Uses mkstemp (not NamedTemporaryFile) because the latter keeps the file
    open for the whole block; on Windows an open file cannot be re-opened for
    writing by the code under test, which would raise PermissionError.
    """
    fd, path = tempfile.mkstemp(suffix=".txt")
    os.close(fd)
    try:
        yield Path(path)
    finally:
        Path(path).unlink(missing_ok=True)


def write_baseline_file(path: str, id_lines: List[str]) -> None:
    """Write baseline file with unicode-escaped format.

    Recreates linthell's save_baseline logic for test setup.
    """
    raw_lines = [line.encode("unicode_escape").decode("utf-8") for line in id_lines]
    Path(path).write_text("\n".join(sorted(raw_lines)))


def read_baseline_file(path: str) -> List[str]:
    """Read baseline file and decode unicode-escaped lines.

    Recreates linthell's load_baseline logic for test assertions.
    """
    raw_lines = Path(path).read_text().splitlines()
    decoded = [line.encode("utf-8").decode("unicode_escape") for line in raw_lines]
    return decoded
