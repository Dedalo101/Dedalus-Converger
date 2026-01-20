from typing import List
from .model import VMState

def observe_live() -> List[VMState]:
    # TODO: Proxmox impl (no retries, honest failure)
    return []  # Refuse incomplete by default
