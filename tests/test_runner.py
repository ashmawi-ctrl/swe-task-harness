from pathlib import Path

from swe_harness.runner import evaluate_task, run_command
from swe_harness.spec import load_task


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_TASK = (
    PROJECT_ROOT
    / "examples"
    / "slugify-regression"
    / "task.json"
)


def test_example_task_reproduces_bug_and_passes_after_patch() -> None:
    result = evaluate_task(load_task(EXAMPLE_TASK))

    assert result.passed is True
    assert [stage.name for stage in result.stages] == [
        "baseline",
        "patch-check",
        "patch-apply",
        "verification-1",
    ]
    assert all(stage.passed for stage in result.stages)


def test_command_timeout_is_reported(tmp_path: Path) -> None:
    result = run_command(
        (
            "python",
            "-c",
            "import time; time.sleep(1)",
        ),
        cwd=tmp_path,
        timeout_seconds=0.01,
    )

    assert result.timed_out is True
    assert result.exit_code is None
