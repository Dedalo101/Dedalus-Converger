import json
import urllib.error
import urllib.parse
import urllib.request
from typing import List

from ..model import VMState
from .base import ObservationAdapter, ObservationError
from .registry import AdapterRegistry

_HETZNER_RUNNING = {"running"}
_HETZNER_STOPPED = {"off"}
_HETZNER_UNKNOWN = {"starting", "stopping", "rebuilding", "migrating", "unknown"}


def _map_hetzner_status(raw: str) -> str:
    normalized = raw.lower()
    if normalized in _HETZNER_RUNNING:
        return "running"
    if normalized in _HETZNER_STOPPED:
        return "stopped"
    if normalized in _HETZNER_UNKNOWN:
        return "unknown"
    return "unknown"


class HetznerAdapter(ObservationAdapter):
    name = "hetzner"
    required_config_keys = {"api_token"}

    def observe(self) -> List[VMState]:
        servers = self._fetch_servers()
        states: List[VMState] = []

        for server in servers:
            server_type = server.get("server_type") or {}
            server_type_name = server_type.get("name")
            states.append(
                VMState(
                    vmid=int(server["id"]),
                    name=str(server.get("name", f"hetzner-{server['id']}")),
                    status=_map_hetzner_status(server.get("status", "unknown")),
                    cpus=server_type.get("cores"),
                    maxmem=(
                        server_type.get("memory") * 1024**3
                        if server_type.get("memory")
                        else None
                    ),
                    source="hetzner",
                    node=server.get("datacenter", {}).get("name"),
                    external_id=str(server["id"]),
                    server_type=server_type_name,
                )
            )

        return states

    def _fetch_servers(self) -> list:
        params = {}
        label_selector = self.config.get("label_selector")
        if label_selector:
            params["label_selector"] = label_selector

        query = f"?{urllib.parse.urlencode(params)}" if params else ""
        request = urllib.request.Request(
            f"https://api.hetzner.cloud/v1/servers{query}",
            headers={
                "Authorization": f"Bearer {self.config['api_token']}",
                "Content-Type": "application/json",
            },
            method="GET",
        )

        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise ObservationError(f"Hetzner API error {exc.code}: {body}") from exc
        except Exception as exc:
            raise ObservationError(f"Hetzner observation failed: {exc}") from exc

        servers = payload.get("servers")
        if not isinstance(servers, list):
            raise ObservationError("Hetzner API returned unexpected payload")

        return servers


AdapterRegistry.register(HetznerAdapter)
