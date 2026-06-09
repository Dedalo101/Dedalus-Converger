from typing import Any, Dict, List

from ..model import PlanStep
from .proxmox_client import create_api, resolve_vm_node


class ProxmoxApplyError(Exception):
    pass


class ProxmoxApplier:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api = create_api(config)

    def apply(self, steps: List[PlanStep]) -> List[dict]:
        results: List[dict] = []

        for step in steps:
            if step.action == "noop":
                results.append(self._result(step, "skipped", step.reason))
                continue

            try:
                node = resolve_vm_node(self.api, step.vmid, step.node)
                if step.action == "start":
                    self.api.nodes(node).qemu(step.vmid).status.start.post()
                    results.append(self._result(step, "applied", "VM started"))
                elif step.action == "stop":
                    self.api.nodes(node).qemu(step.vmid).status.stop.post()
                    results.append(self._result(step, "applied", "VM stopped"))
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
                    results.append(
                        self._result(step, "applied", f"VM resized: {step.reason}")
                    )
                else:
                    raise ProxmoxApplyError(f"Unsupported action: {step.action}")
            except Exception as exc:
                results.append(self._result(step, "failed", str(exc)))

        return results

    @staticmethod
    def _result(step: PlanStep, status: str, detail: str) -> dict:
        return {
            "vmid": step.vmid,
            "name": step.name,
            "action": step.action,
            "status": status,
            "reason": step.reason,
            "detail": detail,
            "node": step.node,
        }
