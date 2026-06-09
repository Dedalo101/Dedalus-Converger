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
                    node=state.node,
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
                    node=state.node,
                )
            )
            continue

        resize_reasons = []
        target_cpus = None
        target_memory = None
        if want.cpus is not None and state.cpus is not None and want.cpus != state.cpus:
            resize_reasons.append(f"cpus {state.cpus} -> {want.cpus}")
            target_cpus = want.cpus
        if (
            want.memory is not None
            and state.maxmem is not None
            and want.memory != state.maxmem
        ):
            resize_reasons.append(f"memory {state.maxmem} -> {want.memory}")
            target_memory = want.memory

        if resize_reasons:
            steps.append(
                PlanStep(
                    vmid=want.vmid,
                    name=want.name,
                    action="resize",
                    reason="; ".join(resize_reasons),
                    node=state.node,
                    target_cpus=target_cpus,
                    target_memory=target_memory,
                )
            )
            continue

        steps.append(
            PlanStep(
                vmid=want.vmid,
                name=want.name,
                action="noop",
                reason="already converged",
                node=state.node,
            )
        )

    return steps
