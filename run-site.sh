#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SITE_DIR="$ROOT_DIR/site"

MODE="${1:-dev}"

if [[ ! -d "$SITE_DIR" ]]; then
  echo "Site directory not found: $SITE_DIR" >&2
  exit 1
fi

cd "$SITE_DIR"

if [[ ! -d node_modules ]]; then
  echo "Installing site dependencies..."
  npm install
fi

case "$MODE" in
  dev)
    exec npm run dev
    ;;
  build)
    exec npm run build
    ;;
  preview)
    exec npm run preview
    ;;
  check)
    exec npm run lint
    ;;
  test)
    exec npm run test
    ;;
  *)
    cat >&2 <<'EOF'
Usage: ./run-site.sh [dev|build|preview|check|test]

  dev      Start the Astro dev server
  build    Build the production site
  preview  Preview the built site
  check    Run lint + content validation
  test     Run tests
EOF
    exit 1
    ;;
esac
