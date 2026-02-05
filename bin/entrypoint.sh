#!/bin/bash
# Entrypoint script for cc-builder
# Fixes permissions on mounted volumes and runs cc-tdd as builder user

set -e

# Fix ownership of workspace (runs as root initially)
if [ -d /workspace ]; then
    chown -R builder:builder /workspace 2>/dev/null || true
fi

# Backend-conditional auth setup
BACKEND="${CC_BACKEND:-}"

if [ "$BACKEND" = "claude" ] || [ -z "$BACKEND" ]; then
    # Claude: copy read-only .claude.json to writable home (mounted at /tmp/.claude-auth)
    if [ -f /tmp/.claude-auth/.claude.json ]; then
        cp /tmp/.claude-auth/.claude.json /home/builder/.claude.json
        chown builder:builder /home/builder/.claude.json
    fi
fi

# OpenCode: copy OAuth auth.json if mounted
if [ -f /tmp/opencode-auth.json ]; then
    mkdir -p /home/builder/.local/share/opencode
    cp /tmp/opencode-auth.json /home/builder/.local/share/opencode/auth.json
    chown -R builder:builder /home/builder/.local/share/opencode
fi

# Switch to builder user and run cc-tdd
exec gosu builder cc-tdd "$@"
