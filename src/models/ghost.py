from collections import deque
from random import choice, randint

import pygame

from src.models.entity import Direction, Entity


class Ghost(Entity):
    """One of the four ghosts.

    Uses BFS pathfinding to chase the player, with per-colour targeting
    rules borrowed from the original arcade Pac-Man.
    """

    def __init__(self, ghost_id: int, color: str,
                 position: tuple[int, int]) -> None:
        """Initialise the ghost at the given grid corner.

        Args:
            ghost_id: Identifier between 1 and 4.
            color: Colour key driving both behaviour and sprite selection.
            position: ``(x, y)`` grid position to spawn at.
        """
        self.id = ghost_id
        self.color = color
        self.nb_frames = 3
        self.frame = 0
        self.anim_frame = 0.0
        self.x = float(position[0])
        self.y = float(position[1])
        self.is_chased = False
        self.flashes = False
        self.respawn_timer = 0
        self.expression = randint(0, 7)
        self.speed = 0.04
        self.direction = Direction.RIGHT
        self.start_chase = 0.0

    @property
    def position(self) -> tuple[float, float]:
        """Return the current ``(x, y)`` grid position."""
        return (self.x, self.y)

    def _get_neighbors(self, x: int, y: int, grid: list[list[int]],
                       other_ghosts_pos: list[tuple[int, int]] | None = None
                       ) -> list[tuple[int, int]]:
        """Return the walkable neighbours of ``(x, y)`` (with grid wrap)."""
        neighbors: list[tuple[int, int]] = []
        h, w = len(grid), len(grid[0])
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = (x + dx) % w, (y + dy) % h
            if grid[ny][nx] != 1:
                neighbors.append((nx, ny))
        return neighbors

    def find_path(self, start: tuple[int, int], target: tuple[int, int],
                  grid: list[list[int]],
                  other_ghosts_pos: list[tuple[int, int]] | None = None
                  ) -> list[tuple[int, int]]:
        """Compute a BFS path from ``start`` to ``target``.

        Args:
            start: Source cell.
            target: Destination cell.
            grid: The maze grid (``1`` means wall).
            other_ghosts_pos: Currently unused, kept for future use.

        Returns:
            The list of cells from start to target, empty if unreachable.
        """
        queue: deque[tuple[int, int]] = deque([start])
        visited = {start}
        parent: dict[tuple[int, int], tuple[int, int] | None] = {start: None}

        while queue:
            current = queue.popleft()
            if current == target:
                path: list[tuple[int, int]] = []
                cursor: tuple[int, int] | None = current
                while cursor is not None:
                    path.append(cursor)
                    cursor = parent[cursor]
                return path[::-1]

            for neighbor in self._get_neighbors(current[0], current[1], grid,
                                                other_ghosts_pos):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = current
                    queue.append(neighbor)
        return []

    def _scatter_target(self, w: int, h: int) -> tuple[int, int]:
        """Return the corner this ghost retreats to during scatter mode."""
        if self.color == "red":
            return w - 2, 1
        if self.color == "pink":
            return 1, 1
        if self.color == "yellow":
            return w - 2, h - 2
        if self.color == "orange":
            return 1, h - 2
        return 1, 1

    def _chase_target(self, w: int, h: int,
                      pacman_pos: tuple[float, float],
                      pacman_direction: int) -> tuple[int, int]:
        """Compute the target cell for this ghost while chasing the player."""
        tx, ty = round(pacman_pos[0]), round(pacman_pos[1])
        if self.color == "pink":
            if pacman_direction == Direction.UP:
                ty -= 4
            elif pacman_direction == Direction.DOWN:
                ty += 4
            elif pacman_direction == Direction.LEFT:
                tx -= 4
            elif pacman_direction == Direction.RIGHT:
                tx += 4
        elif self.color == "yellow":
            if pacman_direction == Direction.UP:
                ty += 4
            elif pacman_direction == Direction.DOWN:
                ty -= 4
            elif pacman_direction == Direction.LEFT:
                tx += 4
            elif pacman_direction == Direction.RIGHT:
                tx -= 4
        elif self.color == "orange":
            if (self.x - tx) ** 2 + (self.y - ty) ** 2 < 64:
                tx, ty = 1, h - 2
        tx = max(0, min(tx, w - 1))
        ty = max(0, min(ty, h - 1))
        return tx, ty

    def move(self, grid: list[list[int]], pacman_pos: tuple[float, float],
             pacman_direction: int,
             other_ghosts_pos: list[tuple[int, int]] | None = None,
             scatter: bool = False) -> None:
        """Advance the ghost by one frame.

        Args:
            grid: The maze grid.
            pacman_pos: Current player position.
            pacman_direction: Current player direction.
            other_ghosts_pos: Positions of the other ghosts (for spacing).
            scatter: When True, retreat to the scatter corner.
        """
        cx, cy = round(self.x), round(self.y)
        h, w = len(grid), len(grid[0])

        is_centered_x = abs(self.x - cx) <= self.speed * 0.51
        is_centered_y = abs(self.y - cy) <= self.speed * 0.51

        if is_centered_x and is_centered_y:
            self.x, self.y = float(cx), float(cy)

            if self.is_chased:
                neighbors = self._get_neighbors(cx, cy, grid,
                                                other_ghosts_pos)
                if not neighbors:
                    neighbors = self._get_neighbors(cx, cy, grid)
                if neighbors:
                    best = max(neighbors, key=lambda n: (
                        (n[0] - pacman_pos[0]) ** 2
                        + (n[1] - pacman_pos[1]) ** 2
                    ))
                    self._set_direction(best, cx, cy)
            elif scatter:
                tx, ty = self._scatter_target(w, h)
                path = self.find_path((cx, cy), (tx, ty), grid,
                                      other_ghosts_pos)
                if len(path) > 1:
                    self._set_direction(path[1], cx, cy)
                else:
                    neighbors = self._get_neighbors(cx, cy, grid,
                                                    other_ghosts_pos)
                    if not neighbors:
                        neighbors = self._get_neighbors(cx, cy, grid)
                    if neighbors:
                        self._set_direction(choice(neighbors), cx, cy)
            else:
                tx, ty = self._chase_target(w, h, pacman_pos, pacman_direction)
                path = self.find_path((cx, cy), (tx, ty), grid,
                                      other_ghosts_pos)
                if len(path) > 1:
                    self._set_direction(path[1], cx, cy)
                else:
                    neighbors = self._get_neighbors(cx, cy, grid,
                                                    other_ghosts_pos)
                    if not neighbors:
                        neighbors = self._get_neighbors(cx, cy, grid)
                    if neighbors:
                        self._set_direction(choice(neighbors), cx, cy)

        next_x, next_y = self.x, self.y
        if self.direction == Direction.UP:
            next_y -= self.speed
        elif self.direction == Direction.DOWN:
            next_y += self.speed
        elif self.direction == Direction.LEFT:
            next_x -= self.speed
        elif self.direction == Direction.RIGHT:
            next_x += self.speed

        next_x %= w
        next_y %= h

        acx, acy = cx, cy
        if self.direction == Direction.UP:
            acy = (acy - 1) % h
        elif self.direction == Direction.DOWN:
            acy = (acy + 1) % h
        elif self.direction == Direction.LEFT:
            acx = (acx - 1) % w
        elif self.direction == Direction.RIGHT:
            acx = (acx + 1) % w

        if grid[acy][acx] == 1:
            if self.direction == Direction.RIGHT and next_x > cx:
                next_x = float(cx)
            elif self.direction == Direction.LEFT and next_x < cx:
                next_x = float(cx)
            elif self.direction == Direction.DOWN and next_y > cy:
                next_y = float(cy)
            elif self.direction == Direction.UP and next_y < cy:
                next_y = float(cy)

        self.x, self.y = next_x, next_y

    def _set_direction(self, next_node: tuple[int, int], cx: int,
                       cy: int) -> None:
        """Pick the direction that gets us closest to ``next_node``."""
        dx = next_node[0] - cx
        dy = next_node[1] - cy
        if dx > 1:
            self.direction = Direction.LEFT
        elif dx < -1:
            self.direction = Direction.RIGHT
        elif dx > 0:
            self.direction = Direction.RIGHT
        elif dx < 0:
            self.direction = Direction.LEFT
        elif dy > 0:
            self.direction = Direction.DOWN
        elif dy < 0:
            self.direction = Direction.UP

    def get_sprite(self,
                   spritesheet: pygame.surface.Surface
                   ) -> pygame.surface.Surface:
        """Return the ghost sprite for the current frame and state.

        Raises:
            ValueError: When ``self.color`` is unknown.
        """
        color_map = {
            "red":    (0, 0),
            "blue":   (0, 32),
            "pink":   (0, 64),
            "orange": (0, 96),
            "mauve":  (0, 128),
            "yellow": (0, 160),
            "green":  (0, 192),
            "grey":   (0, 224),
        }
        if self.color not in color_map:
            raise ValueError(f"Unknown ghost color: {self.color}")

        if self.respawn_timer > 0:
            return pygame.Surface((32, 32), pygame.SRCALPHA)

        if not self.is_chased:
            x = color_map[self.color][0] + (self.frame * 32)
            y = color_map[self.color][1]
        else:
            x = 0 + (self.frame * 32)
            y = 256 if not self.flashes or self.frame >= 1 else 288

        rect = pygame.Rect(x, y, 32, 32)
        image = spritesheet.subsurface(rect).copy()

        if not self.flashes and not self.is_chased:
            face_rect = pygame.Rect(self.expression * 16, 320, 16, 16)
            image.blit(spritesheet.subsurface(face_rect), (8, 8))
        return image

    def update(self) -> None:
        """Advance the animation frame counters by one tick."""
        self.anim_frame += 0.1
        self.frame = int(self.anim_frame) % self.nb_frames

    def __str__(self) -> str:
        """Return a debug-friendly representation of the ghost."""
        return (f"Ghost(id={self.id}, color={self.color}, "
                f"position={self.position})")
