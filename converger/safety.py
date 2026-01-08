from typing import List

from .model import PlanStep


class PolicyViolation(RuntimeError):
    """Explicit refusal of unsafe actions."""

    pass


def enforce_safety(steps: List[PlanStep]) -> List[PlanStep]:
    """
    Policy enforcement — returns only safe steps.
    Raises PolicyViolation on invariant breach.

    Current locked policy:
    - Never stop a VM whose name starts with "prod-"
    """
    for step in steps:
        if step.name.startswith("prod-") and step.action == "stop":
            raise PolicyViolation(
                f"Refused to stop production workload: {step.name}. "
                "Production VMs are write-protected by default."
            )

    # If no violation, all steps are safe
    return steps
