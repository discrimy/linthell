from linthell.plugins.regex import LinthellRegexPlugin


class LinthellPylintPlugin(LinthellRegexPlugin):
    """Linthell plugin for pylint."""

    def __init__(self) -> None:  # noqa: D107
        lint_format = r'(?P<path>.+):(?P<line>\d+):\d+: (?P<message>.+): .+'  # noqa: E501
        super().__init__(lint_format=lint_format)
