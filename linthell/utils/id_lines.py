"""Utilities for ID Lines and digests conversions."""

import hashlib

from linthell.utils.types import Digest, IdLine


def id_line_to_digest(id_line: IdLine) -> Digest:
    """Convert MD5 hash as hex from utf-8 id line."""
    return hashlib.md5(id_line.encode('utf-8')).hexdigest()
