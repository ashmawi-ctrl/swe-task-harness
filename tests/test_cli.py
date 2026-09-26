import json
from pathlib import Path

from swe_harness.cli import main

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_TASK = (
    PROJECT_ROOT
    / "examples"
    / "slugify-regression"
    / "task.json"
)


def test_cli_reports_passing_task(capsys) -> None:
    exit_code = main(["run", str(EXAMPLE_TASK)])

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "[PASS] baseline" in output
    assert "[PASS] verification-1" in output
    assert "Result: PASS" in output


def test_cli_json_output_is_machine_readable(capsys) -> None:
    exit_code = main(
        [
            "run",
            str(EXAMPLE_TASK),
            "--format",
            "json",
        ]
    )

    assert exit_code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["passed"] is True
    assert output["task_name"] == "Collapse repeated whitespace in slugify"
