from linthell.plugins.regex import LinthellRegexPlugin


class LinthellMypyPlugin(LinthellRegexPlugin):
    def __init__(self) -> None:
        super().__init__(lint_format = r'(?P<path>.+):(?P<line>\d+): (?P<message>error: .+)(\n\1:\2: note: .+)?')
