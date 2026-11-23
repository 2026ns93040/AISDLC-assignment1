# Implementation Plan: Library Book-Loan Service

**Branch**: `001-book-loan-service` | **Date**: 2026-11-23 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-book-loan-service/spec.md`

## Summary

Build a JSON HTTP library lending service using Python 3.12, FastAPI, and
SQLAlchemy. Runtime records use file-backed SQLite for restart persistence;
tests use isolated in-memory SQLite. The API implements catalog and member
creation, loan and return lifecycle rules, availability, overdue lookup, JSON
errors, and transactional limits. Ruff, Bandit, and pytest run through the
ordered `.harness/run_harness.py` evidence runner.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, SQLAlchemy, pytest, httpx `TestClient`, Ruff,
Bandit

**Storage**: SQLite file for runtime, configured through `LIBRARY_DATABASE_URL`;
SQLite in-memory database for tests

**Testing**: pytest with httpx `TestClient`; one primary test per AC-1 through
AC-14, each test name containing its AC identifier

**Target Platform**: Python service process on a supported server environment

**Project Type**: Web service

**Performance Goals**: Meet the supplied acceptance scenarios with ordinary
single-service SQLite workloads; no higher throughput target is specified.

**Constraints**: All mandatory tests pass, coverage is at least 80%, Ruff has
zero errors, Bandit has zero medium/high findings, no hardcoded secrets, and
configuration is environment-driven. Existing harness evidence is immutable.

**Scale/Scope**: Initial single-service library catalog and lending workflow;
no reservations, renewals, fines, notifications, deletion, or authentication.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Small, purposeful changes**: PASS — implementation is limited to the
  requested API, tests, harness, and directly related SDD artifacts.
- **Preserve intended behavior**: PASS — contracts map directly to AC-1 through
  AC-14 and clarified rules.
- **Verify requirements with tests**: PASS — the plan requires one-to-one
  acceptance tests, mandatory test success, and at least 80% coverage.
- **Make failures explicit**: PASS — all API errors use JSON `detail`; runtime
  configuration is environment-driven and secrets are excluded.
- **Keep work reviewable**: PASS — source is under `src/`, tests under `tests/`,
  and harness evidence is append-only.
- **Ruff/Bandit gates**: PASS — the harness runs both without disabling rules.
- **SDD governance**: PASS — specification changes remain in the feature
  artifacts and are documented.

## Phase 0: Research

Research decisions are recorded in [research.md](research.md). They resolve the
requested framework, persistence, transaction, configuration, acceptance-test
mapping, and harness requirements.

## Phase 1: Design

Design artifacts:

- [data-model.md](data-model.md) defines Book, Member, Loan, relationships, and
  invariants.
- [contracts/openapi.yaml](contracts/openapi.yaml) defines all public routes,
  request/response shapes, statuses, and JSON errors.
- [quickstart.md](quickstart.md) defines end-to-end validation and harness
  evidence expectations.

## Project Structure

### Documentation

```text
specs/001-book-loan-service/
├── plan.md
├── research.md
├── data-model.md
├── contracts/
│   └── openapi.yaml
├── quickstart.md
└── tasks.md
```

### Source Code

```text
src/
├── library_service/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── services.py
│   ├── api.py
│   └── main.py

tests/
├── conftest.py
└── test_book_loan_api.py

.harness/
└── run_harness.py

evidence/
└── harness-results/
    └── run-N/
```

**Structure Decision**: Use one Python web-service package under `src/` with
separate configuration, database, persistence models, API schemas, business
services, and application assembly. Keep acceptance tests in one focused module
with shared fixtures. Keep the harness separate from application code and write
new evidence runs without altering prior results.

## Implementation Notes

- Configure the runtime SQLite URL through an environment variable and expose
  dependency overrides for the in-memory test database. The canonical runtime
  variable is `LIBRARY_DATABASE_URL`.
- Use database uniqueness constraints for ISBN and case-insensitive member
  email, translating conflicts to 409 responses.
- Use explicit transaction boundaries around loan eligibility checks and loan
  insertion; ensure concurrent requests cannot oversubscribe inventory or the
  member limit.
- Centralize JSON error handling so validation, not-found, conflict, and
  unexpected service errors follow the `detail` contract.
- Keep date calculations in UTC: `due_date` is the UTC calendar date 14 days
  after `loaned_at`; overdue means strictly before today's UTC date.
- Name the 14 primary tests with `AC-1` through `AC-14` and ensure each maps
  one-to-one to the corresponding acceptance criterion.
- The harness must run `ruff`, then `bandit`, then `pytest`, capture each gate's
  stdout, stderr, and exit code, and print a PASS/FAIL summary.

## Complexity Tracking

No constitution violations require justification.
