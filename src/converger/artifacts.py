import json
from dataclasses import asdict
from pathlib import Path
from typing import List

from .model import PlanStep, VMState


def write_current(states: List[VMState], path: str | Path) -> Path:
    output = Path(path)
    payload = [asdict(state) for state in states]
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output


def write_plan(steps: List[PlanStep], path: str | Path) -> Path:
    output = Path(path)
    payload = [asdict(step) for step in steps]
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output


def write_result(results: List[dict], path: str | Path) -> Path:
    output = Path(path)
    output.write_text(json.dumps(results, indent=2), encoding="utf-8")
    return output
