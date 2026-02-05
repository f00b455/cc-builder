# Go TDD Project

Go 1.22+ with godog BDD, standard library testing, 80%+ coverage target.

## Structure
- `cmd/main.go` — entry point (minimal bootstrap)
- `internal/api/` — HTTP handlers
- `internal/domain/` — business logic
- `internal/storage/` — data persistence
- `features/*.feature` + `features/steps/*_test.go` — BDD scenarios

## Rules
- Accept interfaces, return structs
- Errors are values — handle explicitly, use `errors.Is()`/`errors.As()`
- BDD steps MUST be `*_test.go` files — run with `go test`, not `godog run`
- Pure functions, single responsibility, max 20-30 lines
- Early returns for errors, named constants, prefer value types
- Use `internal/` for private packages
- Don't panic in library code, make zero values useful

## Testing
- Unit tests: `*_test.go` next to source, table-driven preferred
- BDD: `go test -v ./features/steps/...`
- Coverage: `go test -cover ./internal/...` (80%+ target)

## Commands
- `go build ./...` — build
- `go test ./...` — all tests
- `go test -v ./features/steps/...` — BDD
- `go test -cover ./internal/...` — coverage
