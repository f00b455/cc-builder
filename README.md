# cc-builder

**Story → Production-Ready Code**

Ein Docker Container der aus einer kurzen Story-Beschreibung produktionsreifen Code generiert:
- Gherkin Szenarien (BDD)
- Implementierung mit garantierter Test-Coverage
- Code Review
- Git Commits auf Feature Branch

## Quick Start

```bash
# Einfachste Variante - Story direkt pipen:
echo "REST API für Todo-Liste mit CRUD Operationen" \
  | docker run -i --rm \
      -v $(pwd):/workspace \
      -e CLAUDE_CODE_OAUTH_TOKEN \
      ghcr.io/your-org/cc-builder:go

# Ergebnis: Feature Branch mit Code, Tests, Gherkin, Report
git log --oneline
cat REPORT.md
```

## Authentication

```bash
# Empfohlen: Claude Max Plan (im Abo inkludiert)
export CLAUDE_CODE_OAUTH_TOKEN=$(claude setup-token)

# Alternative: API Key (pay per token)
export ANTHROPIC_API_KEY=sk-...
```

## Usage

### Via stdin (empfohlen)

```bash
# Minimal
echo "User Login mit JWT" | docker run -i -e CLAUDE_CODE_OAUTH_TOKEN cc-builder:go

# Mit Optionen
echo "GraphQL API für Blog" | docker run -i \
  -v $(pwd):/workspace \
  -e CLAUDE_CODE_OAUTH_TOKEN \
  cc-builder:go \
  --coverage 90 \
  --branch feature/blog-api
```

### Via File

```bash
cat > story.md << 'EOF'
# User Authentication

Benutzer können sich registrieren und einloggen.
Passwörter werden sicher gehasht.
JWT Tokens für Sessions, 24h gültig.
EOF

docker run --rm \
  -v $(pwd):/workspace \
  -e CLAUDE_CODE_OAUTH_TOKEN \
  cc-builder:go \
  --story story.md
```

### CI/CD (Repo Clone)

```bash
echo "Story..." | docker run -i \
  -e CLAUDE_CODE_OAUTH_TOKEN \
  -e GIT_TOKEN \
  cc-builder:go \
  --repo https://github.com/org/repo \
  --branch feature/issue-123
```

## Images

| Image | Language | BDD Framework |
|-------|----------|---------------|
| `cc-builder:go` | Go 1.22 | godog |
| `cc-builder:python` | Python 3.12 | behave |
| `cc-builder:jvm` | Java 21 / Kotlin | Cucumber |
| `cc-builder:electron` | TypeScript/Electron | Cucumber.js |

## Options

```
--story FILE       Story file oder "-" für stdin
--config FILE      Config YAML (optional)
--language LANG    go, python, java, kotlin, auto
--coverage N       Coverage target % (default: 80)
--max-iterations N Max TDD loops (default: 10)
--branch NAME      Target branch
--repo URL         Git repo URL (statt volume mount)
--git-token TOKEN  Git token für repo access
--dry-run          Keine commits
```

## Output

```
workspace/
├── STORY.md         # Refined story + acceptance criteria
├── REPORT.md        # Implementation report
├── features/
│   └── *.feature    # Generated Gherkin scenarios
└── [code]           # Generated implementation
```

## How it Works

1. **Story Refinement**: Claude analysiert die Story, erstellt Akzeptanzkriterien und initiale Gherkin-Szenarien

2. **TDD Loop**: Claude implementiert Code, erkennt Edge Cases, fügt neue Szenarien hinzu - bis Coverage erreicht

3. **Code Review**: Claude reviewed den Code auf Security, Performance, Best Practices - und fixt selbst

4. **Finalize**: Finale Verifikation, Report generieren, Git commits

## Build

```bash
# Base image
docker build -f Dockerfile.base -t cc-builder:base .

# Language images
docker build -f Dockerfile.go -t cc-builder:go .
docker build -f Dockerfile.python -t cc-builder:python .
docker build -f Dockerfile.jvm -t cc-builder:jvm .
docker build -f Dockerfile.electron -t cc-builder:electron .
```

## License

MIT
