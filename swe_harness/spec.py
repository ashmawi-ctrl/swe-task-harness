import json
from pathlib import Path
from typing import Any

from .models import TaskSpec


class TaskDefinitionError(ValueError):
    pass


def load_task(path: str | Path) -> TaskSpec:
    task_file = Path(path).resolve()

    try:
        raw = json.loads(task_file.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise TaskDefinitionError(f"task file not found: {task_file}") from exc
    except json.JSONDecodeError as exc:
        raise TaskDefinitionError(
            f"invalid task JSON at line {exc.lineno}, column {exc.colno}"
        ) from exc

    if not isinstance(raw, dict):
        raise TaskDefinitionError("task definition must be a JSON object")

    root = task_file.parent
    name = _require_string(raw, "name")
    repo_path = root / _require_string(raw, "repo_path")
    patch_path = root / _require_string(raw, "patch_path")
    baseline = _parse_command(raw.get("baseline_command"), "baseline_command")

    verification_raw = raw.get("verification_commands")
    if not isinstance(verification_raw, list) or not verification_raw:
        raise TaskDefinitionError(
            "verification_commands must be a non-empty list"
        )

    verification = tuple(
        _parse_command(command, f"verification_commands[{index}]")
        for index, command in enumerate(verification_raw)
    )

    expected_codes_raw = raw.get("expected_baseline_exit_codes", [1])
    if (
        not isinstance(expected_codes_raw, list)
        or not expected_codes_raw
        or not all(isinstance(code, int) for code in expected_codes_raw)
    ):
        raise TaskDefinitionError(
            "expected_baseline_exit_codes must be a non-empty integer list"
        )

    timeout_raw = raw.get("timeout_seconds", 60)
    if not isinstance(timeout_raw, (int, float)) or timeout_raw <= 0:
        raise TaskDefinitionError("timeout_seconds must be greater than 0")

    if not repo_path.is_dir():
        raise TaskDefinitionError(f"repo_path is not a directory: {repo_path}")
    if not patch_path.is_file():
        raise TaskDefinitionError(f"patch_path is not a file: {patch_path}")

    return TaskSpec(
        name=name,
        repo_path=repo_path,
        patch_path=patch_path,
        baseline_command=baseline,
        verification_commands=verification,
        expected_baseline_exit_codes=tuple(expected_codes_raw),
        timeout_seconds=float(timeout_raw),
    )


def _require_string(raw: dict[str, Any], field: str) -> str:
    value = raw.get(field)
    if not isinstance(value, str) or not value.strip():
        raise TaskDefinitionError(f"{field} must be a non-empty string")
    return value


def _parse_command(value: Any, field: str) -> tuple[str, ...]:
    if (
        not isinstance(value, list)
        or not value
        or not all(isinstance(part, str) and part for part in value)
    ):
        raise TaskDefinitionError(
            f"{field} must be a non-empty list of command arguments"
        )
    return tuple(value)
