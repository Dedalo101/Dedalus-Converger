from typing import List
from .model import PlanStep

class PolicyViolation(Exception):
    pass

def enforce_safety(steps: List[PlanStep]) -> List[PlanStep]:
    for step in steps:
        if step.name.startswith("prod-") and step.action == "stop":
            raise PolicyViolation(f"Never stop prod VM: {step.name}")
    return steps
