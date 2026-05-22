import pygame
from src.models.entity import Entity

class Object(Entity):
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
        "super_pacgum": pygame.Rect(16, 16, 16, 16)
    }

    def __init__(self, name: str, position: tuple[int, int]) -> None:
        self.name = name
        self._position = position
        self.is_visible = True

    @property
    def position(self) -> tuple[float, float]:
        return (float(self._position[0]), float(self._position[1]))

    def get_sprite(self, spritesheet: pygame.Surface) -> pygame.Surface:
        if self.name in Object.sprites_dict:
            if not self.is_visible:
                return pygame.Surface((16, 16), pygame.SRCALPHA)
            return spritesheet.subsurface(Object.sprites_dict[self.name]).copy()
        else:
            raise ValueError(f"Unknown object sprite: {self.name}")

    def update(self) -> None:
        pass

    def __str__(self) -> str:
        return f"Object(name={self.name}, position={self.position})"
