#!/usr/bin/env bash
# Rebuilds installer/claude-exam-prep-code.zip from the LICENSE file and the
# current contents of src/ (Linux / macOS / WSL). Replaces the existing zip.
#
# Left out of the zip (personal data and build junk): __pycache__, *.pyc,
# .exam-app/, settings.local.json, fexam-/pexam-performance.json,
# fexam-scorereport.json, workspace.md, ccar-f_p2.html/.json
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
command -v python3 >/dev/null 2>&1 || { echo "ERROR: python3 was not found on your PATH." >&2; exit 1; }
[ -d "$REPO/src" ]   || { echo "ERROR: $REPO/src not found." >&2; exit 1; }
[ -f "$REPO/LICENSE" ] || { echo "ERROR: $REPO/LICENSE not found." >&2; exit 1; }

python3 -I -c '
import os, sys, zipfile
repo = sys.argv[1]
src = os.path.join(repo, "src")
out = os.path.join(repo, "installer", "claude-exam-prep-code.zip")
skip = {"__pycache__", ".exam-app", "settings.local.json", "fexam-performance.json",
        "pexam-performance.json", "fexam-scorereport.json", "workspace.md",
        "ccar-f_p2.html", "ccar-f_p2.json"}
entries = [(os.path.join(repo, "LICENSE"), "LICENSE")]
for dirpath, dirs, files in os.walk(src):
    dirs[:] = sorted(d for d in dirs if d not in skip)
    for f in sorted(files):
        if f in skip or f.endswith(".pyc"):
            continue
        full = os.path.join(dirpath, f)
        entries.append((full, os.path.relpath(full, src).replace(os.sep, "/")))
tmp = out + ".tmp"
with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
    for full, name in entries:
        z.write(full, name)
os.replace(tmp, out)
print("Wrote %s (%d files, %d bytes)" % (out, len(entries), os.path.getsize(out)))
' "$REPO"
