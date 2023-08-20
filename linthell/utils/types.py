from dataclasses import dataclass

# unique identifier of the error
# For example, this can be combination of filename, code line and message.
# Is needed to identify error even source code changed
# (line was moved, surrounding code was edited, etc.)
IdLine = str
# Hash of id line, is used to compare saved errors with current ones
Digest = str


@dataclass(frozen=True)
class LinterError:
    """Linter error in terms of linthell's vision."""

    id_line: IdLine
    error_message: str
