from typing import List
from .model import VMState, Desired, PlanStep

def plan(current: List[VMState], desired: List[Desired]) -> List[PlanStep]:
    # TODO: Diff logic (refuse unknown/missing)
    return []  # Empty plan enforces refusal
