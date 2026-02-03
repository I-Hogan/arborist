# Tech Stack Research

## Context
Arborist is a CLI automation runner that orchestrates Codex CLI across multiple
projects. The codebase is small, focuses on filesystem operations, and needs to
be portable across developer machines.

## Options Considered
### Language/runtime
- Node.js (ESM)
  - Pros: already used in existing scripts, strong filesystem/process APIs,
    cross-platform, easy distribution.
  - Cons: requires Node/npm installed.
- Python
  - Pros: great scripting ecosystem, common on many machines.
  - Cons: would require a rewrite of existing Node scripts and packaging.

### Formatting/Linting
- Biome
  - Pros: single tool for formatting and linting, fast, auto-fix support.
  - Cons: newer ecosystem compared to ESLint/Prettier.
- ESLint + Prettier
  - Pros: mature ecosystem.
  - Cons: two-tool setup, more configuration.

### Test Runner
- Node built-in test runner (`node --test`)
  - Pros: zero dependency, fast, parallel by default.
  - Cons: fewer bells/whistles than Jest.
- Jest
  - Pros: rich ecosystem.
  - Cons: heavier dependency footprint.

## Decisions
- Use Node.js (ESM) to align with the existing `scripts/arborist.mjs` entry
  point and keep the runtime consistent.
- Use Biome for formatting/linting to keep tooling fast and minimal.
- Use Node's built-in test runner for fast unit tests.

## Version Strategy
- Tooling dependencies are specified with `latest` to ensure the newest
  available versions are installed at setup time.
