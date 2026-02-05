#!/bin/bash
cd "$(dirname "$0")/.."
source benchmark/.env 2>/dev/null

mkdir -p benchmark/opencode

# Use gh auth token for Copilot provider access
GITHUB_TOKEN="${GITHUB_TOKEN:-$(gh auth token 2>/dev/null)}"
if [ -z "$GITHUB_TOKEN" ]; then
    echo "ERROR: No GITHUB_TOKEN and 'gh auth token' failed. Run 'gh auth login' first."
    exit 1
fi

cat benchmark/TASK.md | docker run -i \
    -e GITHUB_TOKEN="$GITHUB_TOKEN" \
    -v "$(pwd)/benchmark/opencode:/workspace" \
    -v opencode-home:/home/builder \
    cc-jvm:opencode
