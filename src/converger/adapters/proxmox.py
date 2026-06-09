from typing import List

from ..model import VMState
from .base import ObservationAdapter, ObservationError
from .proxmox_client import create_api, resolve_node
from .registry import AdapterRegistry

_STATUS_MAP = {
    "running": "running",
    "stopped": "stopped",
}


class ProxmoxAdapter(ObservationAdapter):
    name = "proxmox"
    required_config_keys = {"host", "user", "token_name", "token_value"}

    def observe(self) -> List[VMState]:
        try:
            api = create_api(self.config)
            node = resolve_node(api, self.config)
            qemu_vms = api.nodes(node).qemu.get()
        except Exception as exc:
            raise ObservationError(f"Proxmox observation failed: {exc}") from exc

        states: List[VMState] = []
        for vm in qemu_vms:
            raw_status = vm.get("status")
            mapped = _STATUS_MAP.get(raw_status)
            if mapped is None:
                states.append(
                    VMState(
                        vmid=int(vm["vmid"]),
                        name=str(vm.get("name", f"vm-{vm['vmid']}")),
                        status="unknown",
                        source="live",
                        node=node,
                    )
                )
                continue

            states.append(
                VMState(
                    vmid=int(vm["vmid"]),
                    name=str(vm.get("name", f"vm-{vm['vmid']}")),
                    status=mapped,
                    cpus=vm.get("cpus"),
                    maxmem=vm.get("maxmem"),
                    source="live",
                    node=node,
                )
            )

        return states


AdapterRegistry.register(ProxmoxAdapter)
