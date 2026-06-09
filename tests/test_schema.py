import pytest

from converger.schema import SchemaValidationError, validate_replay_payload


def test_validate_replay_payload_accepts_valid_entries():
    payload = [
        {
            "vmid": 100,
            "name": "web-01",
            "status": "stopped",
            "cpus": 2,
            "maxmem": 4096,
            "source": "replay",
            "node": "pve1",
        }
    ]
    validated = validate_replay_payload(payload)
    assert validated[0]["vmid"] == 100
    assert validated[0]["node"] == "pve1"


def test_validate_replay_payload_rejects_invalid_status():
    with pytest.raises(SchemaValidationError):
        validate_replay_payload([{"vmid": 100, "name": "web-01", "status": "booting"}])


def test_validate_replay_payload_rejects_missing_fields():
    with pytest.raises(SchemaValidationError):
        validate_replay_payload([{"vmid": 100, "status": "stopped"}])
