"""
Language-specific BDD runners.

Each runner knows how to:
- Run BDD tests (godog, behave, cucumber)
- Measure code coverage
- Parse test output
"""

from typing import TYPE_CHECKING
from .base import BaseRunner
from .go import GoRunner
from .python import PythonRunner
from .jvm import JVMRunner
from .electron import ElectronRunner

if TYPE_CHECKING:
    pass


def get_runner(language: str) -> BaseRunner:
    """
    Get the appropriate runner for the language.

    Args:
        language: go, python, java, kotlin, electron, or auto

    Returns:
        Language-specific runner instance
    """
    runners = {
        'go': GoRunner,
        'python': PythonRunner,
        'java': JVMRunner,
        'kotlin': JVMRunner,
        'electron': ElectronRunner,
        'typescript': ElectronRunner,
    }

    if language == 'auto':
        language = detect_language()

    runner_class = runners.get(language)
    if not runner_class:
        raise ValueError(f"Unsupported language: {language}. Supported: {list(runners.keys())}")

    return runner_class()


def detect_language() -> str:
    """
    Auto-detect project language based on files present.

    Returns:
        Detected language string
    """
    import os
    from pathlib import Path

    # Check for default language from image (e.g., cc-builder:go sets CC_DEFAULT_LANGUAGE=go)
    default_lang = os.environ.get('CC_DEFAULT_LANGUAGE')
    if default_lang:
        print(f"Using default language from image: {default_lang}")
        return default_lang

    # Check for language-specific files
    checks = [
        ('go.mod', 'go'),
        ('go.sum', 'go'),
        ('pyproject.toml', 'python'),
        ('requirements.txt', 'python'),
        ('setup.py', 'python'),
        ('build.gradle', 'java'),
        ('build.gradle.kts', 'kotlin'),
        ('pom.xml', 'java'),
    ]

    for filename, lang in checks:
        if Path(filename).exists():
            print(f"Auto-detected language: {lang} (found {filename})")
            return lang

    # Check for Electron/TypeScript (package.json with electron)
    package_json = Path('package.json')
    if package_json.exists():
        import json
        try:
            pkg = json.loads(package_json.read_text())
            deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
            if 'electron' in deps:
                print("Auto-detected language: electron (found electron in package.json)")
                return 'electron'
        except json.JSONDecodeError:
            pass

    # Check for source files
    if list(Path('.').rglob('*.go')):
        return 'go'
    if list(Path('.').rglob('*.py')):
        return 'python'
    if list(Path('.').rglob('*.kt')):
        return 'kotlin'
    if list(Path('.').rglob('*.java')):
        return 'java'
    if list(Path('.').rglob('*.ts')) or list(Path('.').rglob('*.tsx')):
        print("Auto-detected language: electron (found TypeScript files)")
        return 'electron'

    raise ValueError("Could not auto-detect language. Please specify --language")


__all__ = ['get_runner', 'detect_language', 'BaseRunner', 'GoRunner', 'PythonRunner', 'JVMRunner', 'ElectronRunner']
