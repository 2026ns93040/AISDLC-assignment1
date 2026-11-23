---

description: "Implementation tasks for the Library Book-Loan Service"
---

# Tasks: Library Book-Loan Service

**Input**: Design documents from `/specs/001-book-loan-service/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/), and
[quickstart.md](quickstart.md)

**Implementation rule**: The harness and all AC-derived tests MUST be created
before application implementation. Tests, Ruff configuration, and Bandit
configuration MUST NOT be modified to make checks pass.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the Python project, dependency manifest, source layout,
and immutable quality-gate runner before implementation.

- [ ] T001 Create the Python 3.12 project manifest with FastAPI, SQLAlchemy, pytest, httpx, pytest-cov, Ruff, and Bandit dependencies in `pyproject.toml`
- [ ] T002 [P] Create the application package layout and package marker in `src/library_service/__init__.py`
- [ ] T003 [P] Create the test and harness directories with placeholder package-safe paths in `tests/conftest.py` and `.harness/run_harness.py`
- [ ] T004 [P] Implement the ordered Ruff, Bandit, pytest harness with new run-number allocation, stdout/stderr/exit-code files, and PASS/FAIL summary in `.harness/run_harness.py`; never overwrite existing `evidence/harness-results/run-N/` records
- [ ] T005 Configure the required Ruff zero-error gate, Bandit medium/high finding gate, pytest coverage threshold, and source/test discovery in `pyproject.toml`; treat this configuration as immutable after setup

---

## Phase 2: Foundational (Tests Before Implementation)

**Purpose**: Define the complete acceptance contract and test fixtures before
writing API, model, or service implementation.

**⚠️ CRITICAL**: T004 and T006–T007 MUST be complete before implementation
tasks T008 onward begin. The initial test run is expected to fail until the
application exists.

- [ ] T006 Create isolated in-memory SQLite and httpx `TestClient` fixtures, environment configuration fixtures, and reusable record factories in `tests/conftest.py`
- [ ] T007 Create exactly one primary pytest test for each AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-8, AC-9, AC-10, AC-11, AC-12, AC-13, and AC-14, with the matching AC identifier in each test name, covering the routes and statuses in `tests/test_book_loan_api.py`; every error assertion must verify JSON content and a `detail` field; do not change these tests after implementation to make checks pass
- [ ] T008 Run `.harness/run_harness.py` against the pre-implementation test suite and record the expected failing baseline in a new `evidence/harness-results/run-N/` directory without editing prior evidence
- [ ] T009 Implement environment-driven settings using `LIBRARY_DATABASE_URL` and the runtime SQLite engine/session lifecycle in `src/library_service/config.py` and `src/library_service/database.py`
- [ ] T010 Implement SQLAlchemy Book, Member, and Loan models with relationships, uniqueness constraints, nullable return state, and indexes in `src/library_service/models.py`; cite `data-model.md` for `Book.id`, `Book.title`, `Book.author`, `Book.isbn`, `Book.total_copies`, `Member.id`, `Member.name`, `Member.email`, `Loan.id`, `Loan.book_id`, `Loan.member_id`, `Loan.loaned_at`, `Loan.due_date`, and `Loan.returned_at`
- [ ] T011 Implement request/response schemas and the shared JSON `detail` error contract in `src/library_service/schemas.py`
- [ ] T012 Create FastAPI application assembly, database initialization, and dependency wiring in `src/library_service/main.py`

**Checkpoint**: The complete acceptance suite exists before implementation, and
the foundational application can start with runtime configuration supplied by
environment variables.

---

## Phase 3: User Story 1 - Manage the Catalog and Members (Priority: P1) 🎯 MVP

**Goal**: Create books and members, enforce their validation and uniqueness
rules, and retrieve current book availability.

**Independent Test**: Run the one-to-one tests for AC-1 through AC-6 and AC-13
against an isolated database; each test must pass without loan-story setup
beyond its own fixtures.

### Implementation for User Story 1

- [ ] T013 [US1] Implement book creation validation and ISBN uniqueness handling for `Book.title`, `Book.author`, `Book.isbn`, and `Book.total_copies` as defined in `data-model.md` in `src/library_service/services.py`
- [ ] T014 [US1] Implement member creation validation and case-insensitive uniqueness handling for `Member.name` and `Member.email` as defined in `data-model.md` in `src/library_service/services.py`
- [ ] T015 [US1] Implement `POST /books`, `POST /members`, and `GET /books/{id}` with 201/404/409/422 responses and derived `available_copies` in `src/library_service/api.py`
- [ ] T016 [US1] Run the AC-1 through AC-6 and AC-13 tests without changing `tests/test_book_loan_api.py`, Ruff configuration, or Bandit configuration

**Checkpoint**: User Story 1 is independently functional and provides the MVP
catalog/member workflow.

---

## Phase 4: User Story 2 - Loan and Return Books (Priority: P1)

**Goal**: Create and return loans while enforcing inventory, member limits,
foreign references, due dates, and active-loan state transitions.

**Independent Test**: Run the one-to-one tests for AC-7 through AC-12 against
an isolated database and verify that each loan mutation preserves the
Book/Member/Loan invariants.

### Implementation for User Story 2

- [ ] T017 [US2] Implement transactional loan eligibility and creation using `Book.total_copies`, `Member.id`, `Loan.book_id`, `Loan.member_id`, `Loan.loaned_at`, and `Loan.due_date` constraints from `data-model.md` in `src/library_service/services.py`
- [ ] T018 [US2] Implement loan return state transition using `Loan.returned_at` from `data-model.md`, returning 404 for an unknown loan and 409 for an already-returned loan in `src/library_service/services.py`
- [ ] T019 [US2] Implement `POST /loans` and `POST /loans/{id}/return` with the contract statuses and JSON `detail` errors in `src/library_service/api.py`
- [ ] T020 [US2] Add transaction/concurrency safeguards so active loans cannot exceed `Book.total_copies` or three active loans per member in `src/library_service/database.py` and `src/library_service/services.py`
- [ ] T021 [US2] Run the AC-7 through AC-12 tests without changing `tests/test_book_loan_api.py`, Ruff configuration, or Bandit configuration

**Checkpoint**: User Stories 1 and 2 work together; catalog availability reflects
successful returns and rejected loan attempts.

---

## Phase 5: User Story 3 - Find Overdue Loans (Priority: P2)

**Goal**: Return only active loans whose due date is strictly before today's
UTC date.

**Independent Test**: Run the one-to-one AC-14 test with overdue, due-today,
future, and returned loans.

### Implementation for User Story 3

- [ ] T022 [US3] Implement UTC overdue selection using `Loan.due_date` and `Loan.returned_at` constraints from `data-model.md` in `src/library_service/services.py`
- [ ] T023 [US3] Implement `GET /loans/overdue` with an empty-list success response and the contract loan schema in `src/library_service/api.py`
- [ ] T024 [US3] Run the AC-14 test without changing `tests/test_book_loan_api.py`, Ruff configuration, or Bandit configuration

**Checkpoint**: All user stories are independently testable and the complete
AC-1 through AC-14 mapping is implemented.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate the complete feature without weakening requirements or
altering recorded evidence.

- [ ] T025 [P] Add concise runtime and API usage documentation referencing `specs/001-book-loan-service/quickstart.md` in `README.md`
- [ ] T026 [P] Review source for hardcoded secrets and ensure runtime settings remain environment-driven in `src/library_service/config.py`
- [ ] T027 Add a focused concurrency test proving simultaneous loan requests never exceed book inventory or the three-active-loan member limit in `tests/test_loan_concurrency.py`
- [ ] T028 Add a persistence test that creates records, rebuilds the application against the same SQLite file, and verifies records survive restart in `tests/test_persistence.py`
- [ ] T029 Run the full `.harness/run_harness.py` gate sequence and verify Ruff, Bandit, pytest, and at least 80% coverage pass; write only a new `evidence/harness-results/run-N/` directory
- [ ] T030 Verify every test remains mapped one-to-one to AC-1 through AC-14 and that no test, acceptance criterion, Ruff rule, Bandit rule, or recorded harness result was deleted, skipped, weakened, disabled, or edited in `tests/test_book_loan_api.py`, `pyproject.toml`, and `evidence/`
- [ ] T031 Run the scenarios in `specs/001-book-loan-service/quickstart.md` and record results only through the harness evidence workflow

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies; T001–T005 can begin immediately, with
  T004 depending only on the project paths created by T001–T003.
- **Phase 2 (Foundational)**: T006–T008 depend on T001–T004 and MUST precede
  implementation tasks T009–T012.
- **Phase 3 (US1)**: Depends on T009–T012; delivers the MVP.
- **Phase 4 (US2)**: Depends on T010–T012 and US1 API/model wiring; T017–T021
  build on the shared entities and application assembly.
- **Phase 5 (US3)**: Depends on T010–T012 and the Loan behavior from US2.
- **Phase 6 (Polish)**: Depends on all desired user stories and their tests.

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2; no dependency on another user story.
- **US2 (P1)**: Starts after Phase 2; uses the shared Book and Member entities
  and complements US1 availability behavior.
- **US3 (P2)**: Starts after Phase 2; requires Loan persistence and lifecycle
  behavior from US2.

### Within Each User Story

- Tests are created before implementation and must fail before implementation
  begins.
- Models and persistence precede services; services precede endpoints.
- A story's tests must pass without modifying tests or quality-gate settings.

## Parallel Opportunities

- T002, T003, and T005 can run in parallel after T001 establishes the manifest.
- T006 and T007 can run in parallel after the test paths exist; T008 follows
  both.
- T013 and T014 can be developed in parallel because they are separate service
  responsibilities; coordinate edits if they share `services.py`.
- T017 and T018 are separate responsibilities but share `services.py`; sequence
  or coordinate them before T019.
- T022 and documentation/security review T025–T026 can run in parallel after
  the required implementation is available.

## Parallel Example: User Story 1

```text
Task T013: Implement book creation service in src/library_service/services.py
Task T014: Implement member creation service in src/library_service/services.py
```

These are logically parallel responsibilities but touch the same file, so they
must be coordinated or sequenced unless the service module is split first.

## Implementation Strategy

### MVP First

1. Complete Phase 1, including the harness and immutable quality configuration.
2. Complete Phase 2, writing all AC-derived tests before implementation.
3. Complete Phase 3 and validate the catalog/member MVP with AC-1 through AC-6
   and AC-13.
4. Stop at the MVP checkpoint and run the harness without weakening any gate.

### Incremental Delivery

1. Add US2 loan and return behavior; validate AC-7 through AC-12.
2. Add US3 overdue lookup; validate AC-14.
3. Run all quality gates and quickstart scenarios.
4. Record only new harness evidence; preserve tests, configuration, and prior
   evidence.

## Notes

- Every task uses the required checkbox, sequential ID, optional `[P]` marker,
  story label where applicable, and an explicit file path.
- The acceptance suite is intentionally written before implementation.
- No task authorizes changing tests, acceptance criteria, Ruff settings, Bandit
  settings, or recorded harness results to obtain a passing result.
