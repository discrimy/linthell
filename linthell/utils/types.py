from dataclasses import dataclass

IdLine = str
Digest = str


@dataclass(frozen=True)
class LinterError:
    id_line: IdLine
    error_message: str
