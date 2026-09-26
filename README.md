# SWE Task Harness

[![quality](https://github.com/ashmawi-ctrl/swe-task-harness/actions/workflows/quality.yml/badge.svg)](https://github.com/ashmawi-ctrl/swe-task-harness/actions/workflows/quality.yml)

A small local harness for evaluating software-engineering bug-fix tasks through a reproducible sequence:

1. copy the target repository into a temporary workspace
2. run the baseline command and prove the bug is reproducible
3. verify that the proposed patch applies cleanly
4. apply the patch
5. run focused or full verification commands
6. capture exit codes, stdout, stderr, timing, and final pass/fail state

The project is designed to practice the same engineering habits used when working on unfamiliar repositories: reproduce first, patch second, verify last.

## Why this exists

A patch can look reasonable while still being impossible to evaluate consistently.

Useful software-engineering tasks should make these questions explicit:

- Does the reported bug actually reproduce?
- What exact command proves the baseline failure?
- Does the patch apply cleanly to the intended code?
- Does the target regression pass after the change?
- Did the patch break anything else?
- Can another engineer rerun the same evaluation?

This harness turns those steps into a repeatable task definition.

## Important safety boundary

Task definitions contain executable commands.

**Only run task files you trust.**

The temporary workspace protects the source fixture from modification, but it is not a security sandbox for hostile code. Use a container or another isolation layer when evaluating untrusted repositories.

## Install

Python 3.11+ and Git are required.

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -e ".[dev]"
```

## Run the included task

```bash
swe-task-harness run examples/slugify-regression/task.json
```

Expected flow:

```text
Task: Collapse repeated whitespace in slugify
[PASS] baseline: expected failing baseline reproduced
[PASS] patch-check: patch applies cleanly
[PASS] patch-apply: patch applied
[PASS] verification-1: verification passed

Result: PASS
```

The baseline is expected to fail. If it unexpectedly passes, the evaluation stops because the task is no longer proving the reported bug.

## JSON output

```bash
swe-task-harness run \
  examples/slugify-regression/task.json \
  --format json
```

This makes the result easy to consume from CI or another evaluator.

## Task definition

Tasks are JSON files:

```json
{
  "name": "Collapse repeated whitespace in slugify",
  "repo_path": "repo",
  "patch_path": "solution.patch",
  "baseline_command": [
    "python",
    "-m",
    "pytest",
    "tests/test_slugify.py",
    "-q"
  ],
  "verification_commands": [
    [
      "python",
      "-m",
      "pytest",
      "-q"
    ]
  ],
  "expected_baseline_exit_codes": [1],
  "timeout_seconds": 30
}
```

Paths are resolved relative to the task JSON file.

Commands are represented as argument arrays instead of shell strings. That keeps command execution explicit and avoids depending on shell parsing.

## Evaluation stages

### 1. Baseline

The repository fixture is copied into a temporary workspace and the baseline command runs there.

The task only proceeds when the exit code matches one of `expected_baseline_exit_codes`.

### 2. Patch check

Before changing the copied repository:

```bash
git apply --check solution.patch
```

must succeed.

### 3. Patch application

The patch is then applied to the temporary copy.

The source fixture inside the repository remains unchanged.

### 4. Verification

Every command in `verification_commands` must exit with status 0.

The evaluator stops at the first failed stage and records the command output and duration.

## Example task layout

```text
examples/slugify-regression/
  task.md
  task.json
  solution.patch
  repo/
    string_utils.py
    tests/
      test_slugify.py
```

`task.md` is the human-readable problem statement.

`task.json` is the executable evaluation contract.

`solution.patch` is the candidate fix.

`repo/` is the known baseline code.

## Local quality workflow

```bash
make install
make quality
make example
```

## Docker

Build:

```bash
docker build -t swe-task-harness .
```

Run the included task:

```bash
docker run --rm swe-task-harness \
  run examples/slugify-regression/task.json
```

The image includes Git and the development dependencies required by the bundled example.

## Project structure

```text
swe_harness/
  cli.py       command-line interface
  models.py    task and stage result models
  runner.py    temporary workspace and command execution
  spec.py      task definition validation

tests/
  test_cli.py
  test_runner.py
  test_spec.py
```

## Engineering workflow

The first evaluator implementation is tracked through:

- [Issue #1](https://github.com/ashmawi-ctrl/swe-task-harness/issues/1)
- feature branch: `feat/task-evaluator`
- an intentionally failing baseline fixture
- a real unified patch
- regression tests for the evaluator
- GitHub Actions CI
- reviewable pull request

## Design choices

### Baseline failure is part of the contract

A bug-fix task should prove the bug before applying a solution. If the baseline passes, the task definition may be stale or incorrect.

### Source fixtures are never modified in place

Every evaluation works from a temporary copied workspace, which makes repeated runs deterministic.

### Patch applicability is checked separately

`git apply --check` separates an invalid patch from a patch whose code compiles or tests incorrectly.

### Command timeouts are recorded

A hung test suite is an evaluation failure, not an infinite wait.

## Current limitations

- commands are trusted and run on the host/container
- no network isolation
- no CPU or memory quotas
- no repository cloning yet; tasks use local fixtures
- no patch scoring or partial-credit model
- no test selection heuristics

## Next improvements

- clone a pinned Git repository/commit as a task source
- Docker-per-task execution
- resource limits
- environment variables in task definitions
- structured artifact directory
- patch diff statistics
- hidden/public test separation
- batch evaluation of multiple candidate patches

## License

MIT
