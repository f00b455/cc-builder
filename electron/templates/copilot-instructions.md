# Electron TypeScript Project

Electron 28+ app with TypeScript strict mode, esbuild bundler, Jest/Cucumber/Playwright testing.

## Structure
- `src/main.ts` — main process (Node.js)
- `src/preload.ts` — contextBridge IPC
- `src/renderer/` — browser context (esbuild-bundled, NO Node.js APIs)
- `src/domain/` — business logic with `*.test.ts`
- `src/ipc/` — IPC handlers with `*.test.ts`
- `features/*.feature` + `features/steps/*.ts` — BDD
- `e2e/*.spec.ts` — Playwright E2E tests

## Rules
- `contextIsolation: true`, `nodeIntegration: false` — always
- Main process: `import { randomUUID } from 'crypto'` — never use global `crypto`
- No `prompt()`, `alert()`, `confirm()` — ESLint will fail
- No `any` types, all files `.ts`, strict null checks
- Every npm import must be in `package.json` first
- Prefer Node.js built-ins over external packages
- Pure functions, single responsibility, max 20-30 lines
- Early returns, named constants, prefer `const`

## Testing
- 80% coverage minimum (Jest)
- Every `.feature` needs a matching `e2e/*.spec.ts`
- E2E tests use `_electron.launch()` + `page.locator()` + `expect()`

## Commands
- `npm run build` — build
- `npm run test` — unit tests
- `npm run lint` — ESLint
- `npm run cucumber` — BDD
- `npm run test:e2e` — E2E
- `npm run validate` — all checks
