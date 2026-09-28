#!/usr/bin/env python3
"""Run the reference tests and record the verbatim result in docs/test_run.txt (embedded in README §52)."""
import platform
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
r = subprocess.run([sys.executable, "-m", "pytest", "reference", "-v", "-p", "no:cacheprovider", "--no-header"],
                   cwd=ROOT, capture_output=True, text=True)
lines = [l.split(" PASSED")[0].ljust(92) + " PASSED" if " PASSED" in l else l
         for l in r.stdout.splitlines() if "::" in l or l.startswith("=")]
lines = [l for l in lines if "test session starts" not in l]
out = f"$ python -m pytest reference -v      # recorded {date.today()} · Python {platform.python_version()}\n" + "\n".join(lines) + "\n"
(ROOT / "docs").mkdir(exist_ok=True)
(ROOT / "docs" / "test_run.txt").write_text(out, encoding="utf-8")
print(out.splitlines()[-1])
sys.exit(r.returncode)
