import json
from pathlib import Path

from converger.adapters.dfir import DfirAdapter
from converger.cli import cli
from click.testing import CliRunner


def test_dfir_adapter_maps_envelope_fields(tmp_path: Path):
    payload = {
        "systems": [
            {
                "id": 100,
                "hostname": "web-01",
                "power_state": "off",
                "cpu_count": 2,
                "ram_bytes": 4096,
                "site": "pve1",
            }
        ]
    }
    path = tmp_path / "dfir.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    adapter = DfirAdapter(
        {
            "path": str(path),
            "format": "envelope",
            "entities_key": "systems",
            "field_map": {
                "vmid": "id",
                "name": "hostname",
                "status": "power_state",
                "cpus": "cpu_count",
                "maxmem": "ram_bytes",
                "node": "site",
            },
            "status_map": {"on": "running", "off": "stopped"},
        }
    )
    states = adapter.observe()
    assert len(states) == 1
    assert states[0].vmid == 100
    assert states[0].name == "web-01"
    assert states[0].status == "stopped"
    assert states[0].source == "dfir"


def test_plan_with_dfir_example():
    runner = CliRunner()
    config_file = Path("examples/converger.dfir.yaml.example")
    result = runner.invoke(
        cli,
        [
            "-c",
            str(config_file),
            "plan",
            "--desired",
            "examples/desired.yaml",
            "--dfir",
            "examples/dfir_systems.json",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "Observation (dfir)" in result.output
