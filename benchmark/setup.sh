#!/bin/bash
# E2E Benchmark: Claude Code vs OpenCode (Copilot) vs OpenCode (Claude Opus 4.5)

set -e
cd "$(dirname "$0")/.."

echo "=== Building Docker Images ==="

# Base images
docker build -f Dockerfile.base-common -t cc-builder:base-common .
docker build -f Dockerfile.base -t cc-builder:base .
docker build -f Dockerfile.base-opencode -t cc-builder:base-opencode .

# JVM images for all backends
docker build --build-arg BASE_IMAGE=cc-builder:base -f Dockerfile.jvm -t cc-jvm:claude .
docker build --build-arg BASE_IMAGE=cc-builder:base-opencode -f Dockerfile.jvm -t cc-jvm:opencode .

# Electron images
docker build --build-arg BASE_IMAGE=cc-builder:base -f Dockerfile.electron -t cc-electron:claude .
docker build --build-arg BASE_IMAGE=cc-builder:base-opencode -f Dockerfile.electron -t cc-electron:opencode .

# Create workspace directories with TASK.md
cd benchmark
rm -rf claude-code opencode opencode-claude
mkdir -p claude-code opencode opencode-claude
cp TASK.md claude-code/
cp TASK.md opencode/
cp TASK.md opencode-claude/

# Clear named volumes for clean runs
docker volume rm opencode-home opencode-home-claude 2>/dev/null || true

echo ""
echo "=== Ready ==="
echo "1) ./benchmark/run-claude.sh           # Claude Code (Opus 4.5)"
echo "2) ./benchmark/run-opencode.sh         # OpenCode + Copilot (GPT-5.1-Codex)"
echo "3) ./benchmark/run-opencode-claude.sh  # OpenCode + Claude (Opus 4.5)"
