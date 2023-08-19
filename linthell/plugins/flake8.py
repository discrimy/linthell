from linthell.plugins.regex import LinthellRegexPlugin


class LinthellFlake8Plugin(LinthellRegexPlugin):
    """Linthell plugin for flake8."""

    def __init__(self) -> None:  # noqa: D107
        super().__init__(
            lint_format=r'(?P<path>.+):(?P<line>\d+):\d+: (?P<message>.+)'
        )
