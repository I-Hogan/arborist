# Backgammon Rules Notes

## Board orientation (used by this project)
- Points are numbered 1-24 from White's home board to Black's home board.
- White moves from point 24 down to point 1 (descending).
- Black moves from point 1 up to point 24 (ascending).
- White home board: points 1-6. Black home board: points 19-24.
- The bar holds hit checkers; checkers must re-enter from the bar before any others move.

## Starting position (standard)
- White: 2 on point 24, 5 on point 13, 3 on point 8, 5 on point 6.
- Black: 2 on point 1, 5 on point 12, 3 on point 17, 5 on point 19.

## Movement + blocking
- Each die represents a separate move of that many points.
- A point occupied by two or more opposing checkers is blocked.
- Landing on a blot (single opposing checker) hits it and sends it to the bar.

## Dice rules
- Two dice are rolled each turn.
- If doubles, the player has four moves of that value.
- A player must use as many dice as possible.
- If only one die can be played, the higher die must be used.

## Entering from the bar
- White re-enters on points 24-19: die 1 -> point 24, die 6 -> point 19.
- Black re-enters on points 1-6: die 1 -> point 1, die 6 -> point 6.
- A checker may only enter if the destination point is not blocked.

## Bearing off
- A player may bear off only if all checkers are in the home board.
- Exact rolls bear off from the matching point.
- If a roll is higher than needed, it may bear off the checker on the highest
  occupied point (closest to bearing off) provided there are no checkers on
  higher points.

## Win condition
- A player wins when all 15 checkers are borne off.
