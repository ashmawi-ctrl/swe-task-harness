.PHONY: install lint test quality example docker-build

install:
	python -m pip install -e ".[dev]"

lint:
	ruff check .

test:
	pytest

quality: lint test

example:
	swe-task-harness run examples/slugify-regression/task.json

docker-build:
	docker build -t swe-task-harness .
