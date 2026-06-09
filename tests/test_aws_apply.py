from unittest.mock import MagicMock, patch

from converger.adapters.aws_apply import AwsApplier
from converger.model import PlanStep


def _config():
    return {"region": "eu-west-1", "vmid_tag": "converger:vmid"}


@patch("converger.adapters.aws_apply.boto3")
def test_aws_apply_start_and_stop(mock_boto3):
    client = MagicMock()
    session = MagicMock()
    session.client.return_value = client
    mock_boto3.Session.return_value = session

    applier = AwsApplier(_config())
    steps = [
        PlanStep(
            vmid=100,
            name="web-01",
            action="start",
            reason="start",
            external_id="i-abc",
        ),
        PlanStep(
            vmid=101,
            name="dev-01",
            action="stop",
            reason="stop",
            external_id="i-def",
        ),
    ]

    results = applier.apply(steps)
    assert results[0]["status"] == "applied"
    assert results[1]["status"] == "applied"
    client.start_instances.assert_called_once_with(InstanceIds=["i-abc"])
    client.stop_instances.assert_called_once_with(InstanceIds=["i-def"])


@patch("converger.adapters.aws_apply.boto3")
def test_aws_apply_resize_stops_when_running(mock_boto3):
    client = MagicMock()
    session = MagicMock()
    session.client.return_value = client
    mock_boto3.Session.return_value = session
    client.describe_instances.return_value = {
        "Reservations": [
            {
                "Instances": [
                    {"State": {"Name": "running"}},
                ]
            }
        ]
    }

    applier = AwsApplier(_config())
    steps = [
        PlanStep(
            vmid=101,
            name="dev-api-01",
            action="resize",
            reason="instance_type t3.small -> t3.medium",
            external_id="i-def",
            target_instance_type="t3.medium",
        )
    ]

    results = applier.apply(steps)
    assert results[0]["status"] == "applied"
    client.stop_instances.assert_called_once_with(InstanceIds=["i-def"])
    client.modify_instance_attribute.assert_called_once_with(
        InstanceId="i-def",
        InstanceType={"Value": "t3.medium"},
    )
    client.start_instances.assert_called_once_with(InstanceIds=["i-def"])


def test_aws_dry_run_records_api_calls():
    applier = AwsApplier(_config(), dry_run=True)
    steps = [
        PlanStep(
            vmid=100,
            name="web-01",
            action="start",
            reason="start",
            external_id="i-abc",
        )
    ]

    results = applier.apply(steps)
    assert results[0]["status"] == "dry_run"
    assert results[0]["api_call"]["operation"] == "StartInstances"
