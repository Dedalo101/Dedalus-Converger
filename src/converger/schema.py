from typing import Any, Dict, List

VALID_STATUSES = {"running", "stopped", "unknown"}
REQUIRED_FIELDS = {"vmid", "name", "status"}


class SchemaValidationError(Exception):
    pass


def validate_replay_payload(payload: Any) -> List[Dict[str, Any]]:
    if not isinstance(payload, list):
        raise SchemaValidationError("Replay payload must be a JSON array")

    validated: List[Dict[str, Any]] = []
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            raise SchemaValidationError(f"Replay entry {index} must be an object")

        missing = REQUIRED_FIELDS - set(item.keys())
        if missing:
            missing_fields = ", ".join(sorted(missing))
            raise SchemaValidationError(
                f"Replay entry {index} missing required fields: {missing_fields}"
            )

        status = item["status"]
        if status not in VALID_STATUSES:
            raise SchemaValidationError(
                f"Replay entry {index} has invalid status {status!r}"
            )

        try:
            vmid = int(item["vmid"])
        except (TypeError, ValueError) as exc:
            raise SchemaValidationError(
                f"Replay entry {index} field 'vmid' must be an integer"
            ) from exc

        validated.append(
            {
                "vmid": vmid,
                "name": str(item["name"]),
                "status": status,
                "cpus": _optional_int(item.get("cpus"), index, "cpus"),
                "maxmem": _optional_int(item.get("maxmem"), index, "maxmem"),
                "source": str(item.get("source", "replay")),
                "node": _optional_str(item.get("node")),
            }
        )

    return validated


def _optional_int(value: Any, index: int, field: str) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise SchemaValidationError(
            f"Replay entry {index} field {field!r} must be an integer"
        ) from exc


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)
