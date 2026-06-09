from converger.adapters.proxmox_apply import ProxmoxApplier
from converger.model import PlanStep


def test_dry_run_records_api_calls_without_execution():
    applier = ProxmoxApplier(
        {
            "host": "pve.local",
            "user": "root@pam",
            "token_name": "converger",
            "token_value": "secret",
            "node": "pve1",
        },
        dry_run=True,
    )
    steps = [
        PlanStep(
            vmid=100,
            name="web-01",
            action="start",
            reason="start",
            node="pve1",
        ),
        PlanStep(
            vmid=101,
            name="dev-api-01",
            action="resize",
            reason="resize",
            node="pve1",
            target_cpus=8,
            target_memory=17179869184,
        ),
    ]

    results = applier.apply(steps)
    assert results[0]["status"] == "dry_run"
    assert results[0]["api_call"]["method"] == "POST"
    assert "status/start" in results[0]["api_call"]["path"]
    assert results[1]["api_call"]["method"] == "PUT"
    assert results[1]["api_call"]["body"]["cores"] == 8
