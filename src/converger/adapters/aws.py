from typing import Dict, List, Optional

try:
    import boto3
except ImportError:
    boto3 = None

from ..model import VMState
from .base import ObservationAdapter, ObservationError
from .registry import AdapterRegistry

_EC2_RUNNING = {"running"}
_EC2_STOPPED = {"stopped"}
_EC2_UNKNOWN = {
    "pending",
    "stopping",
    "shutting-down",
    "terminated",
    "terminating",
}


def _tags_dict(tags: Optional[List[dict]]) -> Dict[str, str]:
    if not tags:
        return {}
    return {tag["Key"]: tag["Value"] for tag in tags if "Key" in tag and "Value" in tag}


def _map_ec2_status(raw: str) -> str:
    normalized = raw.lower()
    if normalized in _EC2_RUNNING:
        return "running"
    if normalized in _EC2_STOPPED:
        return "stopped"
    return "unknown"


class AwsEc2Adapter(ObservationAdapter):
    name = "aws"
    required_config_keys = {"region"}

    def observe(self) -> List[VMState]:
        if boto3 is None:
            raise ObservationError(
                "boto3 is required for AWS observation. Install with: pip install dedalus-converger[aws]"
            )

        session_kwargs = {"region_name": self.config["region"]}
        profile = self.config.get("profile")
        if profile:
            session = boto3.Session(profile_name=profile, **session_kwargs)
        else:
            session = boto3.Session(**session_kwargs)

        client = session.client("ec2")
        try:
            response = client.describe_instances()
        except Exception as exc:
            raise ObservationError(f"AWS EC2 observation failed: {exc}") from exc

        vmid_tag = self.config.get("vmid_tag", "converger:vmid")
        name_tag = self.config.get("name_tag", "Name")
        scope_key = self.config.get("scope_tag_key")
        scope_value = self.config.get("scope_tag_value")

        states: List[VMState] = []
        for reservation in response.get("Reservations", []):
            for instance in reservation.get("Instances", []):
                tags = _tags_dict(instance.get("Tags"))
                if scope_key and tags.get(scope_key) != scope_value:
                    continue

                vmid_raw = tags.get(vmid_tag)
                if vmid_raw is None:
                    continue

                try:
                    vmid = int(vmid_raw)
                except (TypeError, ValueError) as exc:
                    raise ObservationError(
                        f"EC2 instance {instance.get('InstanceId')} has non-integer {vmid_tag}={vmid_raw!r}"
                    ) from exc

                name = tags.get(name_tag) or instance.get("InstanceId", f"ec2-{vmid}")
                node = instance.get("Placement", {}).get("AvailabilityZone")

                states.append(
                    VMState(
                        vmid=vmid,
                        name=str(name),
                        status=_map_ec2_status(
                            instance.get("State", {}).get("Name", "unknown")
                        ),
                        cpus=None,
                        maxmem=None,
                        source="aws",
                        node=node,
                        external_id=instance.get("InstanceId"),
                        instance_type=instance.get("InstanceType"),
                    )
                )

        if scope_key and not states:
            raise ObservationError(
                f"No EC2 instances matched scope tag {scope_key}={scope_value!r}"
            )

        return states


AdapterRegistry.register(AwsEc2Adapter)
