# Quickstart Validation: Library Book-Loan Service

## Prerequisites

- Python 3.12
- Project dependencies installed from the project dependency manifest
- A writable runtime database URL supplied through `LIBRARY_DATABASE_URL`

## Run the service

Set `LIBRARY_DATABASE_URL` through the environment, then start the
FastAPI application using the project's documented application entry point.
The service must use a file-backed SQLite database for runtime data.

## Run acceptance tests

Run pytest against `tests/`. The suite must contain exactly one primary test for
each acceptance criterion, with names containing `AC-1` through `AC-14`.

Expected result: all mandatory tests pass and measured coverage is at least 80%.

## Run quality gates

Run the harness:

```text
python .harness/run_harness.py
```

The harness runs Ruff, Bandit, and pytest in that order. It writes each gate's
stdout, stderr, and exit code to a new `evidence/harness-results/run-N/`
directory and prints a final PASS/FAIL summary. Existing evidence directories
and recorded harness results must not be edited.

## Manual contract checks

The endpoint shapes, statuses, schemas, and error requirements are defined in
[contracts/openapi.yaml](contracts/openapi.yaml). Entity constraints and
state invariants are defined in [data-model.md](data-model.md).

At minimum, verify:

1. Create a valid book and member.
2. Create loans until inventory or the three-active-loan member limit is reached.
3. Return a loan and verify availability is restored.
4. Query overdue loans using records before, on, and after today's UTC date.
5. Restart the service and verify records remain available.
