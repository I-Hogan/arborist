# Web UI Shell Plan

This document outlines the plan for adding a lightweight web UI shell to
Arborist following the project best practices.

## Plan

- Add a dependency-free Node.js server script that serves static assets and
  listens on port 7788 by default (configurable by env var).
- Create a small static UI shell (HTML/CSS/JS) that loads in the browser and
  renders placeholder sections for the upcoming controls.
- Document how to run the web UI in the main README.
- Add fast unit tests only if new logic becomes complex; otherwise keep the
  implementation minimal and covered by a quick manual smoke test.
- Run `scripts/pre_commit.sh` and address any issues.
