import json
from pathlib import Path

from converger.artifacts import write_current, write_plan, write_result
from converger.model import PlanStep, VMState


def test_write_current_and_plan(tmp_path: Path):
    states = [VMState(vmid=100, name="web-01", status="stopped", node="pve1")]
    steps = [
        PlanStep(
            vmid=100,
            name="web-01",
            action="start",
            reason="desired running, observed stopped",
            node="pve1",
        )
    ]

    current_path = write_current(states, tmp_path / "current.json")
    plan_path = write_plan(steps, tmp_path / "plan.json")

    current_payload = json.loads(current_path.read_text(encoding="utf-8"))
    plan_payload = json.loads(plan_path.read_text(encoding="utf-8"))

    assert current_payload[0]["node"] == "pve1"
    assert plan_payload[0]["action"] == "start"


def test_write_result(tmp_path: Path):
    results = [{"vmid": 100, "status": "applied"}]
    path = write_result(results, tmp_path / "result.json")
    assert json.loads(path.read_text(encoding="utf-8")) == results
