import json
from typing import List

from ..model import VMState
from ..schema import SchemaValidationError, validate_replay_payload
from .base import ObservationAdapter, ObservationError
from .registry import AdapterRegistry


class ReplayAdapter(ObservationAdapter):
    name = "replay"
    required_config_keys = {"path"}

    def observe(self) -> List[VMState]:
        path = self.config["path"]
        try:
            with open(path, encoding="utf-8") as handle:
                payload = json.load(handle)
        except FileNotFoundError as exc:
            raise ObservationError(f"Replay file not found: {path}") from exc
        except json.JSONDecodeError as exc:
            raise ObservationError(f"Replay file is not valid JSON: {path}") from exc

        try:
            validated = validate_replay_payload(payload)
        except SchemaValidationError as exc:
            raise ObservationError(str(exc)) from exc

        return [
            VMState(
                vmid=item["vmid"],
                name=item["name"],
                status=item["status"],
                cpus=item.get("cpus"),
                maxmem=item.get("maxmem"),
                source=item.get("source", "replay"),
                node=item.get("node"),
                external_id=item.get("external_id"),
                instance_type=item.get("instance_type"),
                server_type=item.get("server_type"),
            )
            for item in validated
        ]


AdapterRegistry.register(ReplayAdapter)
