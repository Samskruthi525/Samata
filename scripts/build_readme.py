#!/usr/bin/env python3
"""Concatenate readme_src/*.md (sorted) into README.md and report line count."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parts = sorted((ROOT / "readme_src").glob("*.md"))
text = "\n".join(p.read_text(encoding="utf-8").rstrip() + "\n" for p in parts)

# inject data-driven tables
import re as _re
import sys as _sys
_sys.path.insert(0, str(ROOT / "scripts"))
from readme_tables import TABLES  # noqa: E402
text = _re.sub(r"<!-- GEN:(\w+) -->", lambda m: TABLES[m.group(1)]() if m.group(1) in TABLES else m.group(0), text)
(ROOT / "README.md").write_text(text, encoding="utf-8")
print(f"README.md written ({text.count(chr(10))} lines from {len(parts)} parts)")

# Sanity check: every relative link / image target exists (outside code blocks)
import re
prose = re.sub(r"```.*?```", "", text, flags=re.S)
targets = re.findall(r'(?:src="|\]\()([^")\s]+)', prose)
missing = sorted({t.split("#")[0] for t in targets
                  if not t.startswith(("http://", "https://", "mailto:", "#")) and not (ROOT / t.split("#")[0]).exists()})
if missing:
    raise SystemExit(f"MISSING FILES: {missing}")
print(f"All {len(set(targets))} image/file references resolve.")

# Anchor check using GitHub slug rules
def slug(h):
    h = re.sub(r"<[^>]+>", "", h).strip().lower()
    h = re.sub(r"[^\w\- ]", "", h)
    return h.replace(" ", "-")

in_code = False
anchors = {}
for line in text.splitlines():
    if line.startswith("```"):
        in_code = not in_code
        continue
    if not in_code:
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            s = slug(m.group(2))
            n = anchors.get(s, -1) + 1
            anchors[s] = n
            if n:
                anchors[f"{s}-{n}"] = 0
links = set(re.findall(r"\]\(#([^)]+)\)", text))
broken = sorted(l for l in links if l not in anchors)
if broken:
    raise SystemExit(f"BROKEN ANCHORS: {broken}")
else:
    print(f"All {len(links)} internal anchors resolve.")
