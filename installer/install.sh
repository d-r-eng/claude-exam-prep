#!/usr/bin/env bash
# Claude Exam Prep installer (Linux / macOS / WSL)
# Extracts claude-exam-prep-code.zip (next to this script) into a new directory
# in the current working directory, runs the tests, then starts the app.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ZIP="$SCRIPT_DIR/claude-exam-prep-code.zip"
DEFAULT_NAME="claude-exam-prep"

die() { echo "ERROR: $*" >&2; exit 1; }

# --- prerequisites (checked before anything is created) ---------------------
missing=0
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 was not found on your PATH."
  echo "  Debian/Ubuntu/WSL: sudo apt install python3"
  echo "  macOS:             brew install python3"
  missing=1
fi
if ! command -v claude >/dev/null 2>&1; then
  echo "Claude Code ('claude') was not found on your PATH."
  echo "  Install it from https://claude.ai/code, then run 'claude' once to sign in."
  missing=1
fi
[ "$missing" -eq 0 ] || die "Install the missing prerequisites above and run this installer again."
[ -f "$ZIP" ] || die "Cannot find $ZIP (it must sit next to install.sh)."

# --- ask for directory name -------------------------------------------------
read -r -p "New directory name [$DEFAULT_NAME]: " NAME
NAME="${NAME:-$DEFAULT_NAME}"
case "$NAME" in
  */*|*\\*|.|..) die "Enter a plain folder name (no slashes); it is created in $(pwd)." ;;
esac
TARGET="$(pwd)/$NAME"
[ ! -e "$TARGET" ] || die "$TARGET already exists. Nothing was changed."

# --- create and extract -----------------------------------------------------
echo "Creating $TARGET ..."
mkdir "$TARGET"
if ! python3 -I -c '
import sys, zipfile
zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])
' "$ZIP" "$TARGET"; then
  rm -rf "$TARGET"
  die "Extraction failed; removed $TARGET."
fi

# --- verify -----------------------------------------------------------------
echo "Running tests ..."
if ! (cd "$TARGET" && python3 -m unittest discover -s app -p "test_*.py"); then
  die "Tests failed. Files are in $TARGET but the app was not started."
fi

echo
echo "Installed to: $TARGET"
echo "Next time:    cd \"$TARGET\" && python3 app/serve.py --open"
echo "Or in Claude Code:  cd \"$TARGET\" && claude   (then /fexam medium)"
echo
echo "Starting the app at http://localhost:8765/practice (Ctrl+C to stop) ..."
cd "$TARGET"
exec python3 app/serve.py --open
