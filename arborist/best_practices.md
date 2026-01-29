# A general guide to best-practices.

## Code quality

For code quality, we want to automate as much as possible. Priority is:

1. Automated tools that fix code quality (i.e. isort, black).
2. Automated tools that detect issues with code quality (i.e. pylint, flake8)
3. Listed checks in the code review instructions.

If any automated code quality tool takes more than a minute, 
find some way to fix it, update the config, replace it, or remove it.

## Testing

There are two main testing paradigms that need to be established:

1. Unit tests and fast integration tests.
2. Comprehensive integrations tests.

### Unit and fast integration tests

These should be set up at the start of the project. None of these tests 
should take more than 1 second to run. Find a way to parallelize them.

### Integration tests

These should look as close to what the user does as possible.
- Try to make them use the same interface or a very close proxy.
  - i.e. if there is a GUI, the test should perform clicks on the GUI. 
  If the project uses a CLI, the tests should send messages there. etc.

Inegration tests should be set up once the interface has been built.
