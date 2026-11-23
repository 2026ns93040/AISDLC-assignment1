# Feature Specification: Library Book-Loan Service

**Feature Branch**: `Not created (no branch hook configured)`

**Created**: 2026-11-23

**Status**: Draft

**Input**: User description: Build a Library Book-Loan Service exposed as a JSON HTTP API, with book and member records, borrowing and return workflows, inventory limits, overdue-loan lookup, and the supplied acceptance criteria.

## Clarifications

### Session 2026-11-23

- Q: Where should authentication and authorization for the book-loan API be enforced? → A: Leave the API unauthenticated for the initial version.
- Q: Must books, members, and loans survive a service restart? → A: Records must persist across service restarts.
- Q: What should `POST /loans/{id}/return` return when the loan ID does not exist? → A: Return 404 with JSON containing `detail`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Manage the catalog and members (Priority: P1)

A library operator creates book and member records and checks a book's current availability.

**Why this priority**: Books and members are required before loans can be recorded.

**Independent Test**: Create books and members through the API, verify successful and rejected requests, and retrieve a book with its available-copy count.

**Acceptance Scenarios**:

1. **Given** valid book details with a 13-digit ISBN and at least one copy, **When** the operator sends `POST /books`, **Then** the service returns 201 and the created book (AC-1).
2. **Given** a book request with a missing title or ISBN that is not 13 digits, **When** the operator sends `POST /books`, **Then** the service returns 422 (AC-2).
3. **Given** a book already uses the requested ISBN, **When** the operator sends `POST /books`, **Then** the service returns 409 (AC-3).
4. **Given** valid member name and email details, **When** the operator sends `POST /members`, **Then** the service returns 201 (AC-4).
5. **Given** an invalid email format or an email already in use, **When** the operator sends `POST /members`, **Then** the service returns 422 for invalid format or 409 for the duplicate (AC-5, AC-6).
6. **Given** an existing book or an unknown book ID, **When** the operator requests `GET /books/{id}`, **Then** the service returns the book with current `available_copies` or returns 404 for the unknown ID (AC-13).

---

### User Story 2 - Loan and return books (Priority: P1)

A library operator records a loan when the requested book is available and the member is within the active-loan limit, then records the book's return.

**Why this priority**: Lending and returns are the core service behavior and maintain the inventory and member limits.

**Independent Test**: Create a book and member, exercise successful and rejected loans at inventory and member limits, and return a loan once and twice.

**Acceptance Scenarios**:

1. **Given** an existing book with an available copy and an existing member with fewer than three active loans, **When** the operator sends `POST /loans`, **Then** the service returns 201 and `due_date` is the loan date plus 14 days (AC-7).
2. **Given** a book has no available copies, **When** the operator requests a loan for it, **Then** the service returns 409 (AC-8).
3. **Given** a member already has three active loans, **When** the operator requests another loan, **Then** the service returns 409 (AC-9).
4. **Given** either referenced book or member does not exist, **When** the operator requests a loan, **Then** the service returns 404 (AC-10).
5. **Given** a loan is active, **When** the operator sends `POST /loans/{id}/return`, **Then** the service returns 200 and sets `returned_at` (AC-11).
6. **Given** a loan has already been returned, **When** the operator sends `POST /loans/{id}/return` again, **Then** the service returns 409 (AC-12).

---

### User Story 3 - Find overdue loans (Priority: P2)

A library operator retrieves loans that are still active and past their due date.

**Why this priority**: This supports follow-up on late books after the catalog and loan lifecycle are available.

**Independent Test**: Prepare active loans with due dates before today, due today, and after today, plus a returned overdue loan; verify only qualifying active loans are returned.

**Acceptance Scenarios**:

1. **Given** loans with different due dates and return states, **When** the operator requests `GET /loans/overdue`, **Then** the response contains only active loans whose `due_date` is before today (AC-14).

### Edge Cases

- A loan due today is not overdue; the overdue comparison is strictly before today's date.
- A returned loan is not active and is excluded from both active-loan limits and overdue results.
- A return request for an unknown loan ID returns 404 with a JSON `detail` field; a return request for an already-returned loan returns 409.
- Simultaneous loan requests for the last available copy must not cause the number of active loans for a book to exceed `total_copies`.
- Simultaneous loan requests for one member must not allow that member to exceed three active loans.
- ISBN validation checks for exactly 13 digits; checksum validation is not part of the stated requirement.
- Error responses, including errors for unknown IDs, use JSON and include a `detail` field.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The service MUST create a book through `POST /books` with `title`, `author`, `isbn`, and `total_copies`; a valid request MUST return 201 and the created book.
- **FR-002**: The service MUST reject a book request with a missing title, an ISBN other than 13 digits, or `total_copies` less than 1 with status 422.
- **FR-003**: The service MUST reject a book whose ISBN duplicates an existing book with status 409.
- **FR-004**: The service MUST create a member through `POST /members` with a valid `name` and `email`, returning 201; it MUST reject an invalid email format with 422 and a duplicate email with 409.
- **FR-005**: The service MUST return an existing book through `GET /books/{id}` with `available_copies` equal to `total_copies` minus its active loans, and MUST return 404 for an unknown book ID.
- **FR-006**: The service MUST create a loan through `POST /loans` only when the book and member exist, the book has at least one available copy, and the member has fewer than three active loans.
- **FR-007**: A successful loan MUST return 201, set `loaned_at`, and set `due_date` to 14 days after the loan date.
- **FR-008**: A loan request with a non-existent book or member MUST return 404. A request for an unavailable book or a member already holding three active loans MUST return 409.
- **FR-009**: An active loan MUST be one whose `returned_at` is unset. Returning an active loan through `POST /loans/{id}/return` MUST return 200 and set `returned_at`; an unknown loan ID MUST return 404 with JSON containing `detail`; returning an already-returned loan MUST return 409.
- **FR-010**: The service MUST return `GET /loans/overdue` results containing only active loans whose due date is strictly before today.
- **FR-011**: All error responses MUST be JSON objects containing a `detail` field.
- **FR-012**: The service MUST NOT contain hardcoded secrets. Runtime configuration MUST be supplied through environment variables.
- **FR-013**: Concurrent loan requests MUST preserve both inventory availability and the maximum of three active loans per member.

### Non-Functional Requirements

- **NFR-001**: All mandatory tests MUST pass, and measured test coverage MUST be at least 80%.
- **NFR-002**: Ruff MUST report zero errors.
- **NFR-003**: Bandit MUST report zero medium- or high-severity findings.
- **NFR-004**: The implementation MUST satisfy project safeguards: acceptance criteria MUST NOT be weakened; failing tests MUST NOT be deleted or skipped; lint or SAST rules MUST NOT be disabled; recorded harness results MUST NOT be edited.
- **NFR-005**: Any changes to this feature's specification or acceptance criteria MUST be made through and documented in the relevant Spec-Driven Development artifacts.
- **NFR-006**: The initial version MUST expose the API without authentication or authorization requirements; adding access control is outside this feature's scope.
- **NFR-007**: Books, members, and loans MUST persist across service restarts.

### Key Entities

- **Book**: A catalog item with `id`, `title`, `author`, a 13-digit `isbn`, and positive `total_copies`. Its current availability is derived as `total_copies` minus active loans.
- **Member**: A borrower with `id`, `name`, and `email`.
- **Loan**: A borrowing record with `id`, `book_id`, `member_id`, `loaned_at`, `due_date`, and nullable `returned_at`. A loan is active while `returned_at` is unset.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 14 supplied acceptance criteria pass as independently verifiable pass/fail scenarios.
- **SC-002**: 100% of API error responses contain a JSON `detail` field.
- **SC-003**: Under concurrent loan requests, active loans never exceed a book's total copies or a member's limit of three.
- **SC-004**: Every successful loan has a due date exactly 14 days after its loan date, and overdue results exclude loans due today or later and all returned loans.

## Assumptions

- The service generates unique IDs; their representation is not part of the requested contract.
- `loaned_at` is a UTC timestamp. `due_date` is a UTC calendar date exactly 14 days after the UTC calendar date of `loaned_at`; “today” for overdue checks is the current UTC calendar date.
- ISBN validation requires exactly 13 digits and does not additionally validate an ISBN checksum.
- Email format uses conventional syntax validation, and email uniqueness is case-insensitive.
- The initial deployment is trusted and does not require caller authentication or authorization; access control is outside this feature's scope.
- Book, member, and loan records are durable library records and must not be lost when the service restarts.
- The initial scope includes only the routes and operations listed in the request; reservations, renewals, fines, notifications, and deletion are excluded.
