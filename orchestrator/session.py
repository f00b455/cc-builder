"""
LLM Session abstraction.

Provides ABC for different LLM backends (Claude Code, OpenCode)
and a factory function to create sessions.
"""

import shutil
import os
from abc import ABC, abstractmethod
from typing import Optional


class LLMSession(ABC):
    """Abstract base class for LLM CLI sessions."""

    @abstractmethod
    def send(self, prompt: str, timeout: int = 1800) -> str:
        """Send a prompt and get response."""
        ...

    @abstractmethod
    def send_with_files(self, prompt: str, files: list[str], timeout: int = 600) -> str:
        """Send prompt with file context."""
        ...

    @abstractmethod
    def reset(self) -> None:
        """Reset session (start fresh)."""
        ...


def _auto_detect_backend() -> str:
    """Auto-detect available backend via `which`."""
    if shutil.which('claude'):
        return 'claude'
    if shutil.which('opencode'):
        return 'opencode'
    raise RuntimeError(
        "No LLM backend found. Install 'claude' (Claude Code CLI) "
        "or 'opencode' (OpenCode CLI), or set CC_BACKEND explicitly."
    )


def create_session(backend: Optional[str] = None, verbose: bool = False, **kwargs) -> LLMSession:
    """
    Factory: create an LLMSession for the given backend.

    Args:
        backend: 'claude', 'opencode', or None for auto-detect.
                 Also reads CC_BACKEND env var.
        verbose: Enable verbose output.
        **kwargs: Backend-specific options.

    Returns:
        An LLMSession instance.
    """
    if backend is None:
        backend = os.environ.get('CC_BACKEND', '').lower() or None

    if backend is None:
        backend = _auto_detect_backend()

    if backend == 'claude':
        from .claude import ClaudeSession
        return ClaudeSession(verbose=verbose, **kwargs)
    elif backend == 'opencode':
        from .opencode import OpenCodeSession
        return OpenCodeSession(verbose=verbose, **kwargs)
    else:
        raise ValueError(f"Unknown backend: {backend!r}. Use 'claude' or 'opencode'.")
