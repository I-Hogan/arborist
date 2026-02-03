# A general guide to best-practices.

## Choosing languages, frameworks, and tools

Think deeply about which languages, frameworks, and tools will be best for 
the long-term health of the project.
- Keep it simple: A smaller, more basic toolset will be easier to maintain.
- Language speed vs. usability:
  - Only use really fast languages when speed is necessary.
  - Library support and ease of human coding are also important.

Add files to the research explaining the options you considered for the project, 
the benefits and drawbacks of each, and why you ultimately chose what you did.

Always search for and use the newest versions. This is important for security.

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

Ideally tests are located close to the files they are testing (not in) rather 
than being in a separate tests/ directory.

### Integration tests

These should look as close to what the user does as possible.
- Try to make them use the same interface or a very close proxy.
  - i.e. if there is a GUI, the test should perform clicks on the GUI. 
  If the project uses a CLI, the tests should send messages there. etc.

Integration tests should be set up once the interface has been built.

## Development

- If you come across a bug, if it is small fix it, if it is large log it in the backlog.

## Documentation

- Each file should have an explanation of what it does at the top.
- Each function/class/datasctructure/etc. should have a description of what it does.
  - Co-located documentation.
- Complex or unintuitive individual lines of code should have comments to help 
developers understand what is going on.