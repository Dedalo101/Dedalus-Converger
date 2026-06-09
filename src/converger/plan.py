from typing import Dict, List

from .model import Desired, PlanStep, VMState


def _index_by_vmid(states: List[VMState]) -> Dict[int, VMState]:
    return {state.vmid: state for state in states}


def plan(current: List[VMState], desired: List[Desired]) -> List[PlanStep]:
    """Compute deterministic reconciliation steps for explicitly desired VMs only."""
    observed = _index_by_vmid(current)
    steps: List[PlanStep] = []

    for want in desired:
        state = observed.get(want.vmid)
        if state is None:
            return []
        if state.status == "unknown":
            return []

        if want.target == "running" and state.status == "stopped":
            steps.append(
                PlanStep(
                    vmid=want.vmid,
                    name=want.name,
                    action="start",
                    reason="desired running, observed stopped",
                )
            )
            continue

        if want.target == "stopped" and state.status == "running":
            steps.append(
                PlanStep(
                    vmid=want.vmid,
                    name=want.name,
                    action="stop",
                    reason="desired stopped, observed running",
                )
            )
            continue

        resize_reasons = []
        if want.cpus is not None and state.cpus is not None and want.cpus != state.cpus:
            resize_reasons.append(f"cpus {state.cpus} -> {want.cpus}")
        if (
            want.memory is not None
            and state.maxmem is not None
            and want.memory != state.maxmem
        ):
            resize_reasons.append(f"memory {state.maxmem} -> {want.memory}")

        if resize_reasons:
            steps.append(
                PlanStep(
                    vmid=want.vmid,
                    name=want.name,
                    action="resize",
                    reason="; ".join(resize_reasons),
                )
            )
            continue

        steps.append(
            PlanStep(
                vmid=want.vmid,
                name=want.name,
                action="noop",
                reason="already converged",
            )
        )

    return steps
