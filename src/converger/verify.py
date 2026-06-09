from dataclasses import asdict, dataclass
from typing import List

from .model import Desired, PlanStep, VMState
from .plan import plan


@dataclass(frozen=True)
class ConvergenceReport:
    converged: bool
    remaining_steps: List[PlanStep]

    def as_dict(self) -> dict:
        return {
            "converged": self.converged,
            "remaining_steps": [asdict(step) for step in self.remaining_steps],
        }


def verify_convergence(
    post_observation: List[VMState], desired: List[Desired]
) -> ConvergenceReport:
    """Re-plan after apply; convergence means no pending actions remain."""
    remaining = plan(post_observation, desired)
    pending = [step for step in remaining if step.action != "noop"]
    return ConvergenceReport(converged=len(pending) == 0, remaining_steps=pending)
