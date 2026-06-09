import json
from pathlib import Path
from typing import List

from .model import PlanStep


def audit(steps: List[PlanStep]) -> None:
    print("=== AUDIT MODE ===")
    print("No changes applied.")
    if not steps:
        print("Empty plan (refusal enforced).")
        return

    for step in steps:
        print(f"{step.action.upper()} {step.name} (vmid={step.vmid}) - {step.reason}")


def apply(steps: List[PlanStep], output: str = "result.json") -> None:
    print("=== APPLY MODE ===")
    print("Mutating - confirmation required.")

    results = []
    for step in steps:
        if step.action == "noop":
            results.append(
                {
                    "vmid": step.vmid,
                    "name": step.name,
                    "action": step.action,
                    "status": "skipped",
                    "reason": step.reason,
                }
            )
            continue

        results.append(
            {
                "vmid": step.vmid,
                "name": step.name,
                "action": step.action,
                "status": "pending",
                "reason": step.reason,
            }
        )
        print(f"PENDING {step.action.upper()} {step.name} (vmid={step.vmid})")

    Path(output).write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Apply results written to {output}")
