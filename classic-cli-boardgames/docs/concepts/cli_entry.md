# CLI Entry Flow

## Goals
- Provide a single, friendly entry point for selecting and launching games.
- Offer consistent navigation commands across menu and gameplay contexts.
- Keep routing logic separate from game logic so new games plug in cleanly.

## Flow Overview
1. Entry script starts and loads the main menu.
2. Menu lists available games with numeric choices.
3. User can:
   - choose a game by number or name
   - type a navigation command (help, back, restart, quit)
4. Selecting a game transitions into that game's loop.
5. In-game loop accepts moves plus the same navigation commands.
6. `back` returns to the main menu; `restart` resets the current game.

## Command Handling
- Input is trimmed and case-insensitive.
- Navigation commands are recognized before game-specific parsing.
- Invalid inputs show a short error plus a hint to type `help`.

## Routing
- A registry maps game keys to callable launchers.
- Menu selection uses this registry to dispatch to a game loop.
- Games not yet implemented may return a placeholder message and then
  return to the menu.

## Terminal States
- `quit` always exits the program cleanly.
- `back` is only meaningful from within a game loop.
- `restart` is only meaningful while in a game loop.
