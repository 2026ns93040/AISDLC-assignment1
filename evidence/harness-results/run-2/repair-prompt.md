The deterministic harness failed. Evidence is in evidence/harness-results/run-2/ (see failure-evidence.md). Repair the IMPLEMENTATION in src/ so the failing checks pass.

Strict rules:
- Edit only files in src/ (and requirements.txt if a dependency is genuinely needed).
- Do NOT modify, skip, xfail or delete any test in tests/.
- Do NOT modify .harness/, pytest.ini, any Ruff/Bandit configuration, or anything in specs/ or .specify/.
- Do NOT add noqa, nosec or type-ignore comments to hide findings, and do not lower the coverage threshold.
- The acceptance criteria in specs/<feature>/spec.md are the source of truth.
- Do not run the harness. I will rerun it myself.
Explain each change briefly.