from abc import ABC, abstractmethod

import pygame


class Direction:
    """Direction codes shared across the project.

    Attributes:
        UP: Move upward (decrease Y).
        RIGHT: Move rightward (increase X).
        DOWN: Move downward (increase Y).
        LEFT: Move leftward (decrease X).
    """

    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


class Entity(ABC):
    """Common interface implemented by everything drawn on the maze."""

    @property
    @abstractmethod
    def position(self) -> tuple[float, float]:
        """Return the current grid position as floats."""
        raise NotImplementedError()

    @abstractmethod
    def update(self) -> None:
        """Advance internal animation timers by one tick."""
        raise NotImplementedError()

    @abstractmethod
    def __str__(self) -> str:
        """Return a short, human-friendly representation of the entity."""
        raise NotImplementedError()

    @abstractmethod
    def get_sprite(self,
                   spritesheet: pygame.surface.Surface
                   ) -> pygame.surface.Surface:
        """Return the sprite to blit for the current frame."""
        raise NotImplementedError()


class ScorePopup:
    """Floating ``"+100"`` text that briefly pops over the maze."""

    def __init__(self, text: str, position: tuple[float, float],
                 color: tuple[int, int, int]) -> None:
        """Store the popup data and start its 60-frame countdown.

        Args:
            text: Score string to display.
            position: Grid position of the popup.
            color: RGB triple used when rendering the text.
        """
        self.text = text
        self.position = position
        self.timer = 60
        self.color = color
