from linthell.plugins.regex import LinthellRegexPlugin


class LinthellPydocstylePlugin(LinthellRegexPlugin):
    def __init__(self) -> None:
        super().__init__(lint_format = r'(?P<path>.+):(?P<line>\d+).+\n\s+ (?P<message>.+)')
