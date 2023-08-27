import abc
import sys
from typing import List, cast

if sys.version_info < (3, 10):
    from importlib_metadata import EntryPoints, entry_points
else:
    from importlib.metadata import EntryPoints, entry_points

from linthell.utils.types import LinterError


class LinthellPlugin(abc.ABC):
    """Linthell plugin base class."""

    @abc.abstractmethod
    def parse(self, linter_output: str) -> List[LinterError]:
        """Parse linter output to list of linter errors."""
        ...


def get_available_plugins() -> EntryPoints:
    """Get available linthell plugins."""
    plugins = cast(EntryPoints, entry_points(group='linthell.plugins'))
    return plugins


def load_plugin_by_name(name: str) -> LinthellPlugin:
    """Load class plugin by it's plugin name."""
    plugins = entry_points(group='linthell.plugins')
    try:
        plugin_class = plugins[name].load()
    except KeyError as error:
        raise ValueError(f"Cannot find plugin {name}") from error
    return plugin_class()
