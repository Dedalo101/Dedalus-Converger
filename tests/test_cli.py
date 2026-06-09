from pathlib import Path

import yaml
from click.testing import CliRunner

from converger.cli import cli


def test_plan_command_with_replay(tmp_path: Path):
    runner = CliRunner()
    config_file = tmp_path / "converger.yaml"
    config_file.write_text(
        yaml.safe_dump(
            {
                "artifacts": {
                    "current": str(tmp_path / "current.json"),
                    "plan": str(tmp_path / "plan.json"),
                    "result": str(tmp_path / "result.json"),
                }
            }
        ),
        encoding="utf-8",
    )

    result = runner.invoke(
        cli,
        [
            "-c",
            str(config_file),
            "plan",
            "--desired",
            "examples/desired.yaml",
            "--replay",
            "examples/replay.json",
        ],
    )

    assert result.exit_code == 0, result.output
    plan_output = tmp_path / "plan.json"
    current_output = tmp_path / "current.json"
    assert plan_output.exists()
    assert current_output.exists()
    plan_text = plan_output.read_text(encoding="utf-8")
    assert '"action": "start"' in plan_text
    assert '"action": "resize"' in plan_text
    assert '"target_cpus": 8' in plan_text


def test_apply_refuses_replay_mode():
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "apply",
            "--desired",
            "examples/desired.yaml",
            "--replay",
            "examples/replay.json",
            "--confirm",
        ],
    )

    assert result.exit_code == 1
    assert "refused" in result.output.lower()
