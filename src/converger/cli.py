import click
import yaml
from src.converger import contract
from src.converger.model import Desired
from src.converger.observe import observe_live
from src.converger.plan import plan
from src.converger.safety import enforce_safety, PolicyViolation
from src.converger.apply import audit

contract.verify_contract()


@click.group()
def main():
    pass


@main.command()
def audit_live():
    try:
        with open("examples/desired.yaml") as f:
            raw = yaml.safe_load(f)
        desired = [Desired(**item) for item in raw]
        current = observe_live()
        steps = plan(current, desired)
        safe_steps = enforce_safety(steps)
        audit(safe_steps)
    except (FileNotFoundError, PolicyViolation, Exception) as e:
        click.echo(f"Error: {e}", err=True)


if __name__ == "__main__":
    main()
