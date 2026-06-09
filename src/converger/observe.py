from typing import List, Optional

from .adapters import AdapterRegistry
from .adapters import proxmox  # noqa: F401 - register adapter
from .adapters import replay  # noqa: F401 - register adapter
from .model import VMState


def observe(source: str, config: Optional[dict] = None) -> List[VMState]:
    """Observe reality through a registered adapter without retries or discovery."""
    adapter_cls = AdapterRegistry.get(source)
    adapter = adapter_cls(config or {})
    return adapter.observe()


def observe_replay(path: str) -> List[VMState]:
    return observe("replay", {"path": path})


def observe_live(config: Optional[dict] = None) -> List[VMState]:
    return observe("proxmox", config or {})
