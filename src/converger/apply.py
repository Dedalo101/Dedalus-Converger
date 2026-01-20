from typing import List
from .model import PlanStep

def audit(steps: List[PlanStep]):
    print("=== AUDIT MODE ===")
    print("No changes applied.")
    if not steps:
        print("Empty plan (refusal enforced).")
    for step in steps:
        print(f"{step.action.upper()} {step.name} (vmid={step.vmid}) - {step.reason}")

def apply(steps: List[PlanStep]):
    print("=== APPLY MODE ===")
    print("Mutating - confirmation required.")
    # TODO: Real mutation + confirm
