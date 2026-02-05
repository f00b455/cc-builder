"""
Electron/TypeScript BDD runner using Cucumber.js.
Full dev environment with linting, E2E tests, and packaging.
"""

import re
import json
import subprocess
from typing import Tuple
from pathlib import Path

from .base import BaseRunner


class ElectronRunner(BaseRunner):
    """
    Electron/TypeScript language runner.

    Uses:
    - @cucumber/cucumber for BDD tests
    - jest for unit tests
    - playwright for E2E tests
    - eslint for linting
    - esbuild for bundling
    - electron-builder for packaging
    - c8/nyc for coverage measurement
    """

    @property
    def name(self) -> str:
        return "electron"

    @property
    def bdd_framework(self) -> str:
        return "cucumber-js"

    def setup_project(self) -> None:
        """Initialize project with templates if available."""
        # Run init-electron-project if available (from Docker image)
        result = subprocess.run(
            ['which', 'init-electron-project'],
            capture_output=True
        )
        if result.returncode == 0:
            subprocess.run(['init-electron-project'], capture_output=True)

    def run_bdd(self) -> Tuple[bool, str]:
        """
        Run Cucumber.js BDD tests.

        Returns:
            Tuple of (all_passed, output)
        """
        if not self.features_exist():
            return False, "No feature files found in features/"

        # Ensure npm packages are installed
        if not Path('node_modules').exists():
            self.run_command(['npm', 'install'])

        # Run cucumber-js
        result = self.run_command(['npx', 'cucumber-js', 'features/', '--format', 'progress'])

        output = result.stdout + result.stderr
        success = result.returncode == 0

        # Check for undefined/pending steps
        if 'undefined' in output.lower() or 'pending' in output.lower():
            success = False

        return success, output

    def run_lint(self) -> Tuple[bool, str]:
        """
        Run ESLint on source files.

        Returns:
            Tuple of (passed, output)
        """
        if not Path('eslint.config.js').exists() and not Path('.eslintrc.js').exists():
            return True, "No ESLint config found, skipping"

        result = self.run_command(['npx', 'eslint', 'src/'])
        output = result.stdout + result.stderr
        return result.returncode == 0, output

    def run_e2e(self) -> Tuple[bool, str]:
        """
        Run Playwright E2E tests.

        Returns:
            Tuple of (passed, output)
        """
        if not Path('e2e').exists() and not Path('playwright.config.ts').exists():
            return True, "No E2E tests found, skipping"

        # Use xvfb for headless testing
        result = self.run_command([
            'xvfb-run', '--auto-servernum',
            'npx', 'playwright', 'test'
        ], timeout=120)

        output = result.stdout + result.stderr
        return result.returncode == 0, output

    def measure_coverage(self) -> float:
        """
        Measure test coverage using c8 or jest.

        Returns:
            Coverage percentage
        """
        # Try jest with coverage first (most reliable)
        result = self.run_command(['npx', 'jest', '--coverage', '--coverageReporters=text'])

        if result.returncode == 0:
            coverage = self._parse_jest_output(result.stdout)
            if coverage > 0:
                return coverage

        # Fallback: try c8 with cucumber
        result = self.run_command([
            'npx', 'c8', '--reporter=text',
            'npx', 'cucumber-js', 'features/'
        ])

        if result.returncode == 0:
            coverage = self._parse_c8_output(result.stdout)
            if coverage > 0:
                return coverage

        # Last resort: check package.json for test:coverage script
        if Path('package.json').exists():
            result = self.run_command(['npm', 'run', 'test:coverage'])
            if result.returncode == 0:
                output = result.stdout + result.stderr
                # Try to find any percentage
                percentages = re.findall(r'(\d+(?:\.\d+)?)\s*%', output)
                if percentages:
                    return float(percentages[-1])

        return 0.0

    def _parse_c8_output(self, output: str) -> float:
        """Parse c8 coverage output."""
        # Format: "All files |   80.5 |   75.2 |   90.1 |   80.5 |"
        match = re.search(r'All files\s*\|\s*([\d.]+)', output)
        if match:
            return float(match.group(1))

        # Alternative: look for total line
        match = re.search(r'Statements\s*:\s*([\d.]+)%', output)
        if match:
            return float(match.group(1))

        return 0.0

    def _parse_jest_output(self, output: str) -> float:
        """Parse jest coverage output."""
        # Format: "All files |   80.5 |   75.2 |   90.1 |   80.5 |"
        match = re.search(r'All files\s*\|\s*([\d.]+)', output)
        if match:
            return float(match.group(1))

        # Alternative format
        match = re.search(r'Statements\s*:\s*([\d.]+)%', output)
        if match:
            return float(match.group(1))

        return 0.0

    def setup_steps_dir(self) -> None:
        """Create steps directory structure for Cucumber.js."""
        steps_dir = Path('features/step_definitions')
        steps_dir.mkdir(parents=True, exist_ok=True)

        support_dir = Path('features/support')
        support_dir.mkdir(parents=True, exist_ok=True)

    def create_environment(self) -> None:
        """Create config files if needed (templates from Docker image preferred)."""
        # Try to use Docker templates first
        self.setup_project()

        # Fallback: create minimal configs if not from Docker
        if not Path('tsconfig.json').exists():
            tsconfig = {
                "compilerOptions": {
                    "target": "ES2020",
                    "module": "commonjs",
                    "lib": ["ES2020", "DOM"],
                    "outDir": "./dist",
                    "rootDir": "./src",
                    "strict": True,
                    "esModuleInterop": True,
                    "skipLibCheck": True,
                    "forceConsistentCasingInFileNames": True,
                    "resolveJsonModule": True,
                    "moduleResolution": "node",
                    "declaration": True,
                    "sourceMap": True
                },
                "include": ["src/**/*"],
                "exclude": ["node_modules", "dist", "**/*.test.ts", "features/**/*", "e2e/**/*"]
            }
            Path('tsconfig.json').write_text(json.dumps(tsconfig, indent=2))

        # Basic package.json if not exists
        if not Path('package.json').exists():
            package = {
                "name": "electron-app",
                "version": "1.0.0",
                "main": "dist/main.js",
                "scripts": {
                    "build": "tsc && npm run build:renderer && npm run copy:static",
                    "build:renderer": "esbuild src/renderer/renderer.ts --bundle --outfile=dist/renderer/renderer.js --platform=browser --sourcemap",
                    "copy:static": "cp src/renderer/*.html src/renderer/*.css dist/renderer/ 2>/dev/null || true",
                    "start": "npm run build && electron .",
                    "test": "jest",
                    "test:coverage": "jest --coverage",
                    "test:e2e": "xvfb-run --auto-servernum playwright test",
                    "cucumber": "cucumber-js",
                    "lint": "eslint src/",
                    "lint:fix": "eslint src/ --fix",
                    "validate": "npm run lint && npm run test:coverage && npm run cucumber && npm run build",
                    "dist": "electron-builder",
                    "dist:linux": "electron-builder --linux"
                },
                "devDependencies": {
                    "@cucumber/cucumber": "^10.0.0",
                    "@playwright/test": "^1.40.0",
                    "@types/node": "^20.0.0",
                    "@types/jest": "^29.0.0",
                    "@typescript-eslint/eslint-plugin": "^6.0.0",
                    "@typescript-eslint/parser": "^6.0.0",
                    "c8": "^9.0.0",
                    "electron": "^28.0.0",
                    "electron-builder": "^24.0.0",
                    "esbuild": "^0.19.0",
                    "eslint": "^8.0.0",
                    "jest": "^29.0.0",
                    "ts-jest": "^29.0.0",
                    "ts-node": "^10.9.0",
                    "typescript": "^5.0.0"
                }
            }
            Path('package.json').write_text(json.dumps(package, indent=2))

    def build(self) -> Tuple[bool, str]:
        """
        Build and optionally package Electron app.

        Returns:
            Tuple of (success, output)
        """
        # First run lint
        lint_ok, lint_output = self.run_lint()
        if not lint_ok:
            return False, f"Lint failed:\n{lint_output}"

        # Compile TypeScript (type-check only - catches missing deps/types)
        result = self.run_command(['npx', 'tsc', '--noEmit'], timeout=120)
        if result.returncode != 0:
            return False, f"TypeScript errors:\n{result.stderr or result.stdout}"

        # Run full build
        package_json = Path('package.json')
        if package_json.exists():
            pkg = json.loads(package_json.read_text())
            scripts = pkg.get('scripts', {})

            if 'build' in scripts:
                result = self.run_command(['npm', 'run', 'build'], timeout=120)
                if result.returncode != 0:
                    return False, result.stderr or result.stdout

            # Try to build distributable (Linux in Docker)
            if 'dist:linux' in scripts:
                result = self.run_command(['npm', 'run', 'dist:linux'], timeout=600)
                if result.returncode == 0:
                    # Find built files
                    release_dir = Path('release')
                    if release_dir.exists():
                        built_files = list(release_dir.glob('*.AppImage')) + \
                                     list(release_dir.glob('*.deb'))
                        if built_files:
                            return True, f"Built: {', '.join(str(f) for f in built_files)}"
                    return True, "Built to dist/"

        # Fallback: just compile TypeScript
        result = self.run_command(['npx', 'tsc'], timeout=120)
        if result.returncode == 0:
            return True, "Compiled TypeScript to dist/"

        return False, result.stderr or "Build failed"

    def validate(self) -> Tuple[bool, str]:
        """
        Run full validation: lint + test + coverage + e2e + build.

        Returns:
            Tuple of (all_passed, summary)
        """
        results = []

        # Lint
        lint_ok, lint_out = self.run_lint()
        results.append(f"Lint: {'✓' if lint_ok else '✗'}")

        # Unit tests with coverage
        coverage = self.measure_coverage()
        results.append(f"Coverage: {coverage}%")

        # BDD tests
        bdd_ok, bdd_out = self.run_bdd()
        results.append(f"BDD: {'✓' if bdd_ok else '✗'}")

        # E2E tests
        e2e_ok, e2e_out = self.run_e2e()
        results.append(f"E2E: {'✓' if e2e_ok else '✗'}")

        # Build
        build_ok, build_out = self.build()
        results.append(f"Build: {'✓' if build_ok else '✗'}")

        all_ok = lint_ok and bdd_ok and e2e_ok and build_ok and coverage >= 80
        return all_ok, "\n".join(results)
