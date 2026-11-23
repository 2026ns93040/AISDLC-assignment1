"""Deterministic harness: lint -> SAST -> tests. Runs ALL gates, records evidence."""
import pathlib
import subprocess
import sys
from datetime import datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
RESULTS = ROOT / "evidence" / "harness-results"

GATES = [
    ("lint", [sys.executable, "-m", "ruff", "check", "src", "tests"]),
    ("security", [sys.executable, "-m", "bandit", "-r", "src", "-ll"]),
    ("tests", [sys.executable, "-m", "pytest", "tests", "--cov=src",
               "--cov-fail-under=80", "-v"]),
]


def next_run_dir() -> pathlib.Path:
    RESULTS.mkdir(parents=True, exist_ok=True)
    nums = [int(p.name.split("-")[1]) for p in RESULTS.glob("run-*")
            if p.name.split("-")[1].isdigit()]
    run_dir = RESULTS / f"run-{max(nums, default=0) + 1}"
    run_dir.mkdir()
    return run_dir


def main() -> int:
    run_dir = next_run_dir()
    rows = []
    for name, cmd in GATES:
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        (run_dir / f"{name}.stdout.txt").write_text(proc.stdout, encoding="utf-8")
        (run_dir / f"{name}.stderr.txt").write_text(proc.stderr, encoding="utf-8")
        (run_dir / f"{name}.exitcode.txt").write_text(str(proc.returncode))
        rows.append((name, "PASS" if proc.returncode == 0 else "FAIL"))

    lines = [f"Harness run: {run_dir.name}  ({datetime.now().isoformat(timespec='seconds')})",
             "-" * 34]
    lines += [f"{n:<12}{r}" for n, r in rows]
    overall = "PASS" if all(r == "PASS" for _, r in rows) else "FAIL"
    lines += ["-" * 34, f"{'OVERALL':<12}{overall}"]
    summary = "\n".join(lines)
    (run_dir / "summary.txt").write_text(summary, encoding="utf-8")
    print(summary)
    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())