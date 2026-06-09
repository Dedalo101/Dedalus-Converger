from typing import List, Optional

from .adapters import AdapterRegistry
from .adapters import aws  # noqa: F401 - register adapter
from .adapters import dfir  # noqa: F401 - register adapter
from .adapters import hetzner  # noqa: F401 - register adapter
from .adapters import proxmox  # noqa: F401 - register adapter
from .adapters import replay  # noqa: F401 - register adapter
from .config import ConvergerConfig, adapter_config_for_source
from .model import VMState


def observe(source: str, config: Optional[dict] = None) -> List[VMState]:
    """Observe reality through a registered adapter without retries or discovery."""
    adapter_cls = AdapterRegistry.get(source)
    adapter = adapter_cls(config or {})
    return adapter.observe()


def observe_from_config(
    config: ConvergerConfig,
    *,
    source: Optional[str] = None,
    replay_path: Optional[str] = None,
    dfir_path: Optional[str] = None,
) -> tuple[List[VMState], str]:
    resolved_source = source or config.source
    if replay_path:
        resolved_source = "replay"
    elif dfir_path:
        resolved_source = "dfir"

    adapter_config = adapter_config_for_source(
        config,
        resolved_source,
        replay_path=replay_path,
        dfir_path=dfir_path,
    )
    return observe(resolved_source, adapter_config), resolved_source


def observe_replay(path: str) -> List[VMState]:
    return observe("replay", {"path": path})


def observe_live(config: Optional[dict] = None) -> List[VMState]:
    return observe("proxmox", config or {})
