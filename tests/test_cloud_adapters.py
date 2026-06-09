import json
from unittest.mock import MagicMock, patch

from converger.adapters.aws import AwsEc2Adapter
from converger.adapters.hetzner import HetznerAdapter


@patch("converger.adapters.aws.boto3")
def test_aws_adapter_maps_tagged_instances(mock_boto3):
    client = MagicMock()
    session = MagicMock()
    session.client.return_value = client
    mock_boto3.Session.return_value = session
    client.describe_instances.return_value = {
        "Reservations": [
            {
                "Instances": [
                    {
                        "InstanceId": "i-abc",
                        "InstanceType": "t3.small",
                        "State": {"Name": "running"},
                        "Placement": {"AvailabilityZone": "eu-west-1a"},
                        "Tags": [
                            {"Key": "converger:vmid", "Value": "100"},
                            {"Key": "Name", "Value": "web-01"},
                            {"Key": "converger", "Value": "managed"},
                        ],
                    }
                ]
            }
        ]
    }

    adapter = AwsEc2Adapter(
        {
            "region": "eu-west-1",
            "vmid_tag": "converger:vmid",
            "scope_tag_key": "converger",
            "scope_tag_value": "managed",
        }
    )
    states = adapter.observe()
    assert len(states) == 1
    assert states[0].vmid == 100
    assert states[0].status == "running"
    assert states[0].source == "aws"


@patch("converger.adapters.hetzner.urllib.request.urlopen")
def test_hetzner_adapter_maps_servers(mock_urlopen):
    payload = {
        "servers": [
            {
                "id": 101,
                "name": "dev-api-01",
                "status": "running",
                "server_type": {"cores": 4, "memory": 8},
                "datacenter": {"name": "fsn1-dc14"},
            }
        ]
    }
    response = MagicMock()
    response.read.return_value = json.dumps(payload).encode("utf-8")
    response.__enter__.return_value = response
    mock_urlopen.return_value = response

    adapter = HetznerAdapter({"api_token": "secret"})
    states = adapter.observe()
    assert len(states) == 1
    assert states[0].vmid == 101
    assert states[0].cpus == 4
    assert states[0].source == "hetzner"
