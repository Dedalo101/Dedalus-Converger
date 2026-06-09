import json
from unittest.mock import MagicMock, patch

from converger.adapters.hetzner_apply import HetznerApplier
from converger.model import PlanStep


@patch("converger.adapters.hetzner_apply.urllib.request.urlopen")
def test_hetzner_apply_start_and_stop(mock_urlopen):
    response = MagicMock()
    response.__enter__.return_value = response
    mock_urlopen.return_value = response

    applier = HetznerApplier({"api_token": "secret"})
    steps = [
        PlanStep(
            vmid=100,
            name="web-01",
            action="start",
            reason="start",
            external_id="100",
        ),
        PlanStep(
            vmid=101,
            name="dev-01",
            action="stop",
            reason="stop",
            external_id="101",
        ),
    ]

    results = applier.apply(steps)
    assert results[0]["status"] == "applied"
    assert results[1]["status"] == "applied"
    assert mock_urlopen.call_count == 2


@patch("converger.adapters.hetzner_apply.urllib.request.urlopen")
def test_hetzner_apply_resize(mock_urlopen):
    response = MagicMock()
    response.__enter__.return_value = response
    mock_urlopen.return_value = response

    applier = HetznerApplier({"api_token": "secret"})
    steps = [
        PlanStep(
            vmid=101,
            name="dev-api-01",
            action="resize",
            reason="server_type cx21 -> cx31",
            external_id="101",
            target_server_type="cx31",
        )
    ]

    results = applier.apply(steps)
    assert results[0]["status"] == "applied"
    request = mock_urlopen.call_args[0][0]
    assert request.full_url.endswith("/servers/101/actions/change_type")
    body = json.loads(request.data.decode("utf-8"))
    assert body["server_type"] == "cx31"


def test_hetzner_dry_run_records_api_calls():
    applier = HetznerApplier({"api_token": "secret"}, dry_run=True)
    steps = [
        PlanStep(
            vmid=100,
            name="web-01",
            action="start",
            reason="start",
            external_id="100",
        )
    ]

    results = applier.apply(steps)
    assert results[0]["status"] == "dry_run"
    assert "poweron" in results[0]["api_call"]["path"]
