"""
Claude Code session management.

Handles persistent sessions for the TDD loop.
"""

import subprocess
import os
import json
from typing import Optional
from pathlib import Path

from .session import LLMSession


class ClaudeSession(LLMSession):
    """
    Manages a persistent Claude Code session.

    Uses claude CLI with --print for non-interactive mode
    and --continue for session persistence.
    """

    def __init__(self, session_id: Optional[str] = None, verbose: bool = False, **kwargs):
        self.session_id = session_id
        self.verbose = verbose
        self.model = os.environ.get('CLAUDE_MODEL', 'claude-opus-4-5-20251101')
        self.session_file = Path('.claude-session')
        self._load_session()

    def _load_session(self) -> None:
        """Load existing session ID if available."""
        if self.session_file.exists():
            self.session_id = self.session_file.read_text().strip()

    def _save_session(self) -> None:
        """Save session ID for persistence."""
        if self.session_id:
            self.session_file.write_text(self.session_id)

    def _get_auth_env(self) -> dict:
        """Get environment with auth credentials."""
        env = os.environ.copy()
        # Claude Code picks up these automatically
        return env

    def send(self, prompt: str, timeout: int = 10800) -> str:
        """
        Send a prompt to Claude and get response.

        Uses persistent session to maintain context between iterations.

        Args:
            prompt: The prompt to send
            timeout: Timeout in seconds (default 30 minutes)

        Returns:
            Claude's response text
        """
        cmd = ['claude', '--print', '--model', self.model]

        # Continue existing session if we have one
        if self.session_id:
            cmd.extend(['--continue'])

        # Allow all tools for code generation
        cmd.extend([
            '--dangerously-skip-permissions',  # Container is sandboxed anyway
            prompt
        ])

        if self.verbose:
            print(f"Sending prompt to Claude ({len(prompt)} chars)...")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=self._get_auth_env()
            )

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout or "Unknown error"
                raise RuntimeError(f"Claude command failed: {error_msg}")

            response = result.stdout

            # Extract session ID from response if this was first message
            # (Claude Code outputs session info in certain modes)
            if not self.session_id:
                self.session_id = "persistent"  # Mark as having a session
                self._save_session()

            return response

        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Claude timed out after {timeout} seconds")

    def send_with_files(self, prompt: str, files: list[str], timeout: int = 10800) -> str:
        """
        Send prompt with file context.

        Args:
            prompt: The prompt
            files: List of file paths to include as context
            timeout: Timeout in seconds

        Returns:
            Claude's response
        """
        # Build prompt with file contents
        file_context = []
        for file_path in files:
            path = Path(file_path)
            if path.exists():
                content = path.read_text()
                file_context.append(f"File: {file_path}\n```\n{content}\n```")

        full_prompt = "\n\n".join(file_context) + "\n\n" + prompt
        return self.send(full_prompt, timeout)

    def reset(self) -> None:
        """Reset session (start fresh)."""
        self.session_id = None
        if self.session_file.exists():
            self.session_file.unlink()


def run_claude_once(prompt: str, timeout: int = 300) -> str:
    """
    Run Claude once without session persistence.

    Useful for one-off tasks like code review.
    """
    cmd = [
        'claude', '--print',
        '--dangerously-skip-permissions',
        prompt
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout
    )

    if result.returncode != 0:
        raise RuntimeError(f"Claude command failed: {result.stderr}")

    return result.stdout
