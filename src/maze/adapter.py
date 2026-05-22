import random
from typing import List
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from libs.mazegenerator.mazegenerator import MazeGenerator

class MazeAdapter:
    def __init__(self, width: int, height: int, seed: int = 42) -> None:
        self._generator = MazeGenerator(
            (width, height),
            False,
            (1, 1),
            (width, height),
            seed
        )
        self.width = width
        self.height = height
        self.grid: List[List[int]] = []
        self.generate_grid()

    def generate_grid(self) -> List[List[int]]:
        adj_h = self.height * 2 + 1
        adj_w = self.width * 2 + 1
        self.grid = [[1 for _ in range(adj_w)] for _ in range(adj_h)]
        raw_maze = self._generator._maze

        for y in range(self.height):
            for x in range(self.width):
                val = raw_maze[y][x]
                cy = y * 2 + 1
                cx = x * 2 + 1

                self.grid[cy][cx] = 2

                if not (val & 1): self.grid[cy - 1][cx] = 2
                if not (val & 2): self.grid[cy][cx + 1] = 2
                if not (val & 4): self.grid[cy + 1][cx] = 2
                if not (val & 8): self.grid[cy][cx - 1] = 2

        corners = [
            (1, 1),
            (1, adj_w - 2),
            (adj_h - 2, 1),
            (adj_h - 2, adj_w - 2)
        ]
        for ry, rx in corners:
            self.grid[ry][rx] = 3

        mid_y = (self.height // 2) * 2 + 1
        mid_x = (self.width // 2) * 2 + 1
        self.grid[mid_y][mid_x] = 4

        return self.grid

    def _get_char(self, val: int) -> str:
        if val == 1: return "#"
        if val == 2: return "."
        if val == 3: return "o"
        if val == 4: return "P"
        return " "

    def render(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")
        reset = "\033[0m"
        colors = {
            4: "\033[92m",
            1: "\033[94m",
            2: "\033[97m",
            3: "\033[93m"
        }
        for row in self.grid:
            line = ""
            for cell in row:
                color = colors.get(cell, reset)
                line += f"{color}{self._get_char(cell)}{reset}"
            print(line)

if __name__ == '__main__':
    new_maze = MazeAdapter(10, 10)
    new_maze.render()
