from pathlib import Path


def normalize_path(path: Path) -> str:
    """Normalize provided Path.

    Normalized path is POSIX complaint path as string,
    relative to project root. For absolute paths
    project root is working directory, relative paths
    doesn't change.
    """
    if path.is_absolute():
        path = path.relative_to(Path.cwd())
    return path.as_posix()
