from linthell.plugins.regex import LinthellRegexPlugin


class LinthellPydocstylePlugin(LinthellRegexPlugin):
    """Linthell plugin for pydocstyle."""

    def __init__(self) -> None:  # noqa: D107
        super().__init__(
            lint_format=r'(?P<path>.+):(?P<line>\d+).+\n\s+ (?P<message>.+)'
        )
