"""Main CLI module."""

from configparser import ConfigParser
from contextlib import suppress
from typing import Optional

import click

from linthell.commands.lint import lint_cli
from linthell.commands.baseline import baseline_cli
from linthell.utils.config import create_config_dict


@click.group()
@click.option(
    '--config',
    'config_path',
    help=(
        'Path to .ini config file. "common" section applies for all commands, '
        'command specific config are specified by their name section, '
        'for example "lint". Keys must have same name as argument name of '
        'their command function. For example, "baseline_file".'
    ),
    type=click.Path(dir_okay=False),
)
@click.pass_context
def cli(ctx: click.Context, config_path: Optional[str]) -> None:
    """Universal flakehell replacement for almost any linter you like.

    The main concept of this tool is baseline file. It contains all errors
    that should be ignored and be fixed later. After baseline is generated,
    all errors inside this file are ignored but new ones not, so you can adapt
    new linter smoothly without fixing old code. To generate and use baseline,
    you should provide the path to this file, linter output and regex to parse
    it. Regex must contain three named groups `path`, `line` and `message`
    and must be the same in `baseline` and `lint` commands of the same baseline
    file and linter.

    Workflow looks like this: at first, create baseline for each linter
    you use. Then replace calls your linter with piping their results
    to `linthell lint` command.

    Example:
    $ <your linter> | linthell baseline -b baseline.ini -f <regex to parse>
    $ <your linter> | linthell lint -b baseline.ini -f <regex to parse>
    """
    if config_path:
        config_parser = ConfigParser()
        config_parser.read(config_path)
        ctx.default_map = create_config_dict(
            config_parser, ctx.command.commands
        )


cli.add_command(lint_cli, 'lint')
cli.add_command(baseline_cli, 'baseline')
with suppress(ImportError):
    from linthell.commands.pre_commit.cli import pre_commit_cli

    cli.add_command(pre_commit_cli, 'pre-commit')
