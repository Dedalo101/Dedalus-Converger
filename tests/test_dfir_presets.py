from pathlib import Path

from converger.adapters.dfir import DfirAdapter
from converger.cli import cli
from converger.dfir_presets import get_preset, merge_dfir_config
from click.testing import CliRunner


def test_velociraptor_preset_maps_clients():
    preset = get_preset("velociraptor")
    path = Path("examples/dfir/velociraptor_clients.json")
    adapter = DfirAdapter(preset.as_adapter_config(str(path)))
    states = adapter.observe()

    assert len(states) == 2
    assert states[0].vmid == 100
    assert states[0].name == "web-01"
    assert states[0].status == "running"
    assert states[1].status == "stopped"


def test_kape_preset_maps_hosts():
    preset = get_preset("kape")
    path = Path("examples/dfir/kape_hosts.json")
    adapter = DfirAdapter(preset.as_adapter_config(str(path)))
    states = adapter.observe()

    assert len(states) == 2
    assert states[0].name == "WEB-01"
    assert states[0].status == "running"
    assert states[1].status == "stopped"


def test_merge_dfir_config_overrides_preset_fields():
    base = get_preset("velociraptor")
    merged = merge_dfir_config(base, "velociraptor")
    assert merged.entities_key == "items"
    assert merged.field_map["vmid"] == "client_id"


def test_plan_with_velociraptor_preset_cli():
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "plan",
            "--desired",
            "examples/desired.yaml",
            "--dfir",
            "examples/dfir/velociraptor_clients.json",
            "--dfir-preset",
            "velociraptor",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "Observation (dfir)" in result.output
