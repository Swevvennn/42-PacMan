import pygame

from src.models.entity import Entity


class Object(Entity):
    """Edible item on the maze: a pacgum, a super-pacgum or a level fruit."""

    sprites_dict = {
        "cherry":       pygame.Rect(0, 0, 16, 16),
        "strawberry":   pygame.Rect(16, 0, 16, 16),
        "orange":       pygame.Rect(32, 0, 16, 16),
        "apple":        pygame.Rect(48, 0, 16, 16),
        "melon":        pygame.Rect(64, 0, 16, 16),
        "galaxian":     pygame.Rect(80, 0, 16, 16),
        "bell":         pygame.Rect(96, 0, 16, 16),
        "key":          pygame.Rect(112, 0, 16, 16),
        "pacgum":       pygame.Rect(0, 16, 16, 16),
        "super_pacgum": pygame.Rect(16, 16, 16, 16),
    }

    def __init__(self, name: str, position: tuple[int, int]) -> None:
        """Build the object at the given grid position.

        Args:
            name: Key used to look the sprite up in ``sprites_dict``.
            position: ``(x, y)`` grid position.
        """
        self.name = name
        self._position = position
        self.is_visible = True
        self.score_value = 0

    @property
    def position(self) -> tuple[float, float]:
        """Return the grid position as floats for the renderer."""
        return (float(self._position[0]), float(self._position[1]))

    def get_sprite(self,
                   spritesheet: pygame.surface.Surface
                   ) -> pygame.surface.Surface:
        """Return the 16x16 sprite that matches this object.

        Args:
            spritesheet: The items spritesheet to slice from.

        Returns:
            A new surface containing the sprite, or a fully transparent
            surface when the object is currently invisible.

        Raises:
            ValueError: If the object name is not registered.
        """
        if self.name not in Object.sprites_dict:
            raise ValueError(f"Unknown object sprite: {self.name}")
        if not self.is_visible:
            return pygame.Surface((16, 16), pygame.SRCALPHA)
        return spritesheet.subsurface(Object.sprites_dict[self.name]).copy()

    def update(self) -> None:
        """No-op kept to satisfy the ``Entity`` interface."""
        pass

    def __str__(self) -> str:
        """Return a debug-friendly representation of the object."""
        return f"Object(name={self.name}, position={self.position})"
