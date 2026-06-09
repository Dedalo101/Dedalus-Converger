import json
import sys
from pathlib import Path

import click
import yaml

from . import contract
from .adapters.proxmox_apply import ProxmoxApplier
from .apply import apply as apply_steps
from .apply import audit as audit_steps
from .artifacts import write_current, write_plan, write_post_apply
from .config import ConvergerConfig, load_config, require_proxmox
from .model import Desired
from .observe import observe_from_config
from .plan import plan
from .safety import PolicyViolation, enforce_safety
from .verify import verify_convergence

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


def _source_options():
    return click.option(
        "--source",
        "-s",
        type=click.Choice(["proxmox", "aws", "hetzner", "replay", "dfir"]),
        default=None,
        help="Observation source override",
    )


@cli.command()
@click.option("--desired", "-d", type=click.Path(exists=True), required=True)
@click.option("--replay", "-r", type=click.Path(exists=True))
@click.option("--dfir", type=click.Path(exists=True))
@_source_options()
@click.pass_context
def audit(
    ctx: click.Context,
    desired: str,
    replay: str | None,
    dfir: str | None,
    source: str | None,
) -> None:
    """Audit mode — zero side effects, print plan."""
    config: ConvergerConfig = ctx.obj["config"]
    try:
        current, resolved = _run_observation(
            config, source=source, replay=replay, dfir=dfir
        )
        current_path = write_current(current, config.artifacts.current)
        desired_objs = _load_desired(desired)
        steps = plan(current, desired_objs)
        safe_steps = enforce_safety(steps)
        audit_steps(safe_steps)
        click.echo(f"Observation ({resolved}) written to {current_path}")
    except (PolicyViolation, Exception) as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@cli.command("plan")
@click.option("--desired", "-d", type=click.Path(exists=True), required=True)
@click.option("--replay", "-r", type=click.Path(exists=True))
@click.option("--dfir", type=click.Path(exists=True))
@_source_options()
@click.option("--output", "-o", type=click.Path(), default=None)
@click.pass_context
def plan_cmd(
    ctx: click.Context,
    desired: str,
    replay: str | None,
    dfir: str | None,
    source: str | None,
    output: str | None,
) -> None:
    """Plan mode — write structured plan.json."""
    config: ConvergerConfig = ctx.obj["config"]
    output_path = output or config.artifacts.plan
    try:
        current, resolved = _run_observation(
            config, source=source, replay=replay, dfir=dfir
        )
        current_path = write_current(current, config.artifacts.current)
        desired_objs = _load_desired(desired)
        steps = plan(current, desired_objs)
        safe_steps = enforce_safety(steps)
        plan_path = write_plan(safe_steps, output_path)
        click.echo(f"Observation ({resolved}) written to {current_path}")
        click.echo(f"Plan written to {plan_path}")
    except (PolicyViolation, Exception) as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@cli.command("apply")
@click.option("--desired", "-d", type=click.Path(exists=True), required=True)
@click.option("--replay", "-r", type=click.Path(exists=True))
@click.option("--dry-run", is_flag=True, help="Record API calls without executing")
@click.option("--confirm", is_flag=True, help="Explicit confirmation required to apply")
@click.pass_context
def apply_cmd(
    ctx: click.Context,
    desired: str,
    replay: str | None,
    dry_run: bool,
    confirm: bool,
) -> None:
    """Apply mode — mutating phase (Proxmox only)."""
    config: ConvergerConfig = ctx.obj["config"]

    if replay:
        click.echo("Apply with --replay is refused — replay is read-only.", err=True)
        sys.exit(1)

    if not dry_run and not confirm:
        click.echo(
            "Apply requires explicit --confirm flag (or use --dry-run).", err=True
        )
        sys.exit(1)

    try:
        proxmox = require_proxmox(config)
        current, resolved = _run_observation(config, source="proxmox")
        current_path = write_current(current, config.artifacts.current)
        desired_objs = _load_desired(desired)
        steps = plan(current, desired_objs)
        safe_steps = enforce_safety(steps)
        click.echo(f"Observation ({resolved}) written to {current_path}")

        if not dry_run:
            click.confirm(f"Apply {len(safe_steps)} changes?", abort=True)

        applier = ProxmoxApplier(proxmox.as_adapter_config(), dry_run=dry_run)
        results = apply_steps(
            safe_steps,
            executor=applier.apply,
            output=config.artifacts.result,
            dry_run=dry_run,
        )

        failed = [item for item in results if item["status"] == "failed"]
        if failed:
            click.echo(f"{len(failed)} step(s) failed.", err=True)
            sys.exit(1)

        if dry_run:
            click.echo("Dry-run complete. No mutations executed.")
            return

        post_current, _ = _run_observation(config, source="proxmox")
        post_path = write_current(post_current, config.artifacts.post_apply)
        report = verify_convergence(post_current, desired_objs)
        report_path = write_post_apply(report, _post_apply_report_path(config))
        click.echo(f"Post-apply observation written to {post_path}")

        if report.converged:
            click.echo(f"Convergence verified. Report: {report_path}")
            click.echo("Applied.")
            return

        click.echo("Post-apply convergence check failed:", err=True)
        click.echo(json.dumps(report.as_dict(), indent=2), err=True)
        sys.exit(1)
    except (PolicyViolation, Exception) as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


def _run_observation(
    config: ConvergerConfig,
    *,
    source: str | None = None,
    replay: str | None = None,
    dfir: str | None = None,
):
    return observe_from_config(
        config,
        source=source,
        replay_path=replay,
        dfir_path=dfir,
    )


def _post_apply_report_path(config: ConvergerConfig) -> str:
    path = Path(config.artifacts.post_apply)
    if path.suffix == ".json":
        return str(path.with_name(f"{path.stem}_report{path.suffix}"))
    return f"{config.artifacts.post_apply}_report.json"


def _load_desired(path: str) -> list[Desired]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return [Desired(**item) for item in data]


def main():
    cli()


if __name__ == "__main__":
    main()
