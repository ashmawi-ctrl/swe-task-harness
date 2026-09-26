import json
from pathlib import Path

import pytest

from swe_harness.spec import TaskDefinitionError, load_task


def write_task(tmp_path: Path, **overrides) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    patch = tmp_path / "solution.patch"
    patch.write_text("", encoding="utf-8")

    payload = {
        "name": "Example",
        "repo_path": "repo",
        "patch_path": "solution.patch",
        "baseline_command": ["python", "-c", "raise SystemExit(1)"],
        "verification_commands": [["python", "-c", "pass"]],
        "expected_baseline_exit_codes": [1],
        "timeout_seconds": 5,
    }
    payload.update(overrides)

    task = tmp_path / "task.json"
    task.write_text(json.dumps(payload), encoding="utf-8")
    return task


def test_load_task_resolves_paths_relative_to_task_file(tmp_path: Path) -> None:
    spec = load_task(write_task(tmp_path))

    assert spec.name == "Example"
    assert spec.repo_path == tmp_path / "repo"
    assert spec.patch_path == tmp_path / "solution.patch"
    assert spec.baseline_command[0] == "python"


def test_shell_string_commands_are_rejected(tmp_path: Path) -> None:
    task = write_task(
        tmp_path,
        baseline_command="pytest -q",
    )

    with pytest.raises(TaskDefinitionError):
        load_task(task)


def test_timeout_must_be_positive(tmp_path: Path) -> None:
    task = write_task(
        tmp_path,
        timeout_seconds=0,
    )

    with pytest.raises(TaskDefinitionError):
        load_task(task)
