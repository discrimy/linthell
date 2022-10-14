from configparser import ConfigParser
from typing import Optional

import click

from linthell.utils import get_dict_or_empty


@click.group()
@click.option(
    '--config',
    'config_path',
    help=(
        'Path to .ini config file. "common" section applies for all commands, '
        'command specific config are specified by their name section, '
        'for example "lint". Keys must have same name as argument name of'
        'their command function. For example, "baseline_file".'
    ),
    type=click.Path(dir_okay=False),
)
@click.pass_context
def cli(ctx: click.Context, config_path: Optional[str]) -> None:
    """Universal flakehell replacement for almost any linter you like.

    The main concept of this tool is baseline file. It contains all errors
    that should be ignored and be fixed later. After baseline is generated,
    all errors inside this file are ignored but new ones not. So you can adapt
    new linter smoothly without fixing old code. To generate and use baseline,
    you should provide the path to this file, linter output and regex to parse
    it. Regex must contain three named groups `path`, `line` and `message`
    and must be the same in `baseline` and `lint` commands of the same baseline
    file and linter.

    Workflow looks like this: at first, create baseline for each linter
    you use. Then replace calls your linter with piping their results
    to `linthell lint` command.
    """
    if config_path:
        command_name = ctx.invoked_subcommand
        config = ConfigParser()
        config.read(config_path)
        common_section = get_dict_or_empty(config, 'common')
        default_map = {
            command_name: {
                **common_section,
                **get_dict_or_empty(config, command_name),
            }
        }
        ctx.default_map = default_map
