"""
Phase 2: TDD Implementation Loop

Iterates until:
- All BDD scenarios pass
- Coverage target is reached
- Or max iterations exceeded
"""

from typing import Tuple
from pathlib import Path

from ..session import create_session
from ..runners import get_runner
from ..git import git_commit


IMPLEMENT_PROMPT_INITIAL_GO = '''
WICHTIG: ERWEITERE die bestehende Codebasis - NIEMALS löschen oder neu erstellen!

ZUERST: Analysiere die bestehende Codebasis GRÜNDLICH!
1. ls -la und tree (falls vorhanden) - Struktur verstehen
2. Lies CLAUDE.md falls vorhanden - Projekt-Regeln beachten!
3. Lies ALLE existierenden Go Dateien
4. Verstehe bestehende Patterns, Imports, Strukturen
5. Prüfe ob /opt/go-templates/ existiert (Docker-Umgebung)
6. Falls ja UND CLAUDE.md fehlt: init-go-project ausführen

DANN: Erweitere/verbessere das Feature aus features/*.feature
BEHALTE existierenden Code - füge nur hinzu was fehlt!

Coverage-Ziel: {coverage}%

PROJEKT-STRUKTUR:
```
├── cmd/main.go       # Entry point (MUSS existieren!)
├── internal/
│   ├── api/          # HTTP handlers
│   ├── domain/       # Business logic
│   └── storage/      # Data persistence
├── features/
│   └── steps/        # godog step definitions
└── go.mod
```

VORGEHEN:
1. Lies die .feature Datei(en) - zähle ALLE Steps
2. Erstelle saubere Projekt-Struktur
3. Implementiere JEDEN Step in features/steps/
4. Unit Tests für {coverage}% Coverage

Package: {package}
'''

IMPLEMENT_PROMPT_INITIAL_ELECTRON = '''
WICHTIG: ERWEITERE die bestehende Codebasis - NIEMALS löschen oder neu erstellen!

ZUERST: Analysiere die bestehende Codebasis GRÜNDLICH!
1. ls -la und tree (falls vorhanden) - Struktur verstehen
2. Lies CLAUDE.md falls vorhanden - Projekt-Regeln beachten!
3. Lies ALLE existierenden TypeScript Dateien im src/ Ordner
4. Verstehe bestehende Patterns, Imports, Typen
5. Prüfe ob /opt/electron-templates/ existiert (Docker-Umgebung)
6. Falls ja UND Config-Dateien fehlen: init-electron-project ausführen

DANN: Erweitere/verbessere das Feature aus features/*.feature
BEHALTE existierenden Code - füge nur hinzu was fehlt!

Coverage-Ziel: {coverage}%

WICHTIG - TYPESCRIPT ONLY!
- ALLE Dateien in .ts (NIEMALS .js)
- Strikte Typisierung
- Keine any-Types

PROJEKT-STRUKTUR (STRIKT EINHALTEN!):
```
├── src/
│   ├── main.ts           # Electron main process
│   ├── preload.ts        # Preload script
│   ├── renderer/
│   │   ├── renderer.ts   # Renderer logic
│   │   ├── index.html
│   │   └── styles.css
│   ├── domain/           # Business logic + tests
│   │   ├── Note.ts
│   │   └── Note.test.ts
│   ├── storage/          # Persistence + tests
│   └── ipc/              # IPC handlers + tests
├── features/
│   ├── *.feature
│   └── steps/            # TypeScript step definitions!
│       └── *.steps.ts
├── e2e/                  # Playwright tests
│   └── app.spec.ts
├── tsconfig.json
├── jest.config.js
├── eslint.config.js
├── playwright.config.ts
└── package.json
```

ELECTRON-SPEZIFISCH:
- KEIN prompt(), alert(), confirm() im Renderer!
- contextIsolation: true
- nodeIntegration: false
- Preload für IPC

VORGEHEN:
1. Falls init-electron-project verfügbar: ausführen
2. Lies die .feature Datei(en)
3. src/domain/ mit Tests erstellen
4. src/storage/ mit Tests erstellen
5. src/ipc/ für Electron IPC
6. features/steps/*.ts für Cucumber
7. Renderer mit esbuild bundeln

Package: {package}
'''

IMPLEMENT_PROMPT_INITIAL_JVM = '''
WICHTIG: ERWEITERE die bestehende Codebasis - NIEMALS löschen oder neu erstellen!

ZUERST: Analysiere die bestehende Codebasis GRÜNDLICH!
1. ls -la und tree (falls vorhanden) - Struktur verstehen
2. Lies CLAUDE.md falls vorhanden - Projekt-Regeln beachten!
3. Lies ALLE existierenden Java/Kotlin Dateien
4. Verstehe bestehende Patterns, Packages, Imports
5. Prüfe ob /opt/jvm-templates/ existiert (Docker-Umgebung)
6. Falls ja UND build.gradle.kts fehlt: init-jvm-project ausführen

DANN: Erweitere/verbessere das Feature aus features/*.feature
BEHALTE existierenden Code - füge nur hinzu was fehlt!

Coverage-Ziel: {coverage}%

SPRING BOOT MICROSERVICE ARCHITEKTUR:
```
src/main/java/de/prehcm/
├── Application.java              # @SpringBootApplication
├── controller/                   # @RestController
├── service/                      # @Service (Business Logic)
├── repository/                   # @Repository (Spring Data JPA)
├── model/                        # @Entity (JPA Entities)
├── dto/                          # Request/Response DTOs
└── exception/                    # @RestControllerAdvice
src/main/resources/
└── application.yaml              # Spring Config + Actuator
src/test/java/de/prehcm/
├── controller/*Test.java         # @WebMvcTest
├── service/*Test.java            # Unit Tests
└── repository/*Test.java         # @DataJpaTest
features/
├── *.feature
└── steps/*StepDefs.java          # Cucumber Steps
build.gradle.kts
```

SPRING BOOT REGELN:
- Constructor Injection (KEIN @Autowired auf Feldern!)
- DTOs an Grenzen (Controller empfängt/sendet DTOs, NICHT Entities)
- @Transactional auf Service-Methoden die Daten ändern
- @Valid auf @RequestBody Parameter
- ResponseEntity<> als Return-Type in Controllern
- UUID als Primary Key
- LocalDateTime für Timestamps
- Actuator Health-Endpoints für K8s

VORGEHEN:
1. Lies die .feature Datei(en)
2. Erstelle/erweitere Model + Repository
3. Erstelle/erweitere Service + Controller
4. Cucumber Steps implementieren
5. Unit Tests für {coverage}% Coverage
6. MockMvc-Tests für Controller

Package: {package}
'''

IMPLEMENT_PROMPT_INITIAL = '''
Sprache: {language}
Framework: {framework}

{language_specific_prompt}

WICHTIGE REGELN:
- NIEMALS existierenden Code löschen oder überschreiben!
- IMMER auf bestehendem Code aufbauen
- Lies ALLE relevanten Dateien BEVOR du etwas änderst
- Separation of Concerns
- {coverage}% Coverage erreichen
- Error Handling überall

CLEAN CODE:
- Pure Functions bevorzugen (keine Side Effects)
- Single Responsibility - eine Funktion = eine Aufgabe
- Aussagekräftige Namen für Variablen und Funktionen
- Kleine Funktionen (max 20-30 Zeilen)
- Early Returns statt tiefer Verschachtelung
- Keine Magic Numbers - benannte Konstanten verwenden

Los!
'''

IMPLEMENT_PROMPT_ITERATION = '''
Test-Ergebnis:

{bdd_output}

Coverage: {coverage}% (Ziel: {target}%)

{status}

AKTION ERFORDERLICH:

## Falls BDD Tests FEHLSCHLAGEN (undefined steps):

Wenn du "ctx.Step" Vorschläge siehst:
1. Öffne die steps.go / steps.ts Datei
2. KOPIERE die vorgeschlagenen Funktionen EXAKT
3. Implementiere den Body jeder Funktion

## Falls Tests GRÜN aber Coverage ZU NIEDRIG:

Coverage erhöhen durch UNIT TESTS (nicht mehr BDD!):
1. Lies existierende *_test.go Dateien
2. Füge Tests für UNGETESTETE Pfade hinzu:
   - Error cases (invalid input, not found, etc.)
   - Edge cases (empty strings, zero values, nil)
   - Alle public functions müssen Tests haben
3. Nutze Table-Driven Tests für mehrere Cases

Beispiel Unit Test:
```go
func TestTodo_Validate(t *testing.T) {{
    tests := []struct{{
        name    string
        title   string
        wantErr bool
    }}{{
        {{"valid", "Buy milk", false}},
        {{"empty title", "", true}},
    }}
    for _, tt := range tests {{
        t.Run(tt.name, func(t *testing.T) {{
            todo := &Todo{{Title: tt.title}}
            err := todo.Validate()
            if (err != nil) != tt.wantErr {{
                t.Errorf("Validate() error = %v, wantErr %v", err, tt.wantErr)
            }}
        }})
    }}
}}
```

WICHTIG: Füge mindestens 3-5 neue Test-Cases pro Datei hinzu!

{e2e_section}
'''


class ImplementPhase:
    """Phase 2: TDD implementation loop."""

    def __init__(self, config, dry_run: bool = False, verbose: bool = False, backend: str = None):
        self.config = config
        self.dry_run = dry_run
        self.verbose = verbose
        self.session = create_session(backend=backend, verbose=self.verbose)
        self.runner = get_runner(config.language)

    def _get_language_prompt(self) -> str:
        """Get language-specific implementation prompt."""
        if self.config.language == 'electron':
            return IMPLEMENT_PROMPT_INITIAL_ELECTRON.format(
                coverage=self.config.coverage_target,
                package=self.config.package or "auto"
            )
        elif self.config.language == 'go':
            return IMPLEMENT_PROMPT_INITIAL_GO.format(
                coverage=self.config.coverage_target,
                package=self.config.package or "auto"
            )
        elif self.config.language in ('java', 'kotlin'):
            return IMPLEMENT_PROMPT_INITIAL_JVM.format(
                coverage=self.config.coverage_target,
                package=self.config.package or "de.prehcm"
            )
        else:
            return f"Language: {self.config.language}\nCoverage: {self.config.coverage_target}%"

    def run(self, gherkin: str) -> Tuple[bool, float, int]:
        """
        Run TDD loop until success or max iterations.

        Returns:
            Tuple of (success, final_coverage, iterations_used)
        """
        # Initial implementation prompt with language-specific content
        language_prompt = self._get_language_prompt()
        prompt = IMPLEMENT_PROMPT_INITIAL.format(
            coverage=self.config.coverage_target,
            framework=self.config.framework or "standard",
            package=self.config.package or "auto",
            language=self.config.language,
            language_specific_prompt=language_prompt
        )

        print(f"Starting TDD loop (max {self.config.max_iterations} iterations)")
        print(f"  Language: {self.config.language}")
        print(f"  Coverage target: {self.config.coverage_target}%")
        print(f"  Runner: {self.runner.__class__.__name__}")
        print()

        # Initialize project from templates if available
        self.runner.init_project()

        print("  Calling LLM for initial implementation...")
        response = self.session.send(prompt)
        if self.verbose:
            print(f"  Claude response: {len(response)} chars")

        for iteration in range(1, self.config.max_iterations + 1):
            print()
            print(f"--- Iteration {iteration}/{self.config.max_iterations} ---")

            # Run BDD tests
            print("  Running BDD tests...")
            bdd_success, bdd_output = self.runner.run_bdd()

            # Measure coverage
            print("  Measuring coverage...")
            coverage = self.runner.measure_coverage()

            print(f"  BDD: {'✓ PASS' if bdd_success else '✗ FAIL'}")
            print(f"  Coverage: {coverage}%")

            if not bdd_success and bdd_output:
                # Show test output snippet - more context for debugging
                all_lines = bdd_output.strip().split('\n')
                # Show first 15 lines (scenario names and undefined steps) + last 25 lines (suggestions)
                first_lines = all_lines[:15]
                last_lines = all_lines[-25:] if len(all_lines) > 40 else all_lines[15:]
                print("  Test output (first 15 lines):")
                for line in first_lines:
                    print(f"    | {line[:100]}")
                if len(all_lines) > 40:
                    print(f"    | ... ({len(all_lines) - 40} lines omitted)")
                print("  Test output (last 25 lines):")
                for line in last_lines:
                    print(f"    | {line[:100]}")

            # Run E2E tests
            print("  Running E2E tests...")
            e2e_success, e2e_output = self.runner.run_e2e()
            print(f"  E2E: {'✓ PASS' if e2e_success else '✗ FAIL'}")

            if not e2e_success and e2e_output:
                snippet = e2e_output.strip().split('\n')[-20:]
                print("  E2E output (last 20 lines):")
                for line in snippet:
                    print(f"    | {line[:100]}")

            # Check success criteria
            if bdd_success and coverage >= self.config.coverage_target and e2e_success:
                print(f"\n✓ All scenarios pass, coverage {coverage}% >= {self.config.coverage_target}%, E2E pass")

                if not self.dry_run:
                    git_commit(
                        message=f"feat: implement feature (iteration {iteration})",
                        files=['.']
                    )
                    print(f"Committed: feat: implement feature (iteration {iteration})")

                return True, coverage, iteration

            # Prepare next iteration prompt
            if not bdd_success:
                status = "STATUS: BDD Tests FEHLGESCHLAGEN - Implementiere die fehlenden Steps!"
            elif not e2e_success:
                status = "STATUS: BDD Tests GRÜN aber E2E Tests FEHLGESCHLAGEN - Fixe die UI damit die E2E-Tests bestehen!"
            else:
                coverage_gap = self.config.coverage_target - coverage
                status = f"STATUS: Tests GRÜN aber Coverage {coverage}% < {self.config.coverage_target}% (fehlen {coverage_gap:.1f}%). FÜGE UNIT TESTS HINZU für error cases und edge cases!"

            # Build E2E section for iteration prompt
            if not e2e_success:
                e2e_section = f"""
E2E Test-Ergebnis:
{e2e_output}

STATUS: E2E Tests FEHLGESCHLAGEN - Implementiere die fehlenden E2E-Tests
und fixe die UI damit die Tests bestehen!
"""
            else:
                e2e_section = ""

            prompt = IMPLEMENT_PROMPT_ITERATION.format(
                bdd_output=bdd_output,
                coverage=coverage,
                target=self.config.coverage_target,
                status=status,
                e2e_section=e2e_section
            )

            print(f"  Calling LLM to fix issues...")
            response = self.session.send(prompt)
            if self.verbose:
                print(f"  Claude response: {len(response)} chars")

        # Max iterations reached
        print(f"\n✗ Max iterations ({self.config.max_iterations}) reached")
        return False, coverage, self.config.max_iterations
