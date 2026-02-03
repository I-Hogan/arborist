# Instructions for reviewing changes

Code review instructions specific to this project. General code review guidelines 
should live in the core `arborist/` project. 

## Code Review Checklist

- Verify CLI navigation flows: main menu -> game -> back/restart/quit all behave correctly.
- Confirm help text is accurate for each game and matches input expectations.
- Check board rendering for alignment and coordinate labels in an 80-column terminal.
- Validate input errors are actionable and do not crash the process.
- Ensure AI determinism when a seed is provided and difficulty caps are respected.
- Manually spot-check rule enforcement for each game (legal moves, terminal states).
- Confirm randomness sources are centralized and seedable where required.
- Review docs/spec updates for consistency with implemented behavior.

## Code Review Notes
