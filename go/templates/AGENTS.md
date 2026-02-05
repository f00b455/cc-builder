# Go TDD Project

## Tech Stack
- **Language**: Go 1.22+
- **BDD**: godog (Cucumber for Go)
- **Testing**: go test (standard library)
- **Coverage**: go test -cover

## Project Structure
```
├── cmd/
│   └── main.go           # Entry point
├── internal/
│   ├── api/              # HTTP handlers
│   │   ├── handlers.go
│   │   └── handlers_test.go
│   ├── domain/           # Business logic
│   │   ├── models.go
│   │   └── models_test.go
│   └── storage/          # Data persistence
│       ├── store.go
│       └── store_test.go
├── features/
│   ├── *.feature         # Gherkin scenarios
│   └── steps/
│       └── steps_test.go # Step definitions (MUST be _test.go!)
├── docs/
│   └── STORY.md
└── go.mod
```

## Critical Rules

### Clean Code Principles
- **Pure functions** - No side effects, same input = same output
- **Single Responsibility** - Each function does ONE thing
- **Meaningful names** - Variables and functions describe their purpose
- **Small functions** - Max 20-30 lines, prefer smaller
- **No magic numbers** - Use named constants
- **Early returns** - Avoid deep nesting, return early for errors
- **Immutability** - Prefer value types, avoid pointer mutations

### Go Idioms
- Accept interfaces, return structs
- Errors are values - handle them explicitly
- Make zero values useful
- Don't panic in library code

### BDD Step Definitions
- Step files MUST be named `*_test.go` in `features/steps/`
- Use `go test ./features/steps/...` to run BDD tests
- Do NOT use `godog run` CLI

### Testing
- Unit tests: `*_test.go` next to source files
- Table-driven tests preferred
- Coverage target: 80%+
- Test behavior, not implementation

### Code Style
- Use `internal/` for private packages
- Keep `cmd/` minimal - just bootstrap
- Error handling everywhere
- Use `errors.Is()` and `errors.As()` for error checking

## Commands
```bash
go build ./...                      # Build all
go test ./...                       # All tests
go test -v ./features/steps/...     # BDD tests
go test -cover ./internal/...       # Coverage
go test -coverprofile=c.out ./...   # Coverage report
```

## When Extending This Codebase
1. Read existing code first - understand patterns
2. Follow existing package structure
3. Add tests for new code
4. Run `go test ./...` before committing
