# Web UI Server Options

This note captures lightweight options for serving a local Arborist web UI and
why the first implementation uses Node's built-in HTTP server.

## Options Considered

- Node.js built-in `http` + static files
  - Pros: zero dependencies, fast startup, easy to ship, matches existing ESM
    scripts, no extra install step.
  - Cons: manual routing and static file handling.
- Express
  - Pros: familiar routing and middleware, lots of examples.
  - Cons: adds dependency surface area and version maintenance for a tiny UI.
- Fastify/Hono
  - Pros: fast and modern; smaller than Express.
  - Cons: still adds dependencies and a learning surface for minimal needs.

## Decision

Use Node's built-in `http` module plus a minimal static file handler. The UI is
small, local-only, and does not need middleware or advanced routing. Keeping the
server dependency-free is consistent with Arborist's lightweight runtime goals.
