"""
CLI for cc-tdd

Usage:
    cc-tdd --story story.md --config config.yaml
    cc-tdd --story story.md --language go --coverage 80
"""

import argparse
import re
import sys
import os
import yaml
import select
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

from .phases.refine import RefinePhase
from .phases.implement import ImplementPhase
from .phases.review import ReviewPhase
from .phases.finalize import FinalizePhase
from .git import clone_repo, init_repo, checkout_branch, get_current_branch


@dataclass
class Config:
    """Configuration for cc-tdd run."""
    language: str = "auto"
    coverage_target: int = 80
    max_iterations: int = 10
    branch: str = "feature/story"
    package: Optional[str] = None
    framework: Optional[str] = None

    @classmethod
    def from_file(cls, path: Path) -> 'Config':
        """Load config from YAML file."""
        if not path.exists():
            return cls()

        with open(path) as f:
            data = yaml.safe_load(f) or {}

        return cls(
            language=data.get('language', 'auto'),
            coverage_target=data.get('coverage_target', 80),
            max_iterations=data.get('max_iterations', 10),
            branch=data.get('branch', 'feature/story'),
            package=data.get('package'),
            framework=data.get('framework'),
        )

    def merge_args(self, args: argparse.Namespace) -> 'Config':
        """Merge CLI arguments into config (CLI takes precedence)."""
        if args.language:
            self.language = args.language
        if args.coverage:
            self.coverage_target = args.coverage
        if args.max_iterations:
            self.max_iterations = args.max_iterations
        if args.branch:
            self.branch = args.branch
        return self


def parse_args(argv: list[str] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog='cc-tdd',
        description='Claude Code TDD Builder - Story to Production-Ready Code',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    cc-tdd --story story.md
    cc-tdd --story story.md --language go --coverage 80
    cc-tdd --story story.md --config config.yaml --dry-run

Exit Codes:
    0  Success - branch is PR-ready
    1  Failure - tests/coverage not achieved
    2  Error - invalid input/config
        """
    )

    parser.add_argument(
        '--story', '-s',
        type=str,
        default=None,
        help='Path to story file, or "-" for stdin (default: stdin if piped, else ./story.md)'
    )

    parser.add_argument(
        '--config', '-c',
        type=Path,
        default=Path('config.yaml'),
        help='Path to config YAML file (default: ./config.yaml)'
    )

    parser.add_argument(
        '--workspace', '-w',
        type=Path,
        default=Path('/workspace'),
        help='Working directory (default: /workspace)'
    )

    parser.add_argument(
        '--repo', '-r',
        type=str,
        help='Git repository URL to clone (if not using volume mount)'
    )

    parser.add_argument(
        '--git-token',
        type=str,
        help='Git token for repo access (or use GIT_TOKEN env var)'
    )

    parser.add_argument(
        '--language', '-l',
        choices=['go', 'python', 'java', 'kotlin', 'electron', 'typescript', 'auto'],
        help='Target language (overrides config)'
    )

    parser.add_argument(
        '--coverage',
        type=int,
        help='Coverage target percentage (overrides config)'
    )

    parser.add_argument(
        '--max-iterations',
        type=int,
        help='Maximum TDD iterations (overrides config)'
    )

    parser.add_argument(
        '--branch',
        help='Target branch name (overrides config)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Don't commit, just show what would happen"
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )

    parser.add_argument(
        '--backend',
        choices=['claude', 'opencode'],
        default=None,
        help='LLM backend (default: auto-detect via CC_BACKEND env or which)'
    )

    return parser.parse_args(argv)


def resolve_backend(args_backend: str = None) -> str:
    """Resolve which backend to use: args > env > auto-detect."""
    import shutil

    backend = args_backend or os.environ.get('CC_BACKEND', '').lower() or None
    if backend:
        return backend

    # Auto-detect
    if shutil.which('claude'):
        return 'claude'
    if shutil.which('opencode'):
        return 'opencode'

    print("ERROR: No LLM backend found.", file=sys.stderr)
    print("  Install 'claude' (Claude Code CLI) or 'opencode' (OpenCode CLI)", file=sys.stderr)
    print("  Or set CC_BACKEND=claude|opencode", file=sys.stderr)
    return ''


def validate_environment(backend: str) -> bool:
    """Check required environment variables for the given backend."""
    if backend == 'claude':
        has_oauth = os.environ.get('CLAUDE_CODE_OAUTH_TOKEN')
        has_api_key = os.environ.get('ANTHROPIC_API_KEY')

        if not has_oauth and not has_api_key:
            print("ERROR: Authentication required for Claude backend. Set one of:", file=sys.stderr)
            print("  CLAUDE_CODE_OAUTH_TOKEN  (Max Plan - recommended)", file=sys.stderr)
            print("  ANTHROPIC_API_KEY        (API usage - pay per token)", file=sys.stderr)
            print("", file=sys.stderr)
            print("Generate OAuth token with: claude setup-token", file=sys.stderr)
            return False

        if has_oauth:
            print("Auth: Using Claude Max subscription (OAuth)")
        else:
            print("Auth: Using API key (pay per token)")

    elif backend == 'opencode':
        has_github = os.environ.get('GITHUB_TOKEN')
        has_api_key = os.environ.get('ANTHROPIC_API_KEY')
        has_oauth = Path(Path.home() / '.local' / 'share' / 'opencode' / 'auth.json').exists()
        model = os.environ.get('OPENCODE_MODEL', 'github-copilot/gpt-5.1-codex')

        if not has_github and not has_api_key and not has_oauth:
            print("ERROR: Authentication required for OpenCode backend. Set one of:", file=sys.stderr)
            print("  GITHUB_TOKEN      (Copilot - recommended)", file=sys.stderr)
            print("  ANTHROPIC_API_KEY  (Anthropic API)", file=sys.stderr)
            print("  auth.json          (OpenCode OAuth)", file=sys.stderr)
            return False

        if has_github:
            print("Auth: Using GitHub Copilot token")
        elif has_oauth:
            print("Auth: Using OpenCode OAuth (auth.json)")
        else:
            print("Auth: Using API key")
        print(f"Model: {model}")

    else:
        print(f"ERROR: Unknown backend: {backend}", file=sys.stderr)
        return False

    print(f"Backend: {backend}")
    return True


def has_stdin_data() -> bool:
    """Check if there's data available on stdin."""
    if not sys.stdin.isatty():
        # stdin is piped or redirected
        if hasattr(select, 'select'):
            # Unix: use select to check for data
            return bool(select.select([sys.stdin], [], [], 0.0)[0])
        else:
            # Fallback: assume data if not a tty
            return True
    return False


def read_story(args: argparse.Namespace) -> Optional[str]:
    """
    Read story from stdin or file.

    Priority:
    1. stdin if piped (echo "story" | cc-tdd)
    2. --story - (explicit stdin)
    3. --story <file>
    4. ./story.md (default)
    """
    # Check for piped stdin
    if args.story == '-' or (args.story is None and has_stdin_data()):
        story = sys.stdin.read().strip()
        if story:
            print("Story: read from stdin")
            return story
        print("ERROR: No story provided via stdin", file=sys.stderr)
        return None

    # File path
    story_path = Path(args.story) if args.story else Path('story.md')

    if not story_path.exists():
        print(f"ERROR: Story file not found: {story_path}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Usage:", file=sys.stderr)
        print("  echo 'Your story here' | cc-tdd", file=sys.stderr)
        print("  cc-tdd --story story.md", file=sys.stderr)
        print("  cc-tdd --story -  (read from stdin)", file=sys.stderr)
        return None

    story = story_path.read_text().strip()
    if not story:
        print(f"ERROR: Story file is empty: {story_path}", file=sys.stderr)
        return None

    print(f"Story: {story_path}")
    return story


def branch_name_from_story(story: str) -> str:
    """Generate a descriptive branch name from the story text."""
    # Take first line or first 60 chars
    first_line = story.strip().split('\n')[0][:60]
    # Remove common prefixes
    first_line = re.sub(r'^(als|as a|i want|user story|feature|story)\b[:\s]*', '', first_line, flags=re.IGNORECASE)
    # Slugify: lowercase, replace non-alphanumeric with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', first_line.lower()).strip('-')
    # Limit length
    slug = slug[:50].rstrip('-')
    return f"feature/{slug}" if slug else "feature/story"


def setup_workspace(args: argparse.Namespace, config: 'Config') -> bool:
    """
    Setup workspace: clone repo or use volume mount.

    Returns True if successful.
    """
    workspace = args.workspace

    # Get git token from args or env
    git_token = args.git_token or os.environ.get('GIT_TOKEN') or os.environ.get('GITHUB_TOKEN')

    if args.repo:
        # Clone mode: clone repo into workspace
        if workspace.exists() and any(workspace.iterdir()):
            print(f"ERROR: Workspace {workspace} is not empty", file=sys.stderr)
            return False

        workspace.mkdir(parents=True, exist_ok=True)

        try:
            clone_repo(args.repo, workspace, git_token, config.branch)
        except Exception as e:
            print(f"ERROR: Failed to clone repo: {e}", file=sys.stderr)
            return False
    else:
        # Volume mount mode: workspace should already exist
        if not workspace.exists():
            workspace.mkdir(parents=True, exist_ok=True)

        os.chdir(workspace)

        git_dir = workspace / '.git'
        if git_dir.exists():
            # Existing repo: stay on current branch, don't reinitialize
            current = get_current_branch()
            print(f"Existing workspace detected (branch: {current})")
        else:
            # Fresh workspace: init git and create branch
            init_repo(workspace, config.branch)
            checkout_branch(config.branch)

    os.chdir(workspace)
    return True


def main(argv: list[str] = None) -> int:
    """Main entry point."""
    args = parse_args(argv)

    # Resolve and validate backend
    backend = resolve_backend(args.backend)
    if not backend:
        return 2
    if not validate_environment(backend):
        return 2

    # Read story FIRST (before workspace setup, so stdin works)
    story = read_story(args)
    if not story:
        return 2

    # Load config (from current dir or default)
    config_path = Path(args.config) if args.config else Path('config.yaml')
    if config_path.exists():
        config = Config.from_file(config_path)
    else:
        config = Config()
    config = config.merge_args(args)

    # Setup workspace (clone repo or use volume mount)
    # Must happen before branch name generation so we can detect existing repos
    workspace = args.workspace
    workspace_has_git = (workspace / '.git').exists()

    # Auto-generate branch name from story if not explicitly set
    # Skip if workspace already has a git repo (keep current branch)
    if not workspace_has_git and not args.branch and config.branch == "feature/story":
        config.branch = branch_name_from_story(story)

    if not setup_workspace(args, config):
        return 2

    # Resolve auto language early
    if config.language == 'auto':
        from .runners import detect_language
        try:
            config.language = detect_language()
        except ValueError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 2

    # Always show resolved config
    print(f"Language: {config.language}")
    print(f"Coverage target: {config.coverage_target}%")
    if args.verbose:
        print(f"Max Iterations: {config.max_iterations}")
        print(f"Branch: {config.branch}")
        print(f"Dry Run: {args.dry_run}")
    print()

    try:
        # Phase 1: Story Refinement
        print("=" * 60)
        print("PHASE 1: Story Refinement")
        print("=" * 60)
        refine = RefinePhase(config, args.dry_run, args.verbose, backend=backend)
        refined_story, gherkin = refine.run(story)

        # Phase 2: TDD Implementation Loop
        print()
        print("=" * 60)
        print("PHASE 2: TDD Implementation")
        print("=" * 60)
        implement = ImplementPhase(config, args.dry_run, args.verbose, backend=backend)
        success, coverage, iterations = implement.run(gherkin)

        if not success:
            print(f"\nFAILED: Could not achieve coverage target after {iterations} iterations")
            return 1

        # Phase 3: Code Review
        print()
        print("=" * 60)
        print("PHASE 3: Code Review")
        print("=" * 60)
        review = ReviewPhase(config, args.dry_run, args.verbose, backend=backend)
        review_passed = review.run()

        if not review_passed:
            print("\nFAILED: Code review found critical issues")
            return 1

        # Phase 4: Finalize
        print()
        print("=" * 60)
        print("PHASE 4: Finalize")
        print("=" * 60)
        finalize = FinalizePhase(config, args.dry_run, args.verbose)
        finalize.run(refined_story, coverage, iterations)

        print()
        print("=" * 60)
        print("SUCCESS - Branch is PR-ready")
        print("=" * 60)
        return 0

    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 1
    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 2


if __name__ == '__main__':
    sys.exit(main())
