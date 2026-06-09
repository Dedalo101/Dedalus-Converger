from typing import List

from ..model import VMState
from .base import ObservationAdapter, ObservationError
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
            from proxmoxer import ProxmoxAPI
        except ImportError as exc:
            raise ObservationError(
                "proxmoxer is required for live Proxmox observation"
            ) from exc

        api = ProxmoxAPI(
            self.config["host"],
            user=self.config["user"],
            token_name=self.config["token_name"],
            token_value=self.config["token_value"],
            verify_ssl=bool(self.config.get("verify_ssl", False)),
        )

        node = self.config.get("node")
        if not node:
            nodes = api.nodes.get()
            if not nodes:
                raise ObservationError("No Proxmox nodes available")
            node = nodes[0]["node"]

        try:
            qemu_vms = api.nodes(node).qemu.get()
        except Exception as exc:
            raise ObservationError(
                f"Proxmox observation failed for node {node}: {exc}"
            ) from exc

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
                )
            )

        return states


AdapterRegistry.register(ProxmoxAdapter)
