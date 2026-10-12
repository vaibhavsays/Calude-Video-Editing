#!/usr/bin/env bash
# Prepares the video tools in fresh cloud sessions: npm deps for Remotion (broll/) and HyperFrames (hyperframes/),
# the HyperFrames render browser, and project copies of the source footage (kept out of git).
set -euo pipefail
[ "${CLAUDE_CODE_REMOTE:-}" = "true" ] || exit 0
cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/../..}"

(cd broll && npm install --no-audit --no-fund --silent)
(cd hyperframes && npm install --no-audit --no-fund --silent && npx --no-install hyperframes browser ensure >/dev/null)

cp -n raw/main.mp4 broll/public/main.mp4
cp -n raw/main.mp4 hyperframes/ai-seo-day1/main.mp4
