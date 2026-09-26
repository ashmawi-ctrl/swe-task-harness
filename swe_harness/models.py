from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TaskSpec:
    name: str
    repo_path: Path
    patch_path: Path
    baseline_command: tuple[str, ...]
    verification_commands: tuple[tuple[str, ...], ...]
    expected_baseline_exit_codes: tuple[int, ...] = (1,)
    timeout_seconds: float = 60.0


@dataclass(frozen=True)
class CommandResult:
    command: tuple[str, ...]
    exit_code: int | None
    stdout: str
    stderr: str
    duration_seconds: float
    timed_out: bool = False


@dataclass(frozen=True)
class StageResult:
    name: str
    passed: bool
    detail: str
    command: CommandResult | None = None


@dataclass(frozen=True)
class EvaluationResult:
    task_name: str
    passed: bool
    stages: tuple[StageResult, ...]
