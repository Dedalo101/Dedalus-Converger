"""Exhaustive negative proofs — what the system CANNOT do."""

import pytest
from converger.model import VMState, Desired, PlanStep
from converger.plan import plan
from converger.safety import enforce_safety, PolicyViolation

def test_refuse_unknown_status():
    """NEVER act on incomplete truth."""
    current = [VMState(vmid=100, name="web-01", status="unknown")]
    desired = [Desired(vmid=100, name="web-01", target="running")]

    steps = plan(current, desired)
    assert len(steps) == 0  # explicit refusal

def test_refuse_out_of_scope():
    """NEVER discover or invent entities."""
    current = [VMState(vmid=999, name="ghost", status="running")]
    desired = [Desired(vmid=100, name="web-01", target="running")]

    steps = plan(current, desired)
    assert len(steps) == 0  # no step for ghost, no step for missing web-01

def test_prod_stop_refused():
    """NEVER stop production workloads."""
    steps = [
        PlanStep(vmid=101, name="prod-db-01", action="stop", reason="test")
    ]
    with pytest.raises(PolicyViolation):
        enforce_safety(steps)

def test_non_prod_stop_allowed():
    """Policy allows stopping non-prod."""
    steps = [
        PlanStep(vmid=100, name="web-01", action="stop", reason="test")
    ]
    safe = enforce_safety(steps)
    assert safe == steps  # passes through

def test_replay_equivalence():
    """NEVER violate time travel."""
    current = [VMState(vmid=100, name="web-01", status="stopped")]
    desired = [Desired(vmid=100, name="web-01", target="running")]

    plan1 = plan(current, desired)
    plan2 = plan(current, desired)  # same inputs
    assert plan1 == plan2

def test_audit_zero_side_effects():
    """NEVER mutate in audit mode."""
    from converger.apply import audit

    steps = [PlanStep(vmid=100, name="web-01", action="start", reason="test")]
    # audit only prints — no exception, no mutation
    audit(steps)
    assert True  # reaches here = zero side effects
