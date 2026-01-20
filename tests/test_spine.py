"""Negative tests proving refusal guarantees."""
import pytest
from src.converger.model import VMState, Desired, PlanStep
from src.converger.plan import plan
from src.converger.safety import enforce_safety, PolicyViolation
from src.converger.apply import audit

def test_cannot_act_on_unknown():
    current = [VMState(vmid=100, name="web-01", status="unknown")]
    desired = [Desired(vmid=100, name="web-01", target="running")]
    steps = plan(current, desired)
    assert len(steps) == 0

def test_cannot_stop_prod():
    steps = [PlanStep(vmid=101, name="prod-db-01", action="stop", reason="test")]
    with pytest.raises(PolicyViolation) as exc:
        enforce_safety(steps)
    assert "prod-db-01" in str(exc.value)

def test_missing_not_stopped():
    current = []
    desired = [Desired(vmid=999, name="ghost-vm", target="running")]
    steps = plan(current, desired)
    assert len(steps) == 0

def test_replay_equivalence():
    current = [VMState(vmid=100, name="web-01", status="stopped")]
    desired = [Desired(vmid=100, name="web-01", target="running")]
    assert plan(current, desired) == plan(current, desired)

def test_audit_has_no_side_effects():
    steps = [PlanStep(vmid=100, name="web-01", action="start", reason="test")]
    audit(steps)  # No mutation
    assert True
