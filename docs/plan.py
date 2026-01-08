from typing import List

from .model import VMState, Desired, PlanStep


def plan(current: List[VMState], desired: List[Desired]) -> List[PlanStep]:
    """
    Deterministic planning — pure function.
    Same inputs → same outputs always.

    Refusal rules:
    - unknown status → skip (no guessing)
    - VM not in desired list → skip (no discovery)
    - missing ≠ stopped (absence from current list means out of scope)
    """
    steps: List[PlanStep] = []
    desired_map = {d.vmid: d for d in desired}

    for state in current:
        # Explicit refusal on incomplete truth
        if state.status == "unknown":
            continue

        des = desired_map.get(state.vmid)
        if des is None:
            continue  # out of scope — not declared

        if state.status == des.target:
            steps.append(
                PlanStep(
                    vmid=state.vmid,
                    name=state.name,
                    action="noop",
                    reason="already in desired state",
                )
            )
        elif state.status == "running" and des.target == "stopped":
            steps.append(
                PlanStep(
                    vmid=state.vmid,
                    name=state.name,
                    action="stop",
                    reason="desired stopped",
                )
            )
        elif state.status == "stopped" and des.target == "running":
            steps.append(
                PlanStep(
                    vmid=state.vmid,
                    name=state.name,
                    action="start",
                    reason="desired running",
                )
            )

    return steps
