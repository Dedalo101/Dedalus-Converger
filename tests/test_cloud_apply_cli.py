from pathlib import Path

import yaml
from click.testing import CliRunner

from converger.cli import cli


def test_apply_refuses_dfir_source(tmp_path: Path):
    runner = CliRunner()
    config_file = tmp_path / "converger.yaml"
    config_file.write_text(
        yaml.safe_dump({"source": "dfir"}),
        encoding="utf-8",
    )

    result = runner.invoke(
        cli,
        [
            "-c",
            str(config_file),
            "apply",
            "--desired",
            "examples/desired.yaml",
            "--dry-run",
        ],
    )

    assert result.exit_code == 1
    assert "not supported" in result.output.lower()


def test_apply_aws_dry_run(tmp_path: Path, monkeypatch):
    runner = CliRunner()
    config_file = tmp_path / "converger.yaml"
    result_file = tmp_path / "result.json"
    config_file.write_text(
        f"""
source: aws
aws:
  region: eu-west-1
artifacts:
  result: {result_file}
""".strip(),
        encoding="utf-8",
    )

    from converger import cli as cli_module
    from converger.model import VMState

    def fake_observe(*args, **kwargs):
        return (
            [
                VMState(
                    vmid=100,
                    name="web-01",
                    status="stopped",
                    external_id="i-abc",
                    instance_type="t3.small",
                    source="aws",
                ),
                VMState(
                    vmid=101,
                    name="dev-api-01",
                    status="running",
                    cpus=8,
                    maxmem=17179869184,
                    external_id="i-def",
                    instance_type="t3.large",
                    source="aws",
                ),
            ],
            "aws",
        )

    monkeypatch.setattr(cli_module, "observe_from_config", fake_observe)

    result = runner.invoke(
        cli,
        [
            "-c",
            str(config_file),
            "apply",
            "--desired",
            "examples/desired.yaml",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "DRY-RUN" in result.output
    assert "StartInstances" in result.output
    assert result_file.exists()
