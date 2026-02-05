"""
OpenCode CLI session management.

Uses `opencode run` for non-interactive LLM access.
Supports configurable model/provider via OPENCODE_MODEL env var.
"""

import glob
import json
import subprocess
import os
from typing import Optional
from pathlib import Path

from .session import LLMSession

OPENCODE_STORAGE = Path.home() / '.local' / 'share' / 'opencode' / 'storage' / 'session'


class OpenCodeSession(LLMSession):
    """
    Manages an OpenCode CLI session.

    Creates a persistent session on init, then reuses it for all calls
    via -c/-s flags. A completion loop re-invokes opencode when it only
    plans but doesn't finish.
    """

    MAX_CONTINUATIONS = 5

    def __init__(self, session_id: Optional[str] = None, verbose: bool = False, **kwargs):
        self.verbose = verbose
        self.session_id: Optional[str] = None
        self.model = os.environ.get('OPENCODE_MODEL', 'github-copilot/gpt-5.1-codex')
        self.max_continuations = int(os.environ.get('OPENCODE_MAX_CONTINUATIONS', self.MAX_CONTINUATIONS))
        self._init_session()

    def _init_session(self) -> None:
        """Create a session with a simple init prompt so we can reuse it."""
        print("  [opencode] initializing session...")
        self._run_opencode("List the files in the current directory. Just ls, nothing else.", timeout=120)
        if self.session_id:
            print(f"  [opencode] session ready: {self.session_id}")
        else:
            print("  [opencode] WARNING: could not capture session ID, will run stateless")

    def _find_latest_session_id(self) -> Optional[str]:
        """Find the most recently modified session ID from OpenCode's storage."""
        pattern = str(OPENCODE_STORAGE / '**' / 'ses_*.json')
        files = glob.glob(pattern, recursive=True)
        if not files:
            return None
        latest = max(files, key=os.path.getmtime)
        try:
            data = json.loads(Path(latest).read_text())
            return data.get('id')
        except (json.JSONDecodeError, OSError):
            return None

    def _is_complete(self, response: str) -> bool:
        """Check if OpenCode finished implementing or is suggesting next steps."""
        incomplete_signals = ['next steps', 'would you like me to', 'shall i']
        lower = response.lower()
        return not any(signal in lower for signal in incomplete_signals)

    def _run_opencode(self, prompt: str, timeout: int = 10800) -> str:
        """Execute a single opencode run invocation."""
        cmd = ['opencode']

        if self.session_id:
            cmd.extend(['-c', '-s', self.session_id])

        cmd.extend(['-m', self.model, '--print-logs', '--log-level', 'DEBUG', 'run', prompt])

        label = f"opencode -c -s {self.session_id}" if self.session_id else f"opencode -m {self.model}"
        print(f"  [opencode] {label} run ... ({len(prompt)} chars)")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=os.environ.copy()
            )

            print(f"  [opencode] exit={result.returncode} stdout={len(result.stdout)} chars, stderr={len(result.stderr)} chars")
            if result.stdout:
                preview = result.stdout[:500].replace('\n', '\n  [opencode]   ')
                print(f"  [opencode]   {preview}")
            if result.stderr:
                # Only show last 500 chars of stderr to avoid flooding with DEBUG logs
                stderr_preview = result.stderr[-500:] if len(result.stderr) > 500 else result.stderr
                print(f"  [opencode] stderr (tail): {stderr_preview}")

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout or "Unknown error"
                raise RuntimeError(f"OpenCode command failed: {error_msg}")

            # Capture session ID after first successful run
            if not self.session_id:
                self.session_id = self._find_latest_session_id()
                if self.session_id:
                    print(f"  [opencode] session: {self.session_id}")

            return result.stdout

        except subprocess.TimeoutExpired:
            raise RuntimeError(f"OpenCode timed out after {timeout} seconds")

    def send(self, prompt: str, timeout: int = 10800) -> str:
        """
        Send a prompt to OpenCode and get response.

        Runs a completion loop: if OpenCode only plans and suggests
        next steps, automatically continues with "implement next steps"
        until the work is done or max_continuations is reached.
        """
        response = self._run_opencode(prompt, timeout)

        for i in range(self.max_continuations):
            if self._is_complete(response):
                print(f"  [opencode] complete after {i} continuations")
                break
            print(f"  [opencode] not complete, continuation {i + 1}/{self.max_continuations}...")
            continuation = self._run_opencode("implement next steps", timeout)
            response += "\n" + continuation

        return response

    def send_with_files(self, prompt: str, files: list[str], timeout: int = 10800) -> str:
        """Send prompt with file context."""
        file_context = []
        for file_path in files:
            path = Path(file_path)
            if path.exists():
                content = path.read_text()
                file_context.append(f"File: {file_path}\n```\n{content}\n```")

        full_prompt = "\n\n".join(file_context) + "\n\n" + prompt
        return self.send(full_prompt, timeout)

    def reset(self) -> None:
        """Reset session and create a fresh one."""
        self.session_id = None
        self._init_session()
