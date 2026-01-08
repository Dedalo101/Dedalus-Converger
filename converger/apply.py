from typing import List
import json

from .model import PlanStep


def audit(steps: List[PlanStep]) -> None:
    """
    Audit mode — zero side effects.
    Emits structured JSON for review (current.json / plan.json artifact).
    """
    print(json.dumps([step.__dict__ for step in steps], indent=2))


def apply(steps: List[PlanStep]) -> None:
    """
    Apply mode — only mutating phase.
    Placeholder until real adapter implementation.
    Requires explicit confirmation in CLI.
    """
    raise NotImplementedError(
        "Apply requires adapter-specific execution and confirmation"
    )
