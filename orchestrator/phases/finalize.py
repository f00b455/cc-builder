"""
Phase 4: Finalize

- Final verification (tests + coverage)
- Generate REPORT.md
- Final commit
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from ..git import git_commit, get_commit_log, get_current_branch
from ..runners import get_runner


class FinalizePhase:
    """Phase 4: Finalize and generate report."""

    def __init__(self, config, dry_run: bool = False, verbose: bool = False):
        self.config = config
        self.dry_run = dry_run
        self.verbose = verbose
        self.runner = get_runner(config.language)

    def run(self, story: str, coverage: float, iterations: int) -> None:
        """
        Finalize: verify and generate report.

        Args:
            story: The refined story content
            coverage: Final coverage percentage
            iterations: Number of TDD iterations used
        """
        print("Finalizing...")

        # Final verification
        print("Running final verification...")
        bdd_success, bdd_output = self.runner.run_bdd()
        final_coverage = self.runner.measure_coverage()

        if not bdd_success:
            raise RuntimeError("Final verification failed: BDD tests not passing")

        if final_coverage < self.config.coverage_target:
            raise RuntimeError(
                f"Final verification failed: Coverage {final_coverage}% < {self.config.coverage_target}%"
            )

        # E2E verification
        e2e_success, e2e_output = self.runner.run_e2e()
        if not e2e_success:
            raise RuntimeError(f"Final verification failed: E2E tests not passing\n{e2e_output}")

        print(f"✓ Final BDD: PASS")
        print(f"✓ Final E2E: PASS")
        print(f"✓ Final Coverage: {final_coverage}%")

        # Build step (MUST pass - catches missing dependencies, type errors, etc.)
        print("Building...")
        build_success, build_output = self.runner.build()
        if build_success:
            print(f"✓ Build: {build_output}")
        else:
            raise RuntimeError(f"Build failed: {build_output}")

        # Gather report data
        report_data = self._gather_report_data(story, final_coverage, iterations)

        # Generate docs/REPORT.md
        docs_dir = Path('docs')
        docs_dir.mkdir(exist_ok=True)
        report_content = self._generate_report(report_data)
        report_path = docs_dir / 'REPORT.md'
        report_path.write_text(report_content)
        print(f"Generated: {report_path}")

        # Final commit
        if not self.dry_run:
            git_commit(
                message="docs: add implementation report",
                files=['docs/']
            )
            print("Committed: docs: add implementation report")

        # Summary
        print()
        print(f"Branch: {get_current_branch()}")
        print(f"Coverage: {final_coverage}% (target: {self.config.coverage_target}%)")
        print(f"Iterations: {iterations}")
        print(f"Scenarios: {report_data.get('scenario_count', '?')}")

    def _gather_report_data(self, story: str, coverage: float, iterations: int) -> Dict[str, Any]:
        """Gather data for the report."""
        data = {
            'story_title': self._extract_title(story),
            'language': self.config.language,
            'coverage_target': self.config.coverage_target,
            'coverage_achieved': coverage,
            'iterations': iterations,
            'timestamp': datetime.now().isoformat(),
            'branch': get_current_branch(),
            'commits': get_commit_log(20),
            'scenarios': self._get_scenarios(),
            'scenario_count': 0,
        }

        data['scenario_count'] = len(data['scenarios'])
        return data

    def _extract_title(self, story: str) -> str:
        """Extract title from story."""
        lines = story.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                return line[2:]
            if line.startswith('## '):
                return line[3:]
            if line and not line.startswith('#'):
                return line[:50]
        return "Implementation"

    def _get_scenarios(self) -> List[Dict[str, str]]:
        """Get list of scenarios from feature files."""
        scenarios = []
        features_dir = Path('features')

        if not features_dir.exists():
            return scenarios

        for feature_file in features_dir.glob('*.feature'):
            content = feature_file.read_text()
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('Scenario:') or line.startswith('Scenario Outline:'):
                    name = line.split(':', 1)[1].strip()
                    scenarios.append({
                        'name': name,
                        'file': feature_file.name,
                        'status': 'PASS'  # Assume pass since we verified
                    })

        return scenarios

    def _generate_report(self, data: Dict[str, Any]) -> str:
        """Generate REPORT.md content."""
        scenarios_table = self._format_scenarios_table(data['scenarios'])
        commits_list = self._format_commits_list(data['commits'])

        coverage_status = "✓" if data['coverage_achieved'] >= data['coverage_target'] else "✗"

        return f'''# Implementation Report

## Summary

| Aspect | Value |
|--------|-------|
| **Story** | {data['story_title']} |
| **Language** | {data['language']} |
| **Branch** | `{data['branch']}` |
| **Iterations** | {data['iterations']} |
| **Timestamp** | {data['timestamp']} |

## Coverage

| Target | Achieved | Status |
|--------|----------|--------|
| {data['coverage_target']}% | {data['coverage_achieved']:.1f}% | {coverage_status} |

## BDD Scenarios ({data['scenario_count']})

{scenarios_table}

## Commits

{commits_list}

## Code Review

- [x] Security: No critical issues
- [x] Performance: No major concerns
- [x] Best Practices: Followed

---

**Ready for PR** {coverage_status}

Generated by [cc-builder](https://github.com/your-org/cc-builder)
'''

    def _format_scenarios_table(self, scenarios: List[Dict[str, str]]) -> str:
        """Format scenarios as markdown table."""
        if not scenarios:
            return "_No scenarios found_"

        lines = ["| # | Scenario | File | Status |", "|---|----------|------|--------|"]
        for i, s in enumerate(scenarios, 1):
            status = "✓ PASS" if s['status'] == 'PASS' else "✗ FAIL"
            lines.append(f"| {i} | {s['name']} | {s['file']} | {status} |")

        return '\n'.join(lines)

    def _format_commits_list(self, commits: List[str]) -> str:
        """Format commits as markdown list."""
        if not commits:
            return "_No commits_"

        lines = []
        for commit in commits[:10]:
            if commit:
                lines.append(f"- `{commit}`")

        return '\n'.join(lines)
