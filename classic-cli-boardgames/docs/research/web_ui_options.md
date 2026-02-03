# Web UI Delivery Options

## Options Considered

### Python standard library (http.server + BaseHTTPRequestHandler)
- Pros: No new dependencies, easy local-only server, simple packaging.
- Cons: Manual routing, no templating or static pipeline.
- Fit: Good for a lightweight local GUI with a small API surface.

### Flask
- Pros: Simple routing, familiar ecosystem, easy templating.
- Cons: Adds a dependency and version management for a small app.
- Fit: Reasonable, but heavier than needed for a local-only UI.

### FastAPI/Starlette
- Pros: Typed request models, modern async tooling.
- Cons: Larger dependency graph, more setup for static assets.
- Fit: Better for larger services than a single-machine GUI.

## Decision
Use the Python standard library HTTP server with a small JSON API and static
HTML/CSS/JS assets. This keeps the project dependency-free while still enabling
a clean, modern local GUI. If future requirements grow (auth, multiplayer,
persistence), revisit a lightweight framework.
