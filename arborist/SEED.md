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

It should also have a minimal, modern, sleek, fast, web-based UI. 
While the server is running you can connect locally on port 7788. 
A user should be able to do the following from the website:
- control which projects are enabled for arborist to work on and which is 
currently selected for providing feedback, saving, etc.
- make feedback items
  - arborist responds with a summary of what it did when done.
  - These can be cleared, or the user can give a follow up prompt.
  - Feedback not added until user selects a submit option.
- save the state of the selected project with the press of a button
  - should create a new commit with all current changes.
  - push that commit to main.
  - a special case for the arborist project itself where it should
  commit changes to the root project.