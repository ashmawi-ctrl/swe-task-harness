# SWE Task Harness

A small local harness for evaluating software-engineering tasks in an isolated, repeatable workflow.

The goal is to make a bug-fix task explicit:

1. reproduce the failing baseline
2. verify that a proposed patch applies cleanly
3. run focused verification
4. run the broader regression suite
5. capture commands, exit codes, stdout, stderr, and timing

The harness is intended for trusted local task definitions and does not execute untrusted tasks safely by itself.
