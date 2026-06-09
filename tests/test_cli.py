from pathlib import Path

from click.testing import CliRunner

from converger.cli import cli


def test_plan_command_with_replay(tmp_path: Path):
    runner = CliRunner()
    output = tmp_path / "plan.json"
    result = runner.invoke(
        cli,
        [
            "plan",
            "--desired",
            "examples/desired.yaml",
            "--replay",
            "examples/replay.json",
            "--output",
            str(output),
        ],
    )

    assert result.exit_code == 0, result.output
    assert output.exists()
    assert '"action": "start"' in output.read_text(encoding="utf-8")
    assert '"action": "resize"' in output.read_text(encoding="utf-8")


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
