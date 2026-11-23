# Research: Library Book-Loan Service

## Decision: Python 3.12 with FastAPI and SQLAlchemy

**Rationale**: The requested stack provides typed request validation, JSON HTTP
routing, and a database abstraction suitable for a durable SQLite-backed service.
It also integrates directly with pytest and httpx `TestClient` for contract-level
API tests.

**Alternatives considered**: A different web framework would not satisfy the
requested stack; direct SQLite access would duplicate persistence and transaction
concerns that SQLAlchemy already addresses.

## Decision: File-backed SQLite for runtime and in-memory SQLite for tests

**Rationale**: A file-backed SQLite database preserves books, members, and loans
across service restarts without requiring an external service. Tests use an
isolated in-memory database so each test run is deterministic and does not modify
runtime data.

**Alternatives considered**: An external database is outside the requested
single-service scope. A runtime in-memory database violates the persistence
clarification.

## Decision: Transactional loan creation

**Rationale**: Loan creation must check both available book copies and the
member's active-loan limit as one atomic operation. The service will perform
these checks inside a database transaction and commit the loan only after both
limits pass.

**Alternatives considered**: Separate check and insert operations could allow
concurrent requests to exceed inventory or the three-loan member limit.

## Decision: Environment-driven configuration

**Rationale**: The database URL and other runtime settings will be read from
environment variables. No credentials or environment-specific secrets belong in
source code.

**Alternatives considered**: Hardcoded defaults for secrets or deployment
configuration violate the constitution. A non-secret local SQLite fallback may
be documented as a development default, but deployment configuration remains
environment-controlled.

## Decision: Contract tests with exactly one acceptance test per criterion

**Rationale**: The test suite will contain one primary pytest test for each of
AC-1 through AC-14, with the corresponding AC identifier in the test name.
Shared fixtures may create prerequisite records, but a test will assert only its
criterion's pass/fail behavior. This makes the acceptance mapping auditable.

**Alternatives considered**: Combining multiple acceptance criteria in one test
would obscure failures and violate the requested one-to-one mapping.

## Decision: Ordered harness gates

**Rationale**: `.harness/run_harness.py` will run Ruff, Bandit, and pytest in
that order, capture stdout, stderr, and exit code under a new
`evidence/harness-results/run-N/` directory, and print a PASS/FAIL summary.
Existing recorded results are immutable.

**Alternatives considered**: Running gates in an arbitrary order or overwriting
recorded evidence would reduce reproducibility and violate project safeguards.
