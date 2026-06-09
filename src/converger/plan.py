from typing import Dict, List

from .model import Desired, PlanStep, VMState


def _index_by_vmid(states: List[VMState]) -> Dict[int, VMState]:
    return {state.vmid: state for state in states}


def _step_fields(state: VMState) -> dict:
    return {
        "node": state.node,
        "external_id": state.external_id,
    }


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

        fields = _step_fields(state)

        if want.target == "running" and state.status == "stopped":
            steps.append(
                PlanStep(
                    vmid=want.vmid,
                    name=want.name,
                    action="start",
                    reason="desired running, observed stopped",
                    **fields,
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
                    **fields,
                )
            )
            continue

        resize_reasons = []
        target_cpus = None
        target_memory = None
        target_instance_type = None
        target_server_type = None

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
        if (
            want.instance_type is not None
            and state.instance_type is not None
            and want.instance_type != state.instance_type
        ):
            resize_reasons.append(
                f"instance_type {state.instance_type} -> {want.instance_type}"
            )
            target_instance_type = want.instance_type
        if (
            want.server_type is not None
            and state.server_type is not None
            and want.server_type != state.server_type
        ):
            resize_reasons.append(
                f"server_type {state.server_type} -> {want.server_type}"
            )
            target_server_type = want.server_type

        if resize_reasons:
            steps.append(
                PlanStep(
                    vmid=want.vmid,
                    name=want.name,
                    action="resize",
                    reason="; ".join(resize_reasons),
                    target_cpus=target_cpus,
                    target_memory=target_memory,
                    target_instance_type=target_instance_type,
                    target_server_type=target_server_type,
                    **fields,
                )
            )
            continue

        steps.append(
            PlanStep(
                vmid=want.vmid,
                name=want.name,
                action="noop",
                reason="already converged",
                **fields,
            )
        )

    return steps
