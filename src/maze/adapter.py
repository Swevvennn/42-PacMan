import os
from typing import List

from libs.mazegenerator.mazegenerator import MazeGenerator


class MazeGenerationError(RuntimeError):
    """Raised when the underlying maze generator fails."""


class MazeAdapter:
    """Wrap A-Maze-ing and expose our own grid format.

    Cell values used by the rest of the project:

    * ``0`` = empty corridor (no pacgum)
    * ``1`` = wall
    * ``2`` = pacgum
    * ``3`` = super-pacgum
    * ``4`` = pacman spawn
    """

    def __init__(self, width: int, height: int, seed: int = 42) -> None:
        """Generate the underlying maze and translate it to our grid.

        Args:
            width: Number of cells along the X axis.
            height: Number of cells along the Y axis.
            seed: Random seed forwarded to the generator.

        Raises:
            MazeGenerationError: When the generator raises any exception.
        """
        self.width = width
        self.height = height
        self.grid: List[List[int]] = []

        try:
            self._generator = MazeGenerator(
                (width, height),
                False,
                (1, 1),
                (width, height),
                seed,
            )
        except Exception as e:
            raise MazeGenerationError(
                f"maze generator failed: {e}"
            ) from e

        self.generate_grid()

    def generate_grid(self) -> List[List[int]]:
        """Translate the bitmask maze into our grid format."""
        adj_h = self.height * 2 + 1
        adj_w = self.width * 2 + 1
        self.grid = [[1 for _ in range(adj_w)] for _ in range(adj_h)]
        raw_maze = self._generator._maze

        for y in range(self.height):
            for x in range(self.width):
                val = raw_maze[y][x]
                cy = y * 2 + 1
                cx = x * 2 + 1

                if val == 15:
                    self.grid[cy][cx] = 0
                    continue

                self.grid[cy][cx] = 2

                if not (val & 1):
                    self.grid[cy - 1][cx] = 2
                if not (val & 2):
                    self.grid[cy][cx + 1] = 2
                if not (val & 4):
                    self.grid[cy + 1][cx] = 2
                if not (val & 8):
                    self.grid[cy][cx - 1] = 2

        corners = [
            (1, 1),
            (1, adj_w - 2),
            (adj_h - 2, 1),
            (adj_h - 2, adj_w - 2),
        ]
        for ry, rx in corners:
            self.grid[ry][rx] = 3

        mid_y = (self.height // 2) * 2 + 1
        mid_x = (self.width // 2) * 2 + 1 if self.width % 2 == 1 \
            else (self.width // 2) * 2 - 1
        self.grid[mid_y][mid_x] = 4

        return self.grid

    def _get_char(self, val: int) -> str:
        """Map a grid value to a single printable character."""
        if val == 1:
            return "#"
        if val == 2:
            return "."
        if val == 3:
            return "o"
        if val == 4:
            return "P"
        return " "

    def render(self) -> None:
        """Print the maze in the terminal (debugging helper only)."""
        os.system("cls" if os.name == "nt" else "clear")
        reset = "\033[0m"
        colors = {
            4: "\033[92m",
            1: "\033[94m",
            2: "\033[97m",
            3: "\033[93m",
        }
        for row in self.grid:
            line = ""
            for cell in row:
                color = colors.get(cell, reset)
                line += f"{color}{self._get_char(cell)}{reset}"
            print(line)
