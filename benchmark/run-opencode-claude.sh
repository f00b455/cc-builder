#!/bin/bash
# Benchmark: OpenCode with Claude Opus 4.5 (Max subscription via OAuth)
cd "$(dirname "$0")/.."
source benchmark/.env 2>/dev/null

mkdir -p benchmark/opencode-claude

# OpenCode auth.json contains OAuth tokens for anthropic provider
OPENCODE_AUTH="$HOME/.local/share/opencode/auth.json"
if [ ! -f "$OPENCODE_AUTH" ]; then
    echo "ERROR: No OpenCode auth found at $OPENCODE_AUTH"
    echo "Run 'opencode auth' locally first to set up Anthropic OAuth."
    exit 1
fi

cat benchmark/TASK.md | docker run -i \
    -e OPENCODE_MODEL="anthropic/claude-opus-4-5-20251101" \
    -v "$OPENCODE_AUTH:/tmp/opencode-auth.json:ro" \
    -v "$(pwd)/benchmark/opencode-claude:/workspace" \
    -v opencode-home-claude:/home/builder \
    cc-jvm:opencode
