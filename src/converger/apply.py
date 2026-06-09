from typing import Callable, List, Optional

from .artifacts import write_result
from .model import PlanStep


def audit(steps: List[PlanStep]) -> None:
    print("=== AUDIT MODE ===")
    print("No changes applied.")
    if not steps:
        print("Empty plan (refusal enforced).")
        return

    for step in steps:
        print(f"{step.action.upper()} {step.name} (vmid={step.vmid}) - {step.reason}")


def apply(
    steps: List[PlanStep],
    executor: Optional[Callable[[List[PlanStep]], List[dict]]] = None,
    output: str = "result.json",
    *,
    dry_run: bool = False,
) -> List[dict]:
    if dry_run:
        print("=== DRY-RUN APPLY ===")
        print("No mutations executed. API calls recorded only.")
    else:
        print("=== APPLY MODE ===")
        print("Mutating - confirmation required.")

    if executor is not None:
        results = executor(steps)
    else:
        results = [
            {
                "vmid": step.vmid,
                "name": step.name,
                "action": step.action,
                "status": "skipped" if step.action == "noop" else "pending",
                "reason": step.reason,
                "detail": "no executor configured",
            }
            for step in steps
        ]

    for result in results:
        status = result["status"]
        if status == "applied":
            print(
                f"APPLIED {result['action'].upper()} {result['name']} "
                f"(vmid={result['vmid']})"
            )
        elif status == "dry_run":
            api_call = result.get("api_call", {})
            target = _format_api_call(api_call)
            print(
                f"DRY-RUN {result['action'].upper()} {result['name']} "
                f"(vmid={result['vmid']}) -> {target}"
            )
        elif status == "failed":
            print(
                f"FAILED {result['action'].upper()} {result['name']} "
                f"(vmid={result['vmid']}): {result.get('detail')}"
            )

    write_result(results, output)
    print(f"Apply results written to {output}")
    return results


def _format_api_call(api_call: dict) -> str:
    if not api_call:
        return "<no api call>"
    if "operation" in api_call:
        return f"{api_call.get('service')}.{api_call.get('operation')}"
    return f"{api_call.get('method')} {api_call.get('path')}"
