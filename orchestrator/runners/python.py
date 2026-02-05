"""
Python BDD runner using behave.
"""

import re
from typing import Tuple
from pathlib import Path

from .base import BaseRunner


class PythonRunner(BaseRunner):
    """
    Python language runner.

    Uses:
    - behave for BDD tests
    - coverage.py for coverage measurement
    """

    @property
    def name(self) -> str:
        return "python"

    @property
    def bdd_framework(self) -> str:
        return "behave"

    def run_bdd(self) -> Tuple[bool, str]:
        """
        Run behave BDD tests.

        Returns:
            Tuple of (all_passed, output)
        """
        if not self.features_exist():
            return False, "No feature files found in features/"

        # Run behave
        result = self.run_command(['behave', 'features/', '--no-capture'])

        output = result.stdout + result.stderr
        success = result.returncode == 0

        # Check for undefined steps
        if 'undefined' in output.lower() or 'not implemented' in output.lower():
            success = False

        return success, output

    def run_e2e(self) -> Tuple[bool, str]:
        """No E2E tests for Python runner."""
        return True, ""

    def measure_coverage(self) -> float:
        """
        Measure test coverage using coverage.py with behave.

        Returns:
            Coverage percentage
        """
        # Run behave with coverage
        result = self.run_command([
            'coverage', 'run', '--source=.',
            '-m', 'behave', 'features/'
        ])

        if result.returncode != 0:
            # Try pytest as fallback (for unit tests)
            result = self.run_command([
                'coverage', 'run', '--source=.',
                '-m', 'pytest'
            ])

        # Get coverage report
        result = self.run_command(['coverage', 'report'])

        if result.returncode != 0:
            return 0.0

        # Parse total coverage
        # Format: "TOTAL                     123     12    90%"
        output = result.stdout
        match = re.search(r'TOTAL\s+\d+\s+\d+\s+(\d+)%', output)

        if match:
            return float(match.group(1))

        # Alternative: look for last percentage
        percentages = re.findall(r'(\d+)%', output)
        if percentages:
            return float(percentages[-1])

        return 0.0

    def setup_steps_dir(self) -> None:
        """Create steps directory structure for behave."""
        steps_dir = Path('features/steps')
        steps_dir.mkdir(parents=True, exist_ok=True)

        # Create __init__.py if needed
        init_file = steps_dir / '__init__.py'
        if not init_file.exists():
            init_file.touch()

    def create_environment(self) -> None:
        """Create behave environment.py if needed."""
        env_file = Path('features/environment.py')
        if not env_file.exists():
            env_file.write_text('''"""Behave environment configuration."""

def before_all(context):
    """Setup before all tests."""
    pass

def after_all(context):
    """Cleanup after all tests."""
    pass
''')
