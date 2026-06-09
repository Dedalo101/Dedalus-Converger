from typing import Any, Dict, List, Optional

try:
    import boto3
except ImportError:
    boto3 = None

from ..model import PlanStep


class AwsApplyError(Exception):
    pass


class AwsApplier:
    def __init__(self, config: Dict[str, Any], *, dry_run: bool = False):
        self.config = config
        self.dry_run = dry_run
        self.client = None if dry_run else self._create_client()

    def apply(self, steps: List[PlanStep]) -> List[dict]:
        results: List[dict] = []

        for step in steps:
            if step.action == "noop":
                results.append(self._result(step, "skipped", step.reason))
                continue

            try:
                api_call = self.describe_api_call(step)
                if self.dry_run:
                    results.append(
                        self._result(
                            step,
                            "dry_run",
                            "API call recorded, not executed",
                            api_call=api_call,
                        )
                    )
                    continue

                self._execute(step)
                results.append(
                    self._result(
                        step, "applied", "Mutation executed", api_call=api_call
                    )
                )
            except Exception as exc:
                results.append(self._result(step, "failed", str(exc)))

        return results

    def describe_api_call(self, step: PlanStep) -> dict:
        instance_id = step.external_id or f"<vmid-{step.vmid}>"
        if step.action == "start":
            return {
                "service": "ec2",
                "operation": "StartInstances",
                "params": {"InstanceIds": [instance_id]},
            }
        if step.action == "stop":
            return {
                "service": "ec2",
                "operation": "StopInstances",
                "params": {"InstanceIds": [instance_id]},
            }
        if step.action == "resize":
            if not step.target_instance_type:
                raise AwsApplyError(
                    f"AWS resize for {step.name} requires instance_type in desired.yaml"
                )
            return {
                "service": "ec2",
                "operation": "ModifyInstanceAttribute",
                "params": {
                    "InstanceId": instance_id,
                    "InstanceType": {"Value": step.target_instance_type},
                },
                "note": "Instance is stopped before type change when currently running",
            }
        raise AwsApplyError(f"Unsupported action: {step.action}")

    def _create_client(self):
        if boto3 is None:
            raise AwsApplyError(
                "boto3 is required for AWS apply. Install with: pip install dedalus-converger[aws]"
            )

        session_kwargs = {"region_name": self.config["region"]}
        profile = self.config.get("profile")
        if profile:
            session = boto3.Session(profile_name=profile, **session_kwargs)
        else:
            session = boto3.Session(**session_kwargs)
        return session.client("ec2")

    def _resolve_instance_id(self, step: PlanStep) -> str:
        if step.external_id:
            return step.external_id

        vmid_tag = self.config.get("vmid_tag", "converger:vmid")
        response = self.client.describe_instances(
            Filters=[{"Name": f"tag:{vmid_tag}", "Values": [str(step.vmid)]}]
        )
        for reservation in response.get("Reservations", []):
            for instance in reservation.get("Instances", []):
                state = instance.get("State", {}).get("Name", "")
                if state not in {"terminated", "shutting-down"}:
                    return instance["InstanceId"]

        raise AwsApplyError(
            f"No EC2 instance found for vmid={step.vmid} (tag {vmid_tag})"
        )

    def _instance_state(self, instance_id: str) -> str:
        response = self.client.describe_instances(InstanceIds=[instance_id])
        for reservation in response.get("Reservations", []):
            for instance in reservation.get("Instances", []):
                return instance.get("State", {}).get("Name", "unknown")
        raise AwsApplyError(f"EC2 instance {instance_id} not found")

    def _wait_for_state(self, instance_id: str, target: str) -> None:
        waiter_name = {
            "stopped": "instance_stopped",
            "running": "instance_running",
        }.get(target)
        if waiter_name is None:
            raise AwsApplyError(f"Unsupported wait state: {target}")
        waiter = self.client.get_waiter(waiter_name)
        waiter.wait(InstanceIds=[instance_id])

    def _execute(self, step: PlanStep) -> None:
        instance_id = self._resolve_instance_id(step)
        if step.action == "start":
            self.client.start_instances(InstanceIds=[instance_id])
            return
        if step.action == "stop":
            self.client.stop_instances(InstanceIds=[instance_id])
            return
        if step.action == "resize":
            if not step.target_instance_type:
                raise AwsApplyError(
                    f"AWS resize for {step.name} requires instance_type in desired.yaml"
                )
            was_running = self._instance_state(instance_id) == "running"
            if was_running:
                self.client.stop_instances(InstanceIds=[instance_id])
                self._wait_for_state(instance_id, "stopped")
            self.client.modify_instance_attribute(
                InstanceId=instance_id,
                InstanceType={"Value": step.target_instance_type},
            )
            if was_running:
                self.client.start_instances(InstanceIds=[instance_id])
            return
        raise AwsApplyError(f"Unsupported action: {step.action}")

    @staticmethod
    def _result(
        step: PlanStep,
        status: str,
        detail: str,
        api_call: Optional[dict] = None,
    ) -> dict:
        payload = {
            "vmid": step.vmid,
            "name": step.name,
            "action": step.action,
            "status": status,
            "reason": step.reason,
            "detail": detail,
            "node": step.node,
            "external_id": step.external_id,
        }
        if api_call is not None:
            payload["api_call"] = api_call
        return payload
