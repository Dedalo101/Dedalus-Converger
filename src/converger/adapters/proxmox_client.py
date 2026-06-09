from typing import Any, Dict


class ProxmoxClientError(Exception):
    pass


def create_api(config: Dict[str, Any]):
    try:
        from proxmoxer import ProxmoxAPI
    except ImportError as exc:
        raise ProxmoxClientError(
            "proxmoxer is required for live Proxmox operations"
        ) from exc

    return ProxmoxAPI(
        config["host"],
        user=config["user"],
        token_name=config["token_name"],
        token_value=config["token_value"],
        verify_ssl=bool(config.get("verify_ssl", False)),
    )


def resolve_node(api, config: Dict[str, Any]) -> str:
    node = config.get("node")
    if node:
        return node

    nodes = api.nodes.get()
    if not nodes:
        raise ProxmoxClientError("No Proxmox nodes available")
    return nodes[0]["node"]


def resolve_vm_node(api, vmid: int, preferred_node: str | None) -> str:
    if preferred_node:
        return preferred_node

    for node_info in api.nodes.get():
        node = node_info["node"]
        vms = api.nodes(node).qemu.get()
        if any(int(vm["vmid"]) == vmid for vm in vms):
            return node

    raise ProxmoxClientError(f"VM {vmid} not found on any Proxmox node")
