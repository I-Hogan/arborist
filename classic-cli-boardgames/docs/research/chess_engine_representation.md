# Chess engine representation options

## Board representation

### Option A: Bitboards
- **Pros:** Very fast move generation, compact state, common in high-performance engines.
- **Cons:** More complex to implement and debug, especially for CLI-first project.

### Option B: 8x8 grid of piece objects (lists/tuples)
- **Pros:** Straightforward, readable, easy to render, simple to reason about.
- **Cons:** Slower than bitboards, but adequate for CLI play and intermediate AI.

### Decision
Choose **Option B (8x8 grid)** to keep the rules engine simple and maintainable.

## Move representation

### Option A: Encoded integers
- **Pros:** Compact, fast comparisons.
- **Cons:** Harder to inspect while debugging, less readable.

### Option B: Dataclass with explicit fields
- **Pros:** Readable, explicit (from/to, promotion, special flags), easier for CLI parsing.
- **Cons:** Slightly more overhead per move.

### Decision
Choose **Option B (dataclass)** for clarity and maintainability.

## State tracking

### Option A: Mutable state
- **Pros:** Faster updates.
- **Cons:** Easier to accidentally mutate in search/analysis.

### Option B: Immutable state (frozen dataclass, copy-on-apply)
- **Pros:** Safer for move generation and future AI search.
- **Cons:** More allocations.

### Decision
Use **immutable state** with copy-on-apply for safety; performance is acceptable for CLI.
