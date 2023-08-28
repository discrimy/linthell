import re
from enum import Enum
from typing import List, Optional

from typing_extensions import assert_never

from linthell.plugins.base import LinthellPlugin
from linthell.utils.types import LinterError

_OLD_VERSION_FILE_PATH_SIGN = '--- '
_NEW_VERSION_FILE_PATH_SIGN = '+++ '
_FILE_PATH_SIGNS = (_OLD_VERSION_FILE_PATH_SIGN, _NEW_VERSION_FILE_PATH_SIGN)
_FILE_PATH_PATTERN = re.compile(r'(?:-{3}|\+{3})\s(?P<file_path>[\w/.-]+).*')
"""Example: --- package/module.py 2023-08-24 09:29:48.256318 +0000"""
_LINE_NUMBER_SIGN = '@'
_LINE_NUMBER_PATTERN = re.compile(
    r'@@ -(?P<old_file_version_line_number>\d+)(,\d+)?'
    r' \+(?P<new_file_version_line_number>\d+)(,\d+)? @@'
)
"""Example: @@ -10,20 +10,20 @@"""
_REMOVE_LINE_SIGN = '-'
"""Example: -    def_param: bool = True"""
_ADD_LINE_SIGN = '+'
"""Example: +    def_param: bool = True,"""
_KEEP_LINE_SIGN = ' '
"""Example:      def_param: bool = True,"""


class _FileVersion(Enum):
    """Enumeration of file versions represented in black output."""

    OLD = 'old'
    NEW = 'new'


class BlackOutputInvalidError(Exception):
    """Base error of invalid black-diff output.

    Used to encapsulate logic of building an error message.
    Allows to set `DEFAULT_MSG` for subclasses.
    """

    DEFAULT_MSG: str = 'no detail'

    def __init__(self, line: str, msg: Optional[str] = None) -> None:
        """Initialize exception instance.

        :param line: line of black-diff output.
        :param msg: verbose message of error.
                    If not passed `self.DEFAULT_MSG` is used.
        """
        self.line = line
        self.msg = msg or self.DEFAULT_MSG

    def __str__(self):
        return f'Invalid black-diff output ({self.msg}): {self.line}'


class BlackOutputInvalidFilePathLineError(BlackOutputInvalidError):
    """Error of black-diff output. Invalid line with file path.

    Raised if line expected to contain file path but doesn't match pattern.
    """

    DEFAULT_MSG = (
        'expected line to contain file path '
        'but it does not match expected pattern'
    )


class BlackOutputInvalidLineNumberLineError(BlackOutputInvalidError):
    """Error of black-diff output. Invalid line with line numbers.

    Raised if line expected to contain line numbers but doesn't match pattern.
    """

    DEFAULT_MSG = (
        'expected line to contain line number '
        'but it does not match expected pattern'
    )


class BlackOutputInvalidLineOrderError(BlackOutputInvalidError):
    """Error of black-diff output. Invalid line order.

    Raised if expected to face lines with file path and line numbers before
    current in-process line.
    """

    DEFAULT_MSG = (
        'expected lines with file path and line number before lines with code'
    )


class LinthellBlackDiffPlugin(LinthellPlugin):
    """Parser for output of command: 'black --diff --check [path,]*'.

    Parser reformats the output to contain only required
    information in one line: file path, line number, line of code.

    It allows to use black with higher error restrictions than
    `BlackCheck` does. Since BlackCheck suppresses any new error in
    a file (if that file is covered by baseline) and this Plugin suppress error
    on specific line of specific file.

    # DEV NOTES

    Example of output. Black used against code that misses empty line
    before `def` and uses magic-comma but `*args` is not moved to spared line:
        --- /home/user/package/module.py    2023-08-24 18:03:29.245834 +0000
        +++ /home/user/package/module.py    2023-08-24 18:03:30.951316 +0000
        @@ -1,3 +1,7 @@
        import re

        -def func(*args,):
        +
        +def func(
        +    *args,
        +):
             pass

    Most important part of the output is that there are two versions of files
    where (excluding special lines that starts with @@, --- or +++):
    - lines that start with ' ' are present in both versions
    - lines that start with '-' are present in old version only
    - lines that start with '+' are present in new version only

    Parser memorize last know file path, parses line numbers
    and increases that line number with each passed line.
    That gives possibility to build output that contains all required parts
    in one line: file path, line number, line of code.

    Because of the format of output Parser is initialized in-process,
    line by line, and that behavior may lead to partial-initialized problems.
    Trying to keep code safe Parser validates all expected initialization
    before any step so if it faces and unexpected state an error is raised
    immediately preventing broken baseline or linter's output.
    """

    def __init__(self) -> None:  # noqa: D107
        self.file_path: Optional[str] = None
        self.old_file_version_line_number: Optional[int] = None
        self.new_file_version_line_number: Optional[int] = None
        self.errors: List[LinterError] = []

    def parse(self, linter_output: str) -> List[LinterError]:
        """Entry point for linthell.

        :param linter_output: complete output of 'black --diff --check ...'
        :return: List of found LinterError representing black-output

        :raise BlackOutputInvalidError: on any unexpected output or it's order
        """
        for line in linter_output.splitlines():
            if line.startswith(_FILE_PATH_SIGNS):
                self._parse_file_path(line)
            elif line.startswith(_LINE_NUMBER_SIGN):
                self._parse_line_number(line)
            elif line.startswith((_REMOVE_LINE_SIGN, _ADD_LINE_SIGN)):
                file_version = (
                    _FileVersion.OLD
                    if line.startswith(_REMOVE_LINE_SIGN)
                    else _FileVersion.NEW
                )

                self._append_errors(line=line, file_version=file_version)
                self._incr_line_num(line=line, file_version=file_version)
            elif line.startswith(_KEEP_LINE_SIGN):
                self._incr_line_num(line=line, file_version=_FileVersion.OLD)
                self._incr_line_num(line=line, file_version=_FileVersion.NEW)

        return self.errors

    def _parse_file_path(self, line: str) -> None:
        """Parse file path from black output that starts with --- or +++."""
        file_path_match = _FILE_PATH_PATTERN.fullmatch(line)
        if not file_path_match:
            raise BlackOutputInvalidFilePathLineError(line=line)

        self.file_path = file_path_match.group('file_path')

    def _parse_line_number(self, line: str) -> None:
        """Parse line numbers from black output that starts with @."""
        line_number_match = _LINE_NUMBER_PATTERN.fullmatch(line)
        if not line_number_match:
            raise BlackOutputInvalidLineNumberLineError(line=line)

        self.old_file_version_line_number = int(
            line_number_match.group('old_file_version_line_number')
        )
        self.new_file_version_line_number = int(
            line_number_match.group('new_file_version_line_number')
        )

    def _append_errors(self, line: str, file_version: _FileVersion) -> None:
        """Append errors.

        LinterError created based on current state and passed argument
        """
        if file_version is _FileVersion.OLD:
            line_number = self.old_file_version_line_number
        elif file_version is _FileVersion.NEW:
            line_number = self.new_file_version_line_number
        else:
            assert_never(file_version)

        if self.file_path is None or line_number is None:
            raise BlackOutputInvalidLineOrderError(line=line)

        self.errors.append(
            LinterError(
                id_line=f'{self.file_path}:{line}',
                error_message=f'{self.file_path}:{line_number}: {line}',
            ),
        )

    def _incr_line_num(
        self,
        line: str,
        file_version: _FileVersion,
    ) -> None:
        """Increment line number corresponding to file_version.

        :param line: used only in case of error
        :param file_version: affects which attribute would be incremented
        """
        if file_version is _FileVersion.OLD:
            if self.old_file_version_line_number is None:
                raise BlackOutputInvalidLineOrderError(line=line)
            self.old_file_version_line_number += 1
        elif file_version is _FileVersion.NEW:
            if self.new_file_version_line_number is None:
                raise BlackOutputInvalidLineOrderError(line=line)
            self.new_file_version_line_number += 1
        else:
            assert_never(file_version)
