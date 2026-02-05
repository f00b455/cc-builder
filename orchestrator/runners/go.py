"""
Go BDD runner using godog.
"""

import re
from typing import Tuple
from pathlib import Path

from .base import BaseRunner


class GoRunner(BaseRunner):
    """
    Go language runner.

    Uses:
    - godog for BDD tests
    - go test -cover for coverage
    """

    @property
    def name(self) -> str:
        return "go"

    @property
    def bdd_framework(self) -> str:
        return "godog"

    def run_bdd(self) -> Tuple[bool, str]:
        """
        Run godog BDD tests via go test.

        Returns:
            Tuple of (all_passed, output)
        """
        if not self.features_exist():
            return False, "No feature files found in features/"

        # Clean test cache to avoid stale object errors
        self.run_command(['go', 'clean', '-testcache'])

        # Run BDD tests via go test (NOT godog CLI!)
        # godog CLI doesn't find Go step definitions - must use go test
        steps_dir = Path('features/steps')
        if steps_dir.exists():
            result = self.run_command(['go', 'test', '-v', './features/steps/...'])
        else:
            # Fallback: run all tests
            result = self.run_command(['go', 'test', '-v', './...'])

        output = result.stdout + result.stderr
        success = result.returncode == 0

        # Parse output for scenario results
        if 'undefined' in output.lower():
            success = False

        return success, output

    def run_e2e(self) -> Tuple[bool, str]:
        """No E2E tests for Go runner."""
        return True, ""

    def measure_coverage(self) -> float:
        """
        Measure test coverage using go test.

        Returns:
            Coverage percentage
        """
        # Clean test cache to avoid stale object errors
        self.run_command(['go', 'clean', '-testcache'])

        # Run go test with coverage
        result = self.run_command([
            'go', 'test', './...',
            '-coverprofile=coverage.out',
            '-covermode=atomic'
        ])

        if result.returncode != 0:
            print(f"Warning: go test failed: {result.stderr}")
            return 0.0

        # Get coverage percentage
        result = self.run_command(['go', 'tool', 'cover', '-func=coverage.out'])

        if result.returncode != 0:
            return 0.0

        # Parse total coverage from output
        # Format: "total:    (statements)    85.3%"
        output = result.stdout
        match = re.search(r'total:\s+\(statements\)\s+([\d.]+)%', output)

        if match:
            return float(match.group(1))

        # Alternative format: just look for last percentage
        percentages = re.findall(r'([\d.]+)%', output)
        if percentages:
            return float(percentages[-1])

        return 0.0

    def init_module(self, module_name: str = "example") -> None:
        """Initialize go module if not exists."""
        if not Path('go.mod').exists():
            self.run_command(['go', 'mod', 'init', module_name])
            print(f"Initialized go module: {module_name}")

    def tidy(self) -> None:
        """Run go mod tidy."""
        self.run_command(['go', 'mod', 'tidy'])

    def build(self) -> tuple[bool, str]:
        """
        Build Go binary.

        Returns:
            Tuple of (success, output)
        """
        from pathlib import Path

        # Find main package
        main_files = list(Path('.').rglob('main.go'))
        if not main_files:
            # Try cmd/ directory
            main_files = list(Path('cmd').rglob('main.go')) if Path('cmd').exists() else []

        if not main_files:
            return False, "No main.go found"

        # Build each main package
        outputs = []
        for main_file in main_files:
            main_dir = main_file.parent
            binary_name = main_dir.name if main_dir.name != '.' else 'app'

            result = self.run_command([
                'go', 'build',
                '-o', f'bin/{binary_name}',
                f'./{main_dir}'
            ])

            if result.returncode != 0:
                return False, result.stderr

            outputs.append(f"Built: bin/{binary_name}")

        return True, '\n'.join(outputs)
