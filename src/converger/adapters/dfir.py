import json
from typing import Any, Dict, List

from ..model import VMState
from ..schema import SchemaValidationError, validate_replay_payload
from .base import ObservationAdapter, ObservationError
from .registry import AdapterRegistry

_DEFAULT_FIELD_MAP = {
    "vmid": "vmid",
    "name": "name",
    "status": "status",
    "cpus": "cpus",
    "maxmem": "maxmem",
    "node": "node",
}

_ENVELOPE_KEYS = ("systems", "entities", "hosts", "vms", "machines")


class DfirAdapter(ObservationAdapter):
    name = "dfir"
    required_config_keys = {"path"}

    def observe(self) -> List[VMState]:
        path = self.config["path"]
        try:
            with open(path, encoding="utf-8") as handle:
                payload = json.load(handle)
        except FileNotFoundError as exc:
            raise ObservationError(f"DFIR file not found: {path}") from exc
        except json.JSONDecodeError as exc:
            raise ObservationError(f"DFIR file is not valid JSON: {path}") from exc

        normalized = self._normalize_payload(payload)
        try:
            validated = validate_replay_payload(normalized)
        except SchemaValidationError as exc:
            raise ObservationError(str(exc)) from exc

        return [
            VMState(
                vmid=item["vmid"],
                name=item["name"],
                status=item["status"],
                cpus=item.get("cpus"),
                maxmem=item.get("maxmem"),
                source="dfir",
                node=item.get("node"),
            )
            for item in validated
        ]

    def _normalize_payload(self, payload: Any) -> List[Dict[str, Any]]:
        fmt = self.config.get("format", "auto")
        if isinstance(payload, list):
            return self._normalize_entities(payload)

        if not isinstance(payload, dict):
            raise ObservationError("DFIR payload must be a JSON array or object")

        if fmt != "envelope":
            for key in _ENVELOPE_KEYS:
                if key in payload and isinstance(payload[key], list):
                    return self._normalize_entities(payload[key])

        entities_key = self.config.get("entities_key", "systems")
        entities = payload.get(entities_key)
        if not isinstance(entities, list):
            raise ObservationError(
                f"DFIR envelope must contain a list under {entities_key!r}"
            )
        return self._normalize_entities(entities)

    def _normalize_entities(self, entities: List[Any]) -> List[Dict[str, Any]]:
        field_map = {**_DEFAULT_FIELD_MAP, **self.config.get("field_map", {})}
        status_map = self.config.get("status_map", {})

        normalized: List[Dict[str, Any]] = []
        for index, entity in enumerate(entities):
            if not isinstance(entity, dict):
                raise ObservationError(f"DFIR entity {index} must be an object")

            if _is_native_entity(entity):
                normalized.append(
                    {
                        "vmid": int(entity["vmid"]),
                        "name": str(entity.get("name", f"entity-{entity['vmid']}")),
                        "status": entity["status"],
                        "cpus": entity.get("cpus"),
                        "maxmem": entity.get("maxmem"),
                        "source": "dfir",
                        "node": entity.get("node"),
                    }
                )
                continue

            raw_status = _get_field(entity, field_map["status"])
            mapped_status = status_map.get(
                str(raw_status).lower(), str(raw_status).lower()
            )
            if mapped_status not in {"running", "stopped", "unknown"}:
                mapped_status = "unknown"

            normalized.append(
                {
                    "vmid": int(_get_field(entity, field_map["vmid"])),
                    "name": str(
                        _get_field(entity, field_map["name"], default=f"entity-{index}")
                    ),
                    "status": mapped_status,
                    "cpus": _optional_field(entity, field_map.get("cpus")),
                    "maxmem": _optional_field(entity, field_map.get("maxmem")),
                    "source": "dfir",
                    "node": _optional_field(entity, field_map.get("node")),
                }
            )

        return normalized


def _is_native_entity(entity: dict) -> bool:
    return (
        "vmid" in entity
        and "status" in entity
        and entity["status"] in {"running", "stopped", "unknown"}
    )


def _get_field(entity: dict, field_name: str | None, default: Any = None) -> Any:
    if not field_name or field_name not in entity:
        if default is not None:
            return default
        raise ObservationError(f"DFIR entity missing required field {field_name!r}")
    return entity[field_name]


def _optional_field(entity: dict, field_name: str | None) -> Any:
    if not field_name or field_name not in entity:
        return None
    return entity[field_name]


AdapterRegistry.register(DfirAdapter)
