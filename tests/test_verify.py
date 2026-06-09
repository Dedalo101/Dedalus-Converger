from converger.model import Desired, VMState
from converger.verify import verify_convergence


def test_verify_convergence_success():
    post = [VMState(vmid=100, name="web-01", status="running")]
    desired = [Desired(vmid=100, name="web-01", target="running")]
    report = verify_convergence(post, desired)
    assert report.converged is True
    assert report.remaining_steps == []


def test_verify_convergence_failure():
    post = [VMState(vmid=100, name="web-01", status="stopped")]
    desired = [Desired(vmid=100, name="web-01", target="running")]
    report = verify_convergence(post, desired)
    assert report.converged is False
    assert report.remaining_steps[0].action == "start"
