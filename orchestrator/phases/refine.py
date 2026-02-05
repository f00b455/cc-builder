"""
Phase 1: Story Refinement

Takes minimal story input and produces:
- Structured STORY.md with acceptance criteria
- Initial Gherkin scenarios in features/
"""

import subprocess
import os
from pathlib import Path
from typing import Tuple

from ..session import create_session
from ..git import git_commit


REFINE_PROMPT = '''
Du bist ein erfahrener Product Owner und Tech Lead.

WICHTIG: ERWEITERE die bestehende Codebasis - NIEMALS löschen oder überschreiben!

ZUERST: Analysiere die bestehende Codebasis GRÜNDLICH!
- Lies CLAUDE.md falls vorhanden - Projekt-Regeln beachten!
- Lies existierende Dateien (ls, cat, find)
- Verstehe die aktuelle Projekt-Struktur
- Identifiziere bestehende Patterns und Konventionen
- Prüfe ob docs/, features/, src/ etc. bereits existieren
- BEHALTE existierenden Code und Dokumentation!

Ich gebe dir eine kurze Story-Beschreibung. Deine Aufgabe:

1. **docs/STORY.md erstellen** mit:
   - Feature-Titel
   - User Story (Als... möchte ich... um...)
   - Akzeptanzkriterien als Checklist
   - Technische Notizen (falls relevant)

2. **Gherkin-Szenarien schreiben** in features/<feature>.feature:
   - MAXIMAL 3-4 Szenarien (STRIKT!)
   - 1x Happy Path (Create + Read)
   - 1x Update
   - 1x Delete
   - 1x Error Case (optional)
   - SIMPLE Steps: "I create a todo", "the response is 200"
   - KEINE Parameter in Steps wenn möglich

WICHTIG:
- Schreibe ECHTE Dateien mit dem Write-Tool
- docs/ Verzeichnis für alle Markdown-Dateien
- features/ Verzeichnis für Gherkin
- Gherkin auf Englisch, STORY.md kann Deutsch sein
- Denke an Security, Validierung, Edge Cases

Story:
{story}

Sprache: {language}
Package/Modul: {package}
'''


class RefinePhase:
    """Phase 1: Refine story and generate initial Gherkin."""

    def __init__(self, config, dry_run: bool = False, verbose: bool = False, backend: str = None):
        self.config = config
        self.dry_run = dry_run
        self.verbose = verbose
        self.session = create_session(backend=backend, verbose=self.verbose)

    def run(self, story: str) -> Tuple[str, str]:
        """
        Refine story and generate Gherkin.

        Returns:
            Tuple of (refined_story, gherkin_content)
        """
        print("Analyzing story and generating Gherkin...")
        print(f"  Input: {story[:100]}{'...' if len(story) > 100 else ''}")

        # Prepare prompt
        prompt = REFINE_PROMPT.format(
            story=story,
            language=self.config.language,
            package=self.config.package or "auto-detect"
        )

        # Run Claude
        print("  Calling LLM...")
        response = self.session.send(prompt)
        if self.verbose:
            print(f"  Claude response: {len(response)} chars")

        # Show snippet of response (verbose only)
        if self.verbose:
            lines = response.strip().split('\n')
            preview_lines = lines[:5] if len(lines) > 5 else lines
            for line in preview_lines:
                print(f"    | {line[:80]}")
            if len(lines) > 5:
                print(f"    | ... ({len(lines) - 5} more lines)")

        # Wait for files to be created
        # Claude will create docs/STORY.md and features/*.feature

        # Ensure docs directory exists
        docs_dir = Path('docs')
        docs_dir.mkdir(exist_ok=True)

        # Read results - check docs/ first, then root (fallback)
        story_path = docs_dir / 'STORY.md'
        if not story_path.exists():
            # Fallback: check root and move to docs/
            root_story = Path('STORY.md')
            if root_story.exists():
                root_story.rename(story_path)
            else:
                raise RuntimeError("Claude did not create STORY.md")

        refined_story = story_path.read_text()

        # Find generated feature files
        features_dir = Path('features')
        if not features_dir.exists():
            raise RuntimeError("Claude did not create features/ directory")

        feature_files = list(features_dir.glob('*.feature'))
        if not feature_files:
            raise RuntimeError("Claude did not create any .feature files")

        gherkin = '\n\n'.join(f.read_text() for f in feature_files)

        # Always show created files
        print(f"\n  Created files:")
        print(f"    - docs/STORY.md ({len(refined_story)} chars)")
        for f in feature_files:
            content = f.read_text()
            scenarios = content.count('Scenario')
            print(f"    - {f} ({scenarios} scenarios)")

        # Commit
        if not self.dry_run:
            git_commit(
                message="docs: refine story and initial gherkin",
                files=['docs/', 'features/']
            )
            print("Committed: docs: refine story and initial gherkin")

        return refined_story, gherkin
