import pygame

from src.models.entity import Direction, Entity


class PacMan(Entity):
    """The player. Moves smoothly on the grid with sub-pixel precision."""

    def __init__(self, position: tuple[int, int]) -> None:
        """Initialise the player at the given grid position.

        Args:
            position: ``(x, y)`` grid position to spawn at.
        """
        self.nb_frames = 3
        self.frame = 0
        self.anim_frame = 0.0
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.x = float(position[0])
        self.y = float(position[1])
        self.speed = 0.06
        self.is_alive = True

    @property
    def position(self) -> tuple[float, float]:
        """Return the current ``(x, y)`` grid position."""
        return (self.x, self.y)

    def die(self) -> None:
        """Start the death animation."""
        self.is_alive = False
        self.nb_frames = 7
        self.anim_frame = 0.0
        self.frame = 0

    def _get_next_pos(self, d: int, grid_width: int, grid_height: int,
                      cx: int, cy: int) -> tuple[int, int]:
        """Return ``(cx, cy)`` shifted by one cell in direction ``d``."""
        cx %= grid_width
        cy %= grid_height
        if d == Direction.UP:
            cy -= 1
        elif d == Direction.DOWN:
            cy += 1
        elif d == Direction.LEFT:
            cx -= 1
        elif d == Direction.RIGHT:
            cx += 1
        return cx % grid_width, cy % grid_height

    def move(self, grid: list[list[int]]) -> None:
        """Advance the player by one frame using its current speed.

        Args:
            grid: The maze grid (cell value ``1`` means wall).
        """
        if not self.is_alive:
            return
        h, w = len(grid), len(grid[0])

        cx, cy = round(self.x), round(self.y)
        is_centered_x = abs(self.x - cx) <= self.speed * 0.51
        is_centered_y = abs(self.y - cy) <= self.speed * 0.51

        if self.next_direction != self.direction:
            if is_centered_x and is_centered_y:
                nx, ny = self._get_next_pos(self.next_direction, w, h, cx, cy)
                if grid[ny][nx] != 1:
                    self.x, self.y = float(cx), float(cy)
                    self.direction = self.next_direction

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

        ahead_x, ahead_y = self._get_next_pos(self.direction, w, h, cx, cy)
        if grid[ahead_y][ahead_x] == 1:
            if self.direction == Direction.RIGHT and next_x > cx:
                next_x = float(cx)
            elif self.direction == Direction.LEFT and next_x < cx:
                next_x = float(cx)
            elif self.direction == Direction.DOWN and next_y > cy:
                next_y = float(cy)
            elif self.direction == Direction.UP and next_y < cy:
                next_y = float(cy)

        self.x, self.y = next_x, next_y

    def get_sprite(self,
                   spritesheet: pygame.surface.Surface
                   ) -> pygame.surface.Surface:
        """Return the player sprite for the current frame and direction."""
        x = self.frame * 32
        y = 0
        if not self.is_alive:
            y = 32
            if self.frame >= 4:
                y = 64
                x = (self.frame - 4) * 32

        rect = pygame.Rect(x, y, 32, 32)
        image = spritesheet.subsurface(rect).copy()

        rotation_angles = {
            Direction.RIGHT: 0,
            Direction.UP: 90,
            Direction.LEFT: 180,
            Direction.DOWN: 270,
        }
        angle = rotation_angles.get(self.direction, 0)
        if angle != 0:
            image = pygame.transform.rotate(image, angle)
        return image

    def update(self) -> None:
        """Advance the animation frame counters by one tick."""
        self.anim_frame += 0.1
        if self.is_alive:
            self.frame = int(self.anim_frame) % self.nb_frames
        else:
            self.frame = min(int(self.anim_frame), self.nb_frames - 1)

    def __str__(self) -> str:
        """Return a debug-friendly representation of the player."""
        return f"PacMan(position={self.position})"
