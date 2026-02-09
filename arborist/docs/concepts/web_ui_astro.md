# Web UI Astro Migration Plan

This document outlines the plan for migrating the Arborist web UI shell to
Astro while preserving existing behavior.

## Plan
1. Create an Astro project in `web_ui/` with `src/pages/index.astro`, keeping
   the current markup and layout while moving static assets to `public/`.
2. Add Astro tooling to the project `package.json`, using the latest stable
   version identified in research.
3. Update `scripts/web_ui.mjs` to build the Astro site (if needed) and serve
   the generated `dist/` output alongside existing API routes.
4. Keep existing JavaScript behavior by serving `public/app.js` and
   `public/styles.css` without changing the API wiring.
5. Update documentation to describe the new build flow.
6. Run `scripts/pre_commit.sh` and fix any issues.
