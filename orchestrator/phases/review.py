"""
Phase 3: Code Review

Claude reviews the generated code for:
- Security issues
- Performance problems
- Best practices violations
- Code style

And fixes issues automatically.
"""

from pathlib import Path
from typing import List

from ..session import create_session
from ..git import git_commit


REVIEW_PROMPT = '''
Du bist ein erfahrener Code Reviewer.

ZUERST: Verschaffe dir einen Überblick!
1. git diff --stat (was wurde geändert?)
2. Lies die geänderten Dateien
3. Verstehe den Kontext der Änderungen

Führe ein gründliches Code Review durch für alle Dateien die geändert wurden.

Prüfe auf:

## Security
- SQL Injection, Command Injection
- XSS (falls Web)
- Hardcoded Secrets/Credentials
- Unsichere Krypto
- Path Traversal

## Performance
- N+1 Queries
- Memory Leaks
- Ineffiziente Algorithmen
- Unnötige Allokationen

## Best Practices
- Error Handling (keine swallowed errors)
- Logging (ausreichend für Debugging)
- Input Validation
- Resource Cleanup (defer, finally, context managers)

## Code Quality
- Klare Benennung
- Single Responsibility
- DRY (keine unnötige Duplikation)
- Dokumentation wo nötig

WICHTIG:
1. Erstelle docs/CODE_REVIEW.md mit allen Findings
2. Kategorisiere: CRITICAL, HIGH, MEDIUM, LOW
3. CRITICAL und HIGH Issues MUSST du selbst fixen
4. Schreibe die gefixten Dateien mit dem Write-Tool

Format für docs/CODE_REVIEW.md:
```markdown
# Code Review

## Summary
- Status: PASS/FAIL
- Critical: X
- High: X
- Medium: X
- Low: X

## Findings

### [CRITICAL/HIGH/MEDIUM/LOW] Issue Title
- **File**: path/to/file.go
- **Line**: 42
- **Issue**: Description
- **Fix**: How it was fixed (or why not fixable)

## Conclusion
PASS/FAIL with explanation
```

Antworte am Ende mit PASS oder FAIL.
'''


class ReviewPhase:
    """Phase 3: Code review and auto-fix."""

    def __init__(self, config, dry_run: bool = False, verbose: bool = False, backend: str = None):
        self.config = config
        self.dry_run = dry_run
        self.verbose = verbose
        self.session = create_session(backend=backend, verbose=self.verbose)

    def run(self) -> bool:
        """
        Run code review.

        Returns:
            True if review passed (no critical issues or all fixed)
        """
        print("Running code review...")

        # Get list of changed files for context
        changed_files = self._get_changed_files()

        if not changed_files:
            print("  No files to review")
            return True

        # Always show files being reviewed
        print(f"  Reviewing {len(changed_files)} files:")
        for f in changed_files[:10]:
            print(f"    - {f}")
        if len(changed_files) > 10:
            print(f"    ... and {len(changed_files) - 10} more")

        # Send review prompt
        print("  Calling LLM for review...")
        response = self.session.send(REVIEW_PROMPT)
        if self.verbose:
            print(f"  Claude response: {len(response)} chars")

        # Show snippet of findings
        lines = response.strip().split('\n')
        finding_lines = [l for l in lines if 'CRITICAL' in l or 'HIGH' in l or 'MEDIUM' in l]
        if finding_lines:
            print(f"  Findings:")
            for line in finding_lines[:5]:
                print(f"    | {line[:70]}")

        # Check if CODE_REVIEW.md was created
        review_path = Path('docs/CODE_REVIEW.md')
        if not review_path.exists():
            # Fallback: check root
            root_review = Path('CODE_REVIEW.md')
            if root_review.exists():
                Path('docs').mkdir(exist_ok=True)
                root_review.rename(review_path)

        if review_path.exists():
            print(f"  Created: docs/CODE_REVIEW.md")

        # Parse response for PASS/FAIL
        passed = self._parse_review_result(response)

        if passed:
            print("  ✓ Code review passed")

            if not self.dry_run:
                # Commit any fixes and review doc
                git_commit(
                    message="refactor: address code review findings",
                    files=['docs/', '.']
                )
                print("  Committed: refactor: address code review findings")
        else:
            print("  ✗ Code review found unresolved critical issues")

        return passed

    def _get_changed_files(self) -> List[str]:
        """Get list of files changed in this session."""
        import subprocess

        # Get files changed since branch creation
        result = subprocess.run(
            ['git', 'diff', '--name-only', 'HEAD~10'],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            # Fallback: get all tracked files
            result = subprocess.run(
                ['git', 'ls-files'],
                capture_output=True,
                text=True
            )

        files = result.stdout.strip().split('\n')
        return [f for f in files if f and self._is_code_file(f)]

    def _is_code_file(self, path: str) -> bool:
        """Check if file is a code file worth reviewing."""
        # Exclude common build/dependency directories
        excluded_dirs = {
            'node_modules', 'vendor', 'dist', 'build', 'coverage',
            '.git', '__pycache__', '.venv', 'venv', 'target'
        }
        path_parts = Path(path).parts
        if any(part in excluded_dirs for part in path_parts):
            return False

        code_extensions = {
            '.go', '.py', '.java', '.kt', '.js', '.ts',
            '.rs', '.rb', '.php', '.c', '.cpp', '.h'
        }
        return Path(path).suffix in code_extensions

    def _parse_review_result(self, response: str) -> bool:
        """Parse Claude's response for PASS/FAIL."""
        response_lower = response.lower()

        # Look for explicit PASS/FAIL
        if 'pass' in response_lower and 'fail' not in response_lower:
            return True
        if 'fail' in response_lower:
            return False

        # Look for "no critical issues"
        if 'no critical' in response_lower or 'keine kritischen' in response_lower:
            return True

        # Look for remaining critical issues
        if 'critical' in response_lower and ('remaining' in response_lower or 'unfixed' in response_lower):
            return False

        # Default to pass if no clear indicator
        return True
