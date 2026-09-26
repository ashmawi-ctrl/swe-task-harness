import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from .models import CommandResult, EvaluationResult, StageResult, TaskSpec


def evaluate_task(task: TaskSpec) -> EvaluationResult:
    stages: list[StageResult] = []

    with tempfile.TemporaryDirectory(prefix="swe-task-") as temp_dir:
        workspace = Path(temp_dir) / "repo"
        shutil.copytree(task.repo_path, workspace)

        baseline = run_command(
            task.baseline_command,
            cwd=workspace,
            timeout_seconds=task.timeout_seconds,
        )
        baseline_passed = (
            not baseline.timed_out
            and baseline.exit_code in task.expected_baseline_exit_codes
        )
        stages.append(
            StageResult(
                name="baseline",
                passed=baseline_passed,
                detail=(
                    "expected failing baseline reproduced"
                    if baseline_passed
                    else (
                        "baseline did not fail with an expected exit code"
                    )
                ),
                command=baseline,
            )
        )
        if not baseline_passed:
            return EvaluationResult(task.name, False, tuple(stages))

        patch_check = run_command(
            ("git", "apply", "--check", str(task.patch_path)),
            cwd=workspace,
            timeout_seconds=task.timeout_seconds,
        )
        patch_check_passed = (
            not patch_check.timed_out and patch_check.exit_code == 0
        )
        stages.append(
            StageResult(
                name="patch-check",
                passed=patch_check_passed,
                detail=(
                    "patch applies cleanly"
                    if patch_check_passed
                    else "patch cannot be applied cleanly"
                ),
                command=patch_check,
            )
        )
        if not patch_check_passed:
            return EvaluationResult(task.name, False, tuple(stages))

        patch_apply = run_command(
            ("git", "apply", str(task.patch_path)),
            cwd=workspace,
            timeout_seconds=task.timeout_seconds,
        )
        patch_apply_passed = (
            not patch_apply.timed_out and patch_apply.exit_code == 0
        )
        stages.append(
            StageResult(
                name="patch-apply",
                passed=patch_apply_passed,
                detail=(
                    "patch applied"
                    if patch_apply_passed
                    else "patch application failed"
                ),
                command=patch_apply,
            )
        )
        if not patch_apply_passed:
            return EvaluationResult(task.name, False, tuple(stages))

        for index, command in enumerate(task.verification_commands, start=1):
            result = run_command(
                command,
                cwd=workspace,
                timeout_seconds=task.timeout_seconds,
            )
            passed = not result.timed_out and result.exit_code == 0
            stages.append(
                StageResult(
                    name=f"verification-{index}",
                    passed=passed,
                    detail=(
                        "verification passed"
                        if passed
                        else "verification failed"
                    ),
                    command=result,
                )
            )
            if not passed:
                return EvaluationResult(task.name, False, tuple(stages))

    return EvaluationResult(task.name, True, tuple(stages))


def run_command(
    command: tuple[str, ...],
    *,
    cwd: Path,
    timeout_seconds: float,
) -> CommandResult:
    started = time.perf_counter()

    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        duration = time.perf_counter() - started
        return CommandResult(
            command=command,
            exit_code=None,
            stdout=_to_text(exc.stdout),
            stderr=_to_text(exc.stderr),
            duration_seconds=duration,
            timed_out=True,
        )

    duration = time.perf_counter() - started
    return CommandResult(
        command=command,
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        duration_seconds=duration,
    )


def _to_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value
