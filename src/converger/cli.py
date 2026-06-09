import json
import sys
from pathlib import Path

import click
import yaml

from . import contract
from .apply import apply as apply_steps
from .apply import audit as audit_steps
from .model import Desired
from .observe import observe_live, observe_replay
from .plan import plan
from .safety import PolicyViolation, enforce_safety

contract.verify_contract()


@click.group()
def cli():
    """Dedalus Converger — domain-agnostic reconciliation with refusal semantics."""


@cli.command()
@click.option(
    "--desired",
    "-d",
    type=click.Path(exists=True),
    required=True,
    help="Path to desired.yaml",
)
@click.option(
    "--replay", "-r", type=click.Path(exists=True), help="Path to replay JSON snapshot"
)
def audit(desired: str, replay: str | None) -> None:
    """Audit mode — zero side effects, print plan."""
    try:
        current = observe_replay(replay) if replay else observe_live()
        desired_objs = _load_desired(desired)
        steps = plan(current, desired_objs)
        safe_steps = enforce_safety(steps)
        audit_steps(safe_steps)
    except (PolicyViolation, Exception) as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@cli.command("plan")
@click.option("--desired", "-d", type=click.Path(exists=True), required=True)
@click.option(
    "--replay", "-r", type=click.Path(exists=True), help="Path to replay snapshot"
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default="plan.json",
    help="Output plan artifact",
)
def plan_cmd(desired: str, replay: str | None, output: str) -> None:
    """Plan mode — write structured plan.json."""
    try:
        current = observe_replay(replay) if replay else observe_live()
        desired_objs = _load_desired(desired)
        steps = plan(current, desired_objs)
        safe_steps = enforce_safety(steps)
        Path(output).write_text(
            json.dumps([step.__dict__ for step in safe_steps], indent=2),
            encoding="utf-8",
        )
        click.echo(f"Plan written to {output}")
    except (PolicyViolation, Exception) as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@cli.command("apply")
@click.option("--desired", "-d", type=click.Path(exists=True), required=True)
@click.option(
    "--replay", "-r", type=click.Path(exists=True), help="Replay mode (dry-run only)"
)
@click.option("--confirm", is_flag=True, help="Explicit confirmation required to apply")
def apply_cmd(desired: str, replay: str | None, confirm: bool) -> None:
    """Apply mode — only mutating phase."""
    if replay:
        click.echo("Apply with --replay is refused — replay is read-only.", err=True)
        sys.exit(1)

    if not confirm:
        click.echo("Apply requires explicit --confirm flag.", err=True)
        sys.exit(1)

    try:
        current = observe_live()
        desired_objs = _load_desired(desired)
        steps = plan(current, desired_objs)
        safe_steps = enforce_safety(steps)
        click.confirm(f"Apply {len(safe_steps)} changes?", abort=True)
        apply_steps(safe_steps)
        click.echo("Applied.")
    except (PolicyViolation, Exception) as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


def _load_desired(path: str) -> list[Desired]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return [Desired(**item) for item in data]


def main():
    cli()


if __name__ == "__main__":
    main()
