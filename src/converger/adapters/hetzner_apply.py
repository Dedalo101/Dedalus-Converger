import json
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

from ..model import PlanStep


class HetznerApplyError(Exception):
    pass


class HetznerApplier:
    _API_BASE = "https://api.hetzner.cloud/v1"

    def __init__(self, config: Dict[str, Any], *, dry_run: bool = False):
        self.config = config
        self.dry_run = dry_run

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
        server_id = step.external_id or str(step.vmid)
        if step.action == "start":
            return {
                "method": "POST",
                "path": f"/v1/servers/{server_id}/actions/poweron",
            }
        if step.action == "stop":
            return {
                "method": "POST",
                "path": f"/v1/servers/{server_id}/actions/poweroff",
            }
        if step.action == "resize":
            if not step.target_server_type:
                raise HetznerApplyError(
                    f"Hetzner resize for {step.name} requires server_type in desired.yaml"
                )
            return {
                "method": "POST",
                "path": f"/v1/servers/{server_id}/actions/change_type",
                "body": {
                    "server_type": step.target_server_type,
                    "upgrade_disk": True,
                },
            }
        raise HetznerApplyError(f"Unsupported action: {step.action}")

    def _execute(self, step: PlanStep) -> None:
        server_id = step.external_id or str(step.vmid)
        if step.action == "start":
            self._post_action(server_id, "poweron")
            return
        if step.action == "stop":
            self._post_action(server_id, "poweroff")
            return
        if step.action == "resize":
            if not step.target_server_type:
                raise HetznerApplyError(
                    f"Hetzner resize for {step.name} requires server_type in desired.yaml"
                )
            self._post_action(
                server_id,
                "change_type",
                {
                    "server_type": step.target_server_type,
                    "upgrade_disk": True,
                },
            )
            return
        raise HetznerApplyError(f"Unsupported action: {step.action}")

    def _post_action(
        self, server_id: str, action: str, body: Optional[dict] = None
    ) -> None:
        payload = json.dumps(body or {}).encode("utf-8")
        request = urllib.request.Request(
            f"{self._API_BASE}/servers/{server_id}/actions/{action}",
            data=payload,
            headers={
                "Authorization": f"Bearer {self.config['api_token']}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=60):
                return
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise HetznerApplyError(
                f"Hetzner API error {exc.code} on {action}: {error_body}"
            ) from exc

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
