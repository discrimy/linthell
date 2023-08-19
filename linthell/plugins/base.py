import abc
import sys
from typing import List, Optional, Set, cast

if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
    from importlib_metadata import EntryPoints
else:
    from importlib.metadata import entry_points
    from importlib.metadata import EntryPoints

from linthell.utils.types import LinterError


class LinthellPlugin(abc.ABC):
    @abc.abstractmethod
    def parse(self, linter_output: str) -> List[LinterError]:
        ...


def get_available_plugins() -> EntryPoints:
    plugins = cast(EntryPoints, entry_points(group='linthell.plugins'))
    return plugins


def load_plugin_by_name(name: str) -> LinthellPlugin:
    plugins = entry_points(group='linthell.plugins')
    try:
        plugin_class = plugins[name].load()
    except KeyError as error:
        raise ValueError(f"Cannot find plugin {name}") from error
    return plugin_class()
