#!/usr/bin/env python3
"""Run every self-check. Exits non-zero if any fails.

  python run_tests.py
"""
import subprocess
import sys
from pathlib import Path

TESTS = sorted(Path(__file__).parent.joinpath("tests").glob("test_*.py"))


def main():
    failures, total = [], 0
    for path in TESTS:
        proc = subprocess.run([sys.executable, str(path)], capture_output=True, text=True)
        last = (proc.stdout.strip().splitlines() or ["no output"])[-1]
        if proc.returncode == 0:
            total += int(last.split()[0]) if last.split()[0].isdigit() else 0
            print(f"  ok    {path.name:<24} {last}")
        else:
            failures.append(path.name)
            print(f"  FAIL  {path.name}")
            print("        " + (proc.stdout.strip().splitlines() or [""])[-1])
            for line in proc.stderr.strip().splitlines()[-4:]:
                print(f"        {line}")

    print()
    if failures:
        print(f"{len(failures)} file(s) failed: {', '.join(failures)}")
        return 1
    print(f"{total} checks passed across {len(TESTS)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
