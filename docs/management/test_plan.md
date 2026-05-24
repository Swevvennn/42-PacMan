# Acceptance test plan

Tests run by hand before each commit. No automated test suite, we relied on
playing the game and checking the behaviour against the subject.

## Launch
- [x] `python3 pac-man.py config.json` opens the main menu.
- [x] `python3 pac-man.py` (no arg) prints usage and exits cleanly.
- [x] `python3 pac-man.py foo.txt` complains that the file must be a `.json`.
- [x] `python3 pac-man.py does_not_exist.json` prints a clear error, no traceback.
- [x] Config with garbage values: clamps to defaults, no traceback.
- [x] Config with `#` comments: parsed fine.

## Menus
- [x] Main menu: Space -> game, H -> highscores, I -> instructions, Esc -> quit.
- [x] Highscores screen lists top 10 entries.
- [x] Instructions screen lists controls.
- [x] Pause (Esc in game): Space resumes, M goes back to main menu.

## Gameplay
- [x] Player moves with arrows and WASD.
- [x] Player cannot walk through walls.
- [x] Eating a pacgum increases the score by the configured amount.
- [x] Eating a super-pacgum makes ghosts edible for ~8 seconds.
- [x] Eating ghosts: 200, 400, 800, 1600 in a row, then resets.
- [x] Getting touched by a normal ghost: -1 life, respawn in the middle.
- [x] Lives = 0 -> Game Over screen with name input.
- [x] All pacgums eaten -> next level.
- [x] Last level cleared -> Victory screen with name input.
- [x] Score and lives carried between levels.
- [x] Time runs out: lose 1 life, level restarts.

## Highscores
- [x] Empty highscore file: game still launches.
- [x] Corrupted highscore file: ignored, starts from empty list.
- [x] Name input: max 10 chars, only alphanumerics and spaces.
- [x] After saving, top 10 is sorted and displayed in main menu.

## Cheat mode
- [x] F1: invincibility on/off.
- [x] F2: skip current level.
- [x] F3: freeze ghosts on/off.
- [x] F4: +1 life.
- [x] F5: player speed boost on/off.

## Bugs found and fixed
- Crash when a fruit was on the player tile on the first frame of a level:
  the fruit check was running before `pm_x, pm_y` got their value.
- Pause used Esc to *quit* the whole app instead of going back to the menu.
- HUD was missing the level timer.
- Lives count was hardcoded to 3 instead of being read from config.
