import sys
from pathlib import Path

import click
import yaml

from . import contract
from .adapters.proxmox_apply import ProxmoxApplier
from .apply import apply as apply_steps
from .apply import audit as audit_steps
from .artifacts import write_current, write_plan
from .config import ConvergerConfig, load_config, require_proxmox
from .model import Desired
from .observe import observe_live, observe_replay
from .plan import plan
from .safety import PolicyViolation, enforce_safety

contract.verify_contract()


@click.group()
@click.option(
    "--config",
    "-c",
    type=click.Path(),
    default=None,
    help="Path to converger.yaml (default: ./converger.yaml if present)",
)
@click.pass_context
def cli(ctx: click.Context, config: str | None) -> None:
    """Dedalus Converger — domain-agnostic reconciliation with refusal semantics."""
    ctx.ensure_object(dict)
    ctx.obj["config"] = load_config(config)


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
@click.pass_context
def audit(ctx: click.Context, desired: str, replay: str | None) -> None:
    """Audit mode — zero side effects, print plan."""
    config: ConvergerConfig = ctx.obj["config"]
    try:
        current, _ = _observe(config, replay)
        current_path = write_current(current, config.artifacts.current)
        desired_objs = _load_desired(desired)
        steps = plan(current, desired_objs)
        safe_steps = enforce_safety(steps)
        audit_steps(safe_steps)
        click.echo(f"Observation written to {current_path}")
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
    default=None,
    help="Output plan artifact (default: from config or plan.json)",
)
@click.pass_context
def plan_cmd(
    ctx: click.Context, desired: str, replay: str | None, output: str | None
) -> None:
    """Plan mode — write structured plan.json."""
    config: ConvergerConfig = ctx.obj["config"]
    output_path = output or config.artifacts.plan
    try:
        current, _ = _observe(config, replay)
        current_path = write_current(current, config.artifacts.current)
        desired_objs = _load_desired(desired)
        steps = plan(current, desired_objs)
        safe_steps = enforce_safety(steps)
        plan_path = write_plan(safe_steps, output_path)
        click.echo(f"Observation written to {current_path}")
        click.echo(f"Plan written to {plan_path}")
    except (PolicyViolation, Exception) as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@cli.command("apply")
@click.option("--desired", "-d", type=click.Path(exists=True), required=True)
@click.option(
    "--replay", "-r", type=click.Path(exists=True), help="Replay mode (dry-run only)"
)
@click.option("--confirm", is_flag=True, help="Explicit confirmation required to apply")
@click.pass_context
def apply_cmd(
    ctx: click.Context, desired: str, replay: str | None, confirm: bool
) -> None:
    """Apply mode — only mutating phase."""
    config: ConvergerConfig = ctx.obj["config"]

    if replay:
        click.echo("Apply with --replay is refused — replay is read-only.", err=True)
        sys.exit(1)

    if not confirm:
        click.echo("Apply requires explicit --confirm flag.", err=True)
        sys.exit(1)

    try:
        proxmox = require_proxmox(config)
        current, _ = _observe(config, replay=None)
        current_path = write_current(current, config.artifacts.current)
        desired_objs = _load_desired(desired)
        steps = plan(current, desired_objs)
        safe_steps = enforce_safety(steps)
        click.echo(f"Observation written to {current_path}")
        click.confirm(f"Apply {len(safe_steps)} changes?", abort=True)

        applier = ProxmoxApplier(proxmox.as_adapter_config())
        results = apply_steps(
            safe_steps,
            executor=applier.apply,
            output=config.artifacts.result,
        )
        failed = [item for item in results if item["status"] == "failed"]
        if failed:
            click.echo(f"{len(failed)} step(s) failed.", err=True)
            sys.exit(1)
        click.echo("Applied.")
    except (PolicyViolation, Exception) as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


def _observe(config: ConvergerConfig, replay: str | None):
    if replay:
        return observe_replay(replay), "replay"
    proxmox = require_proxmox(config)
    return observe_live(proxmox.as_adapter_config()), "live"


def _load_desired(path: str) -> list[Desired]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return [Desired(**item) for item in data]


def main():
    cli()


if __name__ == "__main__":
    main()
