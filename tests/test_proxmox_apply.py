from unittest.mock import MagicMock, patch

from converger.adapters.proxmox_apply import ProxmoxApplier
from converger.model import PlanStep


def _config():
    return {
        "host": "pve.local",
        "user": "root@pam",
        "token_name": "converger",
        "token_value": "secret",
        "node": "pve1",
    }


@patch("converger.adapters.proxmox_apply.create_api")
def test_apply_start_and_stop(mock_create_api):  # noqa: ARG001
    api = MagicMock()
    mock_create_api.return_value = api
    api.nodes.return_value.qemu.return_value.status.start.post.return_value = None
    api.nodes.return_value.qemu.return_value.status.stop.post.return_value = None

    applier = ProxmoxApplier(_config())
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
            name="dev-01",
            action="stop",
            reason="stop",
            node="pve1",
        ),
    ]

    results = applier.apply(steps)
    assert results[0]["status"] == "applied"
    assert results[1]["status"] == "applied"
    api.nodes.assert_any_call("pve1")


@patch("converger.adapters.proxmox_apply.create_api")
def test_apply_resize(mock_create_api):
    api = MagicMock()
    mock_create_api.return_value = api

    applier = ProxmoxApplier(_config())
    steps = [
        PlanStep(
            vmid=101,
            name="dev-api-01",
            action="resize",
            reason="cpus 4 -> 8",
            node="pve1",
            target_cpus=8,
            target_memory=17179869184,
        )
    ]

    results = applier.apply(steps)
    assert results[0]["status"] == "applied"
    api.nodes("pve1").qemu(101).config.put.assert_called_once_with(
        cores=8, memory=17179869184
    )
