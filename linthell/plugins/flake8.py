from linthell.plugins.regex import LinthellRegexPlugin


class LinthellFlake8Plugin(LinthellRegexPlugin):
    def __init__(self) -> None:
        super().__init__(lint_format = r'(?P<path>.+):(?P<line>\d+):\d+: (?P<message>.+)')
