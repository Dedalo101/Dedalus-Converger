from typing import List

from .model import VMState, Desired, PlanStep


def plan(current: List[VMState], desired: List[Desired]) -> List[PlanStep]:
    """
    Deterministic planning.
    Pure function: same inputs → same outputs.
    Refuses unknown. Skips out-of-scope.
    """
    steps: List[PlanStep] = []
    desired_map = {d.vmid: d for d in desired}

    for state in current:
        if state.status == "unknown":
            continue  # explicit refusal — no guessing

        des = desired_map.get(state.vmid)
        if des is None:
            continue  # out of scope — not in desired list

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
