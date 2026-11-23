<!--
Sync Impact Report
Version change: 1.0.0 -> 1.1.0 (quality gates and SDD safeguards added)
Modified principles:
- III. Verify Requirements with Tests (expanded with mandatory pass and coverage gates)
- IV. Make Failures Explicit (expanded with configuration and security rules)
- V. Keep Work Reviewable (expanded with agent safeguards)
Added sections: Additional Constraints and Development Workflow (expanded)
Removed sections: None
Follow-up TODO: Confirm the original ratification date.
-->
# Part-1A Constitution

## Core Principles

### I. Small, Purposeful Changes
Changes MUST directly address the requested need and stay within its scope. Contributors MUST follow established project patterns and avoid unnecessary complexity. This keeps changes understandable and reduces unintended effects.

### II. Preserve Intended Behavior
Changes MUST preserve existing behavior and interfaces unless changing them is part of the stated requirement. Any intentional behavior change MUST be clear to users and reflected in relevant documentation.

### III. Verify Requirements with Tests
All mandatory tests MUST pass. Measured test coverage MUST be at least 80%, as reported by the project's configured coverage tool. Behavior changes MUST have focused tests for the changed behavior and important edge cases. Contributors MUST run the smallest relevant available validation and report its result; if validation cannot be run, they MUST state why.

### IV. Make Failures Explicit
Code MUST handle invalid input and operational failures through clear, project-consistent errors. It MUST NOT silently hide failures or return success-shaped fallbacks. Secrets MUST NOT be hardcoded or committed to source control; runtime configuration MUST come from environment variables.

### V. Keep Work Reviewable
Changes MUST be readable and limited to directly related files. Directly affected documentation and dependent call sites MUST remain consistent. Unrelated existing work MUST be preserved. Agents MUST NOT weaken acceptance criteria, delete or skip failing tests, disable lint or SAST rules, or edit recorded harness results.

## Additional Constraints

Contributors MUST inspect the relevant code and existing conventions before choosing implementation details. Technology, dependencies, and project-specific policies MUST be based on repository evidence or explicit requirements, not assumptions. New dependencies MUST be added only when they are necessary to satisfy the requirement.

Ruff MUST report zero errors. Bandit MUST report zero medium- or high-severity findings. These quality gates MUST NOT be bypassed by disabling or weakening their rules.

## Development Workflow

Before changing code, identify the affected behavior and relevant existing tests. After changes, run targeted tests, checks, or builds appropriate to the change. Review the final diff for scope, unintended behavior changes, and consistency with this constitution; summarize the changes and validation performed.

Changes to feature specifications or acceptance criteria MUST be made through the relevant Spec-Driven Development (SDD) artifacts and documented there. Such changes MUST NOT be introduced only through implementation or test edits.

## Governance

This constitution governs project work. Amendments MUST be made in this document and reviewed for impact on existing guidance. Each amendment MUST update the version, last-amended date, and a temporary Sync Impact Report; the report MUST be removed before the amendment is committed.

Versioning follows semantic versioning: increment MAJOR for backward-incompatible governance changes, MINOR for new principles or materially expanded requirements, and PATCH for clarifications and non-semantic refinements. The ratification date records the original adoption date and MUST remain unchanged by later amendments. The last-amended date MUST be the date of the latest substantive amendment.

Contributors and reviewers MUST check relevant work against these principles during implementation and review. Any deviation MUST be necessary to satisfy a higher-priority requirement and its rationale MUST be documented in the change.

**Version**: 1.1.0 | **Ratified**: TODO(RATIFICATION_DATE): confirm original adoption date | **Last Amended**: 2026-11-23
