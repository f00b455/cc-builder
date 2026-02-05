# Electron TypeScript Project

## Tech Stack
- **Runtime**: Electron 28+
- **Language**: TypeScript (strict mode)
- **Bundler**: esbuild (for renderer)
- **Testing**: Jest (unit), Cucumber (BDD), Playwright (E2E)
- **Linting**: ESLint with TypeScript rules

## Project Structure
```
src/
├── main.ts           # Electron main process
├── preload.ts        # Preload script (contextBridge)
├── renderer/
│   ├── renderer.ts   # Renderer logic (bundled with esbuild)
│   ├── index.html
│   └── styles.css
├── domain/           # Business logic
│   ├── *.ts
│   └── *.test.ts
├── storage/          # Data persistence
│   ├── *.ts
│   └── *.test.ts
└── ipc/              # IPC handlers
    ├── *.ts
    └── *.test.ts

features/             # BDD scenarios
├── *.feature
└── steps/*.ts

e2e/                  # Playwright E2E tests
└── *.spec.ts
```

## Critical Rules

### Clean Code Principles
- **Pure functions** - No side effects, same input = same output
- **Single Responsibility** - Each function does ONE thing
- **Meaningful names** - Variables and functions describe their purpose
- **Small functions** - Max 20-30 lines, prefer smaller
- **No magic numbers** - Use named constants
- **Early returns** - Avoid deep nesting
- **Immutability** - Prefer `const`, avoid mutations

### Electron Security
- `contextIsolation: true` - ALWAYS
- `nodeIntegration: false` - ALWAYS
- Use `preload.ts` with `contextBridge` for IPC

### Node.js vs Browser Context
- Main process = Node.js: Use `import { randomUUID } from 'crypto'` (NOT global `crypto`)
- Renderer process = Browser: bundled with esbuild, NO Node.js APIs
- The global `crypto` object is WebCrypto (browser only), NOT Node.js `crypto` module
- NEVER use `crypto.randomUUID()` without importing from Node.js `crypto` module first

### NO Browser Dialogs
ESLint will FAIL if you use:
- `prompt()` - Use custom modal instead
- `alert()` - Use toast notification instead
- `confirm()` - Use custom dialog instead

### TypeScript
- NO `any` types
- ALL files must be `.ts` (never `.js`)
- Strict null checks enabled
- Use interfaces for data structures
- Use enums for fixed sets of values

### Dependencies
- EVERY npm package you import MUST be in package.json FIRST
- Run `npm install <package>` BEFORE importing it
- Run `npm install --save-dev @types/<package>` for TypeScript types
- NEVER import a package that is not in package.json
- Prefer zero-dependency solutions over adding new packages
- If a feature can be built with Node.js built-in modules, DO NOT add external packages

## Commands
```bash
npm run build          # TypeScript + esbuild bundle
npm run start          # Build and run Electron
npm run test           # Jest unit tests
npm run test:coverage  # Jest with coverage (80% min)
npm run lint           # ESLint check
npm run cucumber       # BDD tests
npm run test:e2e       # Playwright E2E (headless)
npm run validate       # All checks
npm run dist:linux     # Package for Linux
npm run dist:mac       # Package for macOS
npm run dist:win       # Package for Windows
```

## Testing Requirements
- Unit tests: 80% coverage minimum
- BDD tests: All scenarios in `features/*.feature` must pass
- E2E tests: `npm run test:e2e` must pass

### E2E Test Rules (CRITICAL)
- For EVERY `.feature` file there MUST be a corresponding `e2e/*.spec.ts` file
- E2E tests drive the actual Electron app via Playwright — they are NOT smoke tests
- E2E tests must exercise the real UI: click buttons, fill inputs, verify results
- Each E2E spec must cover the happy path of every Scenario in the corresponding feature
- Use `_electron.launch()` to start the app, interact via `page.locator()`, assert via `expect()`
- E2E tests must be independent (each test cleans up after itself)

## When Extending This Codebase
1. Read existing code first
2. Follow existing patterns
3. Add tests for new code
4. Run `npm run validate` before committing
