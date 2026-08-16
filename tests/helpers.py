import os
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path


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
