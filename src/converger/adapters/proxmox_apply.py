from typing import Any, Dict, List, Optional

from ..model import PlanStep
from .proxmox_client import create_api, resolve_vm_node


class ProxmoxApplyError(Exception):
    pass


class ProxmoxApplier:
    def __init__(self, config: Dict[str, Any], *, dry_run: bool = False):
        self.config = config
        self.dry_run = dry_run
        self.api = None if dry_run else create_api(config)

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

                node = resolve_vm_node(self.api, step.vmid, step.node)
                self._execute(step, node)
                results.append(
                    self._result(
                        step, "applied", "Mutation executed", api_call=api_call
                    )
                )
            except Exception as exc:
                results.append(self._result(step, "failed", str(exc)))

        return results

    def describe_api_call(self, step: PlanStep) -> dict:
        node = step.node or self.config.get("node") or "<resolved-node>"
        if step.action == "start":
            return {
                "method": "POST",
                "path": f"/api2/json/nodes/{node}/qemu/{step.vmid}/status/start",
            }
        if step.action == "stop":
            return {
                "method": "POST",
                "path": f"/api2/json/nodes/{node}/qemu/{step.vmid}/status/stop",
            }
        if step.action == "resize":
            payload = {}
            if step.target_cpus is not None:
                payload["cores"] = step.target_cpus
            if step.target_memory is not None:
                payload["memory"] = step.target_memory
            if not payload:
                raise ProxmoxApplyError(
                    f"Resize step for {step.name} has no target values"
                )
            return {
                "method": "PUT",
                "path": f"/api2/json/nodes/{node}/qemu/{step.vmid}/config",
                "body": payload,
            }
        raise ProxmoxApplyError(f"Unsupported action: {step.action}")

    def _execute(self, step: PlanStep, node: str) -> None:
        if step.action == "start":
            self.api.nodes(node).qemu(step.vmid).status.start.post()
        elif step.action == "stop":
            self.api.nodes(node).qemu(step.vmid).status.stop.post()
        elif step.action == "resize":
            config_payload = {}
            if step.target_cpus is not None:
                config_payload["cores"] = step.target_cpus
            if step.target_memory is not None:
                config_payload["memory"] = step.target_memory
            if not config_payload:
                raise ProxmoxApplyError(
                    f"Resize step for {step.name} has no target values"
                )
            self.api.nodes(node).qemu(step.vmid).config.put(**config_payload)
        else:
            raise ProxmoxApplyError(f"Unsupported action: {step.action}")

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
        }
        if api_call is not None:
            payload["api_call"] = api_call
        return payload
