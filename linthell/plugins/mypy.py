from linthell.plugins.regex import LinthellRegexPlugin


class LinthellMypyPlugin(LinthellRegexPlugin):
    """Linthell plugin for mypy."""

    def __init__(self) -> None:  # noqa: D107
        lint_format = r'(?P<path>.+):(?P<line>\d+): (?P<message>error: .+)(\n\1:\2: note: .+)?'  # noqa: E501
        super().__init__(lint_format=lint_format)
