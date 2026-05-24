# Project timeline

Rough Kanban-style tracking. Items are ordered roughly by start date.

## Week 1 - Setup & exploration
- [x] Read the subject and split it into chunks.
- [x] Install pygame, set up venv.
- [x] Get the assigned A-Maze-ing package and read its source.
- [x] First playable prototype: empty maze, pac-man moving with arrows.
- [x] Decide on project layout (src/ui, src/models, src/maze, src/utils).

## Week 2 - Maze + entities
- [x] Wrap A-Maze-ing into an adapter so the rest of the code uses our own
      grid format (1=wall, 2=corridor, 3=super-pacgum, 4=spawn).
- [x] Player movement with grid alignment / direction queueing.
- [x] Ghosts with BFS pathfinding.
- [x] Pacgums + super-pacgums collisions.

## Week 3 - Game loop
- [x] Lives, score, level progression.
- [x] Scatter/chase mode timer.
- [x] Frightened mode + ghost respawn timer.
- [x] Fruit bonus (cherry, strawberry, ...).
- [x] Death animation.

## Week 4 - Menus, config, highscores
- [x] Config file loader (JSON + `#` comments + defaults).
- [x] Main menu (start / highscores / instructions / exit).
- [x] Pause menu.
- [x] Game over + Victory screens with name input.
- [x] Persistent highscores (top 10).
- [x] HUD with time / lives / score / level.
- [x] Cheat mode (F1-F5) for the peer review.

## Week 5 - Wrap-up
- [x] Polish error handling so no Python traceback ever leaks.
- [x] Write the README in English.
- [x] Write project management docs.
- [x] Packaging spec for itch.io.

## Things that took longer than expected
- BFS pathfinding for the ghosts was OK, but turning the grid coordinates
  into smooth sub-pixel movement took two evenings.
- The corner detection for the wall textures (mask 0..15) had off-by-one
  bugs around the edges of the maze.
