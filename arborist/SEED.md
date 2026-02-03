Arborist is an automated project gardener that continuously improves many
projects in a workspace by reading their high-level intent and task lists,
then executing focused work cycles.

It should be simple to run as a long-lived local service that:
- discovers projects in a root directory,
- follows each project's AGENTS.md and SEED.md guidance,
- works through tasks/todos/requests one at a time,
- avoids destructive changes,
- records feedback and keeps work organized.

The tool itself should be small, reliable, and easy to adapt so it can serve
as the backbone for a personal multi-project automation workflow.
