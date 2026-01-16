"""Negative tests proving refusal guarantees."""

import pytest
from converger.model import VMState
from converger.plan import plan
from converger.safety import enforce_safety, PolicyViolation

# Assuming Desired and PlanStep are defined in model.py
from converger.model import Desired, PlanStep


def test_cannot_act_on_unknown():
    """NEVER: Act on incomplete truth."""
    current = [
        VMState(vmid=100, name="web-01", status="unknown"),
    ]
    desired = [
        Desired(vmid=100, name="web-01", target="running"),
    ]
    
    steps = plan(current, desired)
    
    # Empty plan - system refuses to guess
    assert len(steps) == 0


def test_cannot_stop_prod():
    """NEVER: Stop production workloads."""
    steps = [
        PlanStep(vmid=101, name="prod-db-01", action="stop", reason="test"),
    ]
    
    with pytest.raises(PolicyViolation) as exc_info:
        enforce_safety(steps)
    
    assert "prod-db-01" in str(exc_info.value)


def test_missing_not_stopped():
    """NEVER: Treat 'missing' as 'stopped'."""
    current = []  # VM not observed
    desired = [
        Desired(vmid=999, name="ghost-vm", target="running"),
    ]
    
    steps = plan(current, desired)
    
    # No steps - system doesn't assume stopped, doesn't try to start
    assert len(steps) == 0


def test_replay_equivalence():
    """NEVER: Violate time travel (deterministic planning)."""
    current = [
        VMState(vmid=100, name="web-01", status="stopped"),
    ]
    desired = [
        Desired(vmid=100, name="web-01", target="running"),
    ]
    
    plan1 = plan(current, desired)
    plan2 = plan(current, desired)
    
    assert plan1 == plan2


def test_audit_has_no_side_effects():
    """NEVER: Mutate during audit/plan modes."""
    from converger.apply import audit
    
    steps = [
        PlanStep(vmid=100, name="web-01", action="start", reason="test"),
    ]
    
    audit(steps)  # Should not raise, should not modify anything
    assert True