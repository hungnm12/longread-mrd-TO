#!/usr/bin/env bash
# Run every check in the repository: Python unit + integration tests, then the site's
# type check, content validation and unit tests.
#
# All Python tests run against synthetic fixtures. None touches a real BAM: the real
# inputs are 80-300 GB, read-only, and owned by other users.
#
# Usage: ./scripts/run-tests.sh [python|site|all]
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"   # scripts/ -> repo root
ANALYSIS_DIR="$ROOT_DIR"
SITE_DIR="$ROOT_DIR/site"
TARGET="${1:-all}"

# Keep matplotlib's cache out of the repository and out of $HOME races.
export MPLCONFIGDIR="${MPLCONFIGDIR:-/tmp/mplconfig}"
mkdir -p "$MPLCONFIGDIR"

FAILED=0

run_python() {
  echo "── Python: unit tests ───────────────────────────────────────────────"
  ( cd "$ANALYSIS_DIR" && python3 -m unittest discover -s tests/unit -p 'test_*.py' ) || FAILED=1

  echo
  echo "── Python: integration tests ────────────────────────────────────────"
  ( cd "$ANALYSIS_DIR" && python3 -m unittest discover -s tests/integration -p 'test_*.py' ) || FAILED=1
}

run_site() {
  if [[ ! -d "$SITE_DIR/node_modules" ]]; then
    echo "── Site: installing dependencies ──────────────────────────────────"
    ( cd "$SITE_DIR" && npm install )
  fi

  echo
  echo "── Site: type check + content validation ────────────────────────────"
  ( cd "$SITE_DIR" && npm run lint ) || FAILED=1

  echo
  echo "── Site: unit tests ─────────────────────────────────────────────────"
  ( cd "$SITE_DIR" && npm run test ) || FAILED=1
}

case "$TARGET" in
  python) run_python ;;
  site)   run_site ;;
  all)    run_python; echo; run_site ;;
  *)
    echo "Usage: ./scripts/run-tests.sh [python|site|all]" >&2
    exit 2
    ;;
esac

echo
if [[ "$FAILED" -eq 0 ]]; then
  echo "All checks passed."
else
  echo "One or more checks FAILED." >&2
fi
exit "$FAILED"
