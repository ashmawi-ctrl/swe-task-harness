import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .runner import evaluate_task
from .spec import TaskDefinitionError, load_task


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="swe-task-harness",
        description=(
            "Reproduce a failing task, apply a patch, and run verification."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser("run", help="Evaluate one task definition")
    run.add_argument("task", type=Path)
    run.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        dest="output_format",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        task = load_task(args.task)
    except TaskDefinitionError as exc:
        print(f"Task definition error: {exc}")
        return 2

    result = evaluate_task(task)

    if args.output_format == "json":
        print(json.dumps(_result_to_dict(result), indent=2))
    else:
        _print_text(result)

    return 0 if result.passed else 1


def _print_text(result) -> None:
    print(f"Task: {result.task_name}")
    for stage in result.stages:
        marker = "PASS" if stage.passed else "FAIL"
        print(f"[{marker}] {stage.name}: {stage.detail}")
        if stage.command is not None:
            command = " ".join(stage.command.command)
            duration = stage.command.duration_seconds
            print(f"       $ {command}")
            print(
                "       "
                f"exit={stage.command.exit_code} "
                f"duration={duration:.3f}s"
            )
    print()
    print("Result: PASS" if result.passed else "Result: FAIL")


def _result_to_dict(result) -> dict:
    data = asdict(result)
    for stage in data["stages"]:
        command = stage.get("command")
        if command is not None:
            command["command"] = list(command["command"])
    return data


if __name__ == "__main__":
    raise SystemExit(main())
