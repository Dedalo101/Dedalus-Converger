import json
from typing import Any, Dict, List

from ..model import VMState
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

        if not isinstance(payload, list):
            raise ObservationError(
                "Replay payload must be a JSON array of VMState objects"
            )

        states: List[VMState] = []
        for index, item in enumerate(payload):
            if not isinstance(item, dict):
                raise ObservationError(f"Replay entry {index} must be an object")
            try:
                states.append(_vmstate_from_dict(item))
            except (KeyError, TypeError, ValueError) as exc:
                raise ObservationError(
                    f"Replay entry {index} is invalid: {exc}"
                ) from exc

        return states


def _vmstate_from_dict(item: Dict[str, Any]) -> VMState:
    return VMState(
        vmid=int(item["vmid"]),
        name=str(item["name"]),
        status=item["status"],
        cpus=item.get("cpus"),
        maxmem=item.get("maxmem"),
        source=str(item.get("source", "replay")),
    )


AdapterRegistry.register(ReplayAdapter)
