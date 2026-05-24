# Risk analysis

| # | Risk                                                       | Likelihood | Impact | Mitigation                                                                                              | Status     |
|---|------------------------------------------------------------|------------|--------|---------------------------------------------------------------------------------------------------------|------------|
| 1 | A-Maze-ing package not delivered on time / broken          | low        | high   | Wrote a thin adapter so the game depends only on our own grid format. Switching package = one file.     | mitigated  |
| 2 | A-Maze-ing fails on a malformed input                      | low        | high   | Errors raised by the generator are caught in the adapter and re-raised as `MazeGenerationError`.        | mitigated  |
| 3 | Ghost pathfinding too slow on large mazes                  | medium     | medium | BFS is bounded by maze cells (small numbers). If it becomes an issue we can fall back to greedy moves.  | mitigated  |
| 4 | User provides a broken config file                         | high       | low    | Config loader falls back to safe defaults and prints a clear message, never a traceback.                | mitigated  |
| 5 | pygame not installed / display unavailable on review PC    | medium     | high   | Wrapped pygame init in try/except; clear error message. `make install` pulls everything.                | mitigated  |
| 6 | Highscore file corrupted by user / partial write           | low        | medium | Loader catches JSON errors and starts from an empty list. Write is atomic (open + dump).                | mitigated  |
| 7 | Time pressure: not enough time for cheat mode + screens    | medium     | medium | Built cheat mode last, on top of existing flags. Screens reuse the same render helpers.                 | mitigated  |
| 8 | Code does not pass `flake8` / `mypy`                       | medium     | medium | Type hints added incrementally, `make lint` run regularly.                                              | mitigated  |
| 9 | Packaging on itch.io fails at submission                   | low        | high   | packaging_spec.json documents the PyInstaller command, tested locally before submitting.                | open       |
| 10| Peer-review modification request we can't handle quickly   | low        | high   | Code is split in small modules, no big god-class, most asks should fit in one file.                     | mitigated  |
