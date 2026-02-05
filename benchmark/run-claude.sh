#!/bin/bash
cd "$(dirname "$0")/.."
source benchmark/.env 2>/dev/null

mkdir -p benchmark/claude-code

cat benchmark/TASK.md | docker run -i \
    -e CLAUDE_CODE_OAUTH_TOKEN="$CLAUDE_CODE_OAUTH_TOKEN" \
    -v "$(pwd)/benchmark/claude-code:/workspace" \
    cc-jvm:claude
