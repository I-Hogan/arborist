# Web UI Framework Decision

This document evaluates framework options for the Arborist web UI and records
why Astro was selected for the migration.

## Options Considered

### Keep the static HTML/CSS/JS shell
- Pros: zero additional dependencies; trivial to serve from the existing Node
  HTTP server.
- Cons: manual templating, harder to maintain as the UI grows, and no build
  pipeline for component reuse.

### Astro
- Pros: optimized for content-driven sites and server-first rendering, with an
  islands architecture that keeps most HTML static while hydrating only the
  interactive pieces. This matches the Arborist UI profile (mostly static
  layout with a few dynamic controls). It supports multiple UI frameworks but
  can also ship plain HTML. It is intended for fast static output.
- Cons: adds a build step and Node version requirements.
- Notes: Astro supports even-numbered Node.js versions with minimums documented
  as v18.20.8, v20.3.0, and v22.0.0. The latest stable release available at the
  time of this decision is Astro 5.17.1.

### Next.js
- Pros: full-stack React framework with built-in optimizations and tooling.
- Cons: more framework surface area than needed for a lightweight local UI, and
  requires committing to React.

### SvelteKit
- Pros: modern framework with good performance characteristics and built-in
  routing and build optimizations.
- Cons: introduces a Svelte-specific stack and more moving pieces than required
  for a mostly static dashboard.

## Decision

Use Astro for the web UI. It provides static-first output with optional
hydration for interactive islands, which aligns with the existing UI that is
mostly static markup plus a small amount of JavaScript for API calls. The
framework keeps output lightweight while making it easier to evolve the layout
as the UI grows.

## Sources
- https://astro.build/
- https://docs.astro.build/en/concepts/islands/
- https://docs.astro.build/en/tutorial/1-setup/1/
- https://newreleases.io/project/github/withastro/astro/release/astro%405.17.1
- https://nextjs.org/docs
- https://svelte.dev/docs/kit
