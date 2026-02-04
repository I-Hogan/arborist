# This file outlines how to do initial setup of a new project

## Case 1: Blank project with only SEED.md

Copy `templates/arborist/.` into the new directory under `arborist/`, then copy
`templates/AGENTS.md`, `templates/.pre-commit-config.yaml`, `templates/docs`,
`templates/experiments`, and `templates/scripts`. Ensure the project's
`scripts/setup.sh` installs the pre-commit hook when `pre-commit` is available.
Ensure `scripts/pre_commit.sh` runs the pre-commit hooks when `pre-commit` is available.
This is a general template for any new project. Never modify the
templates unless specifically instructed. All following instructions
should be executed in the new project.

## Case 2: Work-in-progress project missing Arborist files

Ensure the project matches the arborist layout by rearranging and adding any missing
files/directories from `templates/arborist` (under the project
`arborist/` subdirectory), `templates/AGENTS.md`, `templates/.pre-commit-config.yaml`,
`templates/docs`, `templates/experiments`, and `templates/scripts` without
overwriting existing files. Ensure the project's `scripts/setup.sh` installs
the pre-commit hook when `pre-commit` is available. Ensure
`scripts/pre_commit.sh` runs the pre-commit hooks when `pre-commit` is available.
If a file already exists, keep it and do not replace it; only add the missing ones.
This should result in the project having the standard Arborist files under
`arborist/` (tasks.md, todo.md, feedback.md, backlog.md, etc.) plus `AGENTS.md`
at the project root while preserving existing work.

Make sure all the steps in the template tasks.md have already been completed 
for the project, i.e. tests and static checks are runnable from the script. 
If `pre-commit` is installed, run `pre-commit install` to enable safety hooks.
