"""
Base class for language-specific BDD runners.
"""

import subprocess
from abc import ABC, abstractmethod
from typing import Tuple
from pathlib import Path


class BaseRunner(ABC):
    """
    Abstract base class for BDD test runners.

    Each language implementation must provide:
    - run_bdd(): Run BDD tests and return (success, output)
    - measure_coverage(): Run tests with coverage and return percentage
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Language name."""
        pass

    @property
    @abstractmethod
    def bdd_framework(self) -> str:
        """BDD framework name (e.g., godog, behave, cucumber)."""
        pass

    @abstractmethod
    def run_bdd(self) -> Tuple[bool, str]:
        """
        Run BDD tests.

        Returns:
            Tuple of (all_passed: bool, output: str)
        """
        pass

    @abstractmethod
    def run_e2e(self) -> Tuple[bool, str]:
        """
        Run E2E tests.

        Returns:
            Tuple of (all_passed: bool, output: str)
        """
        pass

    @abstractmethod
    def measure_coverage(self) -> float:
        """
        Run tests and measure code coverage.

        Returns:
            Coverage percentage (0-100)
        """
        pass

    def run_command(self, cmd: list[str], timeout: int = 300) -> subprocess.CompletedProcess:
        """
        Run a shell command.

        Args:
            cmd: Command and arguments
            timeout: Timeout in seconds

        Returns:
            CompletedProcess with stdout, stderr, returncode
        """
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )

    def features_exist(self) -> bool:
        """Check if feature files exist."""
        features_dir = Path('features')
        if not features_dir.exists():
            return False
        return bool(list(features_dir.glob('*.feature')))

    def get_feature_files(self) -> list[Path]:
        """Get all feature files."""
        return list(Path('features').glob('*.feature'))

    def init_project(self) -> None:
        """Initialize project from templates if available. Override in subclasses."""
        pass

    def build(self) -> Tuple[bool, str]:
        """
        Build the project (compile, package, etc.).

        Returns:
            Tuple of (success: bool, output: str)

        Override in subclasses for language-specific build.
        """
        return True, "No build step defined for this language"
