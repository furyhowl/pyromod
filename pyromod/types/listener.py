from asyncio import Future
from dataclasses import dataclass
from typing import Callable

from hydrogram.filters import Filter

from pyromod.types.identifier import Identifier
from pyromod.types.listener_types import ListenerTypes


@dataclass
class Listener:
    listener_type: ListenerTypes
    filters: Filter
    unallowed_click_alert: bool
    identifier: Identifier
    future: Future = None
    callback: Callable = None
