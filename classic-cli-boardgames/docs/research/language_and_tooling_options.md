# Language and Tooling Options

## Languages Considered

### Python
- Pros: Fast iteration, strong standard library, easy CLI scripting, rich
  ecosystem for testing and linting.
- Cons: Slower runtime than compiled languages; large projects need structure
  discipline.
- Fit: Excellent for turn-based game logic and CLI UX; easy to maintain.

### Node.js (JavaScript/TypeScript)
- Pros: Great CLI ecosystem, easy distribution with npm, async tooling.
- Cons: More boilerplate for game state modeling; TypeScript adds build steps.
- Fit: Viable, but adds packaging complexity for a small CLI.

### Go
- Pros: Single binary distribution, strong performance.
- Cons: Slower iteration, more verbose for AI heuristics and tests.
- Fit: Overkill for the initial MVP.

### Decision
Use Python as the primary language for readability, fast iteration, and
straightforward CLI integration.

## CLI and UI Options Considered

### Standard Library (print/input)
- Pros: Zero dependencies, simple to reason about.
- Cons: Limited styling and navigation affordances.

### Rich
- Pros: Clean table/board rendering, colors, readable formatting.
- Cons: Adds a dependency and some API surface area.

### Typer/Click
- Pros: Great command parsing, help text, options.
- Cons: More suited to argument-driven CLI than menu-driven flows.

### Decision
Start with standard library input and add Rich for board rendering to achieve
user-friendly visuals without a heavy framework.

## Testing and Code Quality Tooling

### pytest
- Pros: Simple fixtures, great ecosystem.
- Cons: Additional dependency.
- Decision: Use pytest for unit and CLI integration tests.

### Ruff
- Pros: Very fast linting + formatting, minimal config.
- Cons: Newer tool; occasional rule differences from legacy linters.
- Decision: Use Ruff for formatting and linting.

### mypy
- Pros: Catches type errors early.
- Cons: Overhead if added too soon.
- Decision: Optional; introduce after core modules stabilize.

## Versioning Note
All dependencies should be installed at the latest stable versions available at
setup time to meet security and maintenance goals.
