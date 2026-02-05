#!/bin/bash
cd "$(dirname "$0")"

echo "=== Benchmark Results ==="
echo ""

for tool in claude-code opencode; do
    echo "--- $tool ---"
    find "$tool/src" -name "*.java" 2>/dev/null | head -20
    echo ""
done
