"""Pre-commit integration utilities."""

from typing import Tuple

from pre_commit.clientlib import load_config
from pre_commit.commands.run import Classifier
from pre_commit.git import get_all_files
from pre_commit.repository import all_hooks
from pre_commit.store import Store


def get_all_files_by_hook(config_file: str, hook_name: str) -> Tuple[str, ...]:
    """Get all files that hook checks (simular to --all behaviour).

    Based on pre-commit hook internals, so might not work on some version of
    pre-commit. Report an author about it (with pre-commit and linthell
    versions).
    """
    config = load_config(config_file)
    classifier = Classifier.from_config(
        filenames=get_all_files(),
        include=config['files'],
        exclude=config['exclude'],
    )
    store = Store()
    hooks = [
        hook for hook in all_hooks(config, store) if hook.name == hook_name
    ]
    if not hooks:
        raise ValueError(f'Unknown hook name: {hook_name}')
    [hook] = hooks
    filenames = classifier.filenames_for_hook(hook)
    return filenames
