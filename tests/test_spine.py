"""Negative tests proving refusal guarantees."""

import json
from pathlib import Path

import pytest

from converger.adapters.replay import ReplayAdapter
from converger.apply import audit
from converger.model import Desired, PlanStep, VMState
from converger.plan import plan
from converger.safety import PolicyViolation, enforce_safety


def test_cannot_act_on_unknown():
    current = [VMState(vmid=100, name="web-01", status="unknown")]
    desired = [Desired(vmid=100, name="web-01", target="running")]
    steps = plan(current, desired)
    assert steps == []


def test_cannot_stop_prod():
    steps = [PlanStep(vmid=101, name="prod-db-01", action="stop", reason="test")]
    with pytest.raises(PolicyViolation) as exc:
        enforce_safety(steps)
    assert "prod-db-01" in str(exc.value)


def test_missing_not_stopped():
    current = []
    desired = [Desired(vmid=999, name="ghost-vm", target="running")]
    steps = plan(current, desired)
    assert steps == []


def test_replay_equivalence():
    current = [VMState(vmid=100, name="web-01", status="stopped")]
    desired = [Desired(vmid=100, name="web-01", target="running")]
    first = plan(current, desired)
    second = plan(current, desired)
    assert first == second
    assert first == [
        PlanStep(
            vmid=100,
            name="web-01",
            action="start",
            reason="desired running, observed stopped",
            node=None,
        )
    ]


def test_audit_has_no_side_effects(capsys):
    steps = [PlanStep(vmid=100, name="web-01", action="start", reason="test")]
    audit(steps)
    captured = capsys.readouterr()
    assert "AUDIT MODE" in captured.out
    assert "START web-01" in captured.out


def test_plan_start_stop_and_resize():
    current = [
        VMState(vmid=100, name="web-01", status="stopped", cpus=2, maxmem=4096),
        VMState(vmid=101, name="dev-api-01", status="running", cpus=4, maxmem=8192),
    ]
    desired = [
        Desired(vmid=100, name="web-01", target="running"),
        Desired(vmid=101, name="dev-api-01", target="running", cpus=8, memory=16384),
    ]

    steps = plan(current, desired)
    assert steps[0].action == "start"
    assert steps[1].action == "resize"


def test_replay_adapter_reads_snapshot(tmp_path: Path):
    payload = [
        {
            "vmid": 100,
            "name": "web-01",
            "status": "stopped",
            "cpus": 2,
            "maxmem": 4096,
            "source": "replay",
        }
    ]
    replay_file = tmp_path / "replay.json"
    replay_file.write_text(json.dumps(payload), encoding="utf-8")

    adapter = ReplayAdapter({"path": str(replay_file)})
    states = adapter.observe()

    assert states == [
        VMState(
            vmid=100,
            name="web-01",
            status="stopped",
            cpus=2,
            maxmem=4096,
            source="replay",
        )
    ]


def test_desired_list_only_no_discovery():
    current = [VMState(vmid=100, name="web-01", status="running")]
    desired = [Desired(vmid=100, name="web-01", target="running")]
    steps = plan(current, desired)
    assert steps == [
        PlanStep(vmid=100, name="web-01", action="noop", reason="already converged")
    ]


def test_refuse_out_of_scope():
    current = [VMState(vmid=999, name="ghost", status="running")]
    desired = [Desired(vmid=100, name="web-01", target="running")]
    assert plan(current, desired) == []


def test_non_prod_stop_allowed():
    steps = [PlanStep(vmid=100, name="web-01", action="stop", reason="test")]
    assert enforce_safety(steps) == steps
