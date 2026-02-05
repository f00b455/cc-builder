"""
Git operations for cc-tdd.
"""

import subprocess
import os
from pathlib import Path
from typing import Optional, List


def run_git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a git command."""
    result = subprocess.run(
        ['git', *args],
        capture_output=True,
        text=True
    )
    if check and result.returncode != 0:
        raise RuntimeError(f"Git command failed: git {' '.join(args)}\n{result.stderr}")
    return result


def clone_repo(repo_url: str, workspace: Path, token: Optional[str] = None, branch: Optional[str] = None) -> None:
    """
    Clone a repository into the workspace.

    Args:
        repo_url: Repository URL (https://github.com/org/repo)
        workspace: Target directory
        token: Git token for authentication
        branch: Branch to checkout after clone
    """
    # Insert token into URL if provided
    if token:
        # https://github.com/org/repo -> https://token@github.com/org/repo
        if repo_url.startswith('https://'):
            repo_url = repo_url.replace('https://', f'https://{token}@')

    # Clone
    print(f"Cloning {repo_url.split('@')[-1]}...")  # Don't log token
    subprocess.run(
        ['git', 'clone', '--depth=1', repo_url, str(workspace)],
        check=True,
        capture_output=True,
        text=True
    )

    # Checkout branch if specified
    if branch:
        os.chdir(workspace)
        # Try to checkout existing branch, or create new one
        result = run_git('checkout', branch, check=False)
        if result.returncode != 0:
            run_git('checkout', '-b', branch)
            print(f"Created branch: {branch}")
        else:
            print(f"Checked out branch: {branch}")


def init_repo(workspace: Path, feature_branch: str = 'feature/story') -> None:
    """
    Initialize a new git repository with proper branch structure.

    Creates:
    - main branch with initial commit
    - feature branch for development
    """
    git_dir = workspace / '.git'

    if git_dir.exists():
        # Repo exists, just ensure we're on feature branch
        return

    os.chdir(workspace)

    # Initialize repo
    run_git('init')

    # Create main branch with initial commit
    run_git('checkout', '-b', 'main')

    # Create .gitignore
    gitignore = workspace / '.gitignore'
    if not gitignore.exists():
        gitignore.write_text('''# Dependencies
node_modules/
vendor/
__pycache__/
*.pyc

# Build
dist/
build/
*.exe
*.dll
*.so
*.dylib

# IDE
.idea/
.vscode/
*.swp
*.swo

# Coverage
coverage.out
coverage/
.nyc_output/

# OS
.DS_Store
Thumbs.db

# Secrets
.env
*.key
*.pem
''')

    # Create docs directory
    docs_dir = workspace / 'docs'
    docs_dir.mkdir(exist_ok=True)

    # Initial commit on main
    run_git('add', '-A')
    result = run_git('diff', '--cached', '--quiet', check=False)
    if result.returncode != 0:
        run_git('commit', '-m', 'chore: initial project setup')
        print("Created main branch with initial commit")

    # Create feature branch from main
    run_git('checkout', '-b', feature_branch)
    print(f"Created feature branch: {feature_branch}")


def checkout_branch(branch: str, create: bool = True) -> None:
    """Checkout or create a branch."""
    result = run_git('checkout', branch, check=False)
    if result.returncode != 0 and create:
        run_git('checkout', '-b', branch)
        print(f"Created branch: {branch}")
    elif result.returncode == 0:
        print(f"Checked out branch: {branch}")
    else:
        raise RuntimeError(f"Failed to checkout branch: {branch}")


def git_commit(message: str, files: Optional[List[str]] = None) -> bool:
    """
    Create a git commit.

    Args:
        message: Commit message
        files: Files to add (default: all changes)

    Returns:
        True if commit was created, False if nothing to commit
    """
    # Add files
    if files:
        for f in files:
            run_git('add', f, check=False)
    else:
        run_git('add', '-A')

    # Check if there are changes to commit
    result = run_git('diff', '--cached', '--quiet', check=False)
    if result.returncode == 0:
        print("Nothing to commit")
        return False

    # Commit
    run_git('commit', '-m', message)
    return True


def git_push(remote: str = 'origin', branch: Optional[str] = None) -> None:
    """Push to remote."""
    args = ['push', '-u', remote]
    if branch:
        args.append(branch)
    else:
        args.append('HEAD')
    run_git(*args)
    print(f"Pushed to {remote}")


def get_current_branch() -> str:
    """Get the current branch name."""
    result = run_git('rev-parse', '--abbrev-ref', 'HEAD')
    return result.stdout.strip()


def get_commit_log(count: int = 10) -> List[str]:
    """Get recent commit messages."""
    result = run_git('log', f'-{count}', '--oneline', check=False)
    if result.returncode != 0:
        return []
    return result.stdout.strip().split('\n')
