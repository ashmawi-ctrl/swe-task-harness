# Task: collapse repeated whitespace in `slugify`

## Problem

`slugify()` currently replaces each individual space with a dash.

That means:

```python
slugify("Hello   World")
```

returns:

```text
hello---world
```

instead of:

```text
hello-world
```

## Expected behavior

- leading and trailing whitespace is removed
- a run of one or more whitespace characters becomes one dash
- existing simple single-space behavior still passes

## Verification

The focused regression suite is:

```bash
python -m pytest tests/test_slugify.py -q
```

The task definition expects the baseline to fail before the patch and the full suite to pass after the patch.
