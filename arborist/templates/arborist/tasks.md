# A list of tasks that need doing. (Should be empty except for the title when there are not tasks remaining)

1. Come up with a high level plan for the project and write it out in 
`arborist/spec.md`. Brainstorm which language(s)/framework(s) you will need to start 
the project (include testing and code style frameworks/strategies). Follow 
`best_practices.md` and fill in those details here as well. Update the index 
sections of the readmes.
2. Based on the languages and frameworks used set up all the automatic style checks that 
will be run in this project. Include a type checking tool if necessary. See `best_practices.md`.
3. Set up the testing framework(s) for this project. See `best_practices.md`. 
Write a small piece of code in each language to ensure tests are running quickly. 
Tests should be run in parallel where possible.
4. Create a unified script called `scripts/pre_commit.sh` which runs all the auto
formatting tools, style checks, compiles if necessary, fast running tests, and
the pre-commit hooks (when `pre-commit` is available). This script needs to run quickly.
5. Add safety pre-commit hooks via `.pre-commit-config.yaml` and ensure
`pre-commit install` is part of the setup flow.
6. Create a `README.md` for the project and a `scripts/setup.sh` script which 
installs any requirements and get the project ready to run (any database migrations, 
builds, etc.). Make sure `scripts/setup.sh` installs the pre-commit hook when
`pre-commit` is available.
7. Populate this project's `code_review.md` with style and functional checks 
that cannot be automated. Use `best_practices.md` and industry standards for what to add.
8. Write small test functions in each language the project is planning to use as well
as a basic unit test. Run `scripts/pre_commit.sh` to make sure you can run the full test suite,
installing any needed tooling or dependencies and debugging any issues until it runs
cleanly. It is vital you can run this.
9. Break down all the work required to make the Minimum Viable Prototype (MVP) into 
manageable pieces. Add these to the bottom of `todo.md` as work items.
