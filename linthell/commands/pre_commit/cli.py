"""Pre-commit integration CLI."""

import click

from linthell.commands.pre_commit.baseline import baseline_cli
from linthell.commands.pre_commit.lint import lint_cli


@click.group()
def pre_commit_cli():
    """Commands for pre-commit integration."""
    pass


pre_commit_cli.add_command(lint_cli, 'lint')
pre_commit_cli.add_command(baseline_cli, 'baseline')
