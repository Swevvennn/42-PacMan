import pygame
from abc import ABC, abstractmethod

class Direction:
    UP =    0
    RIGHT = 1
    DOWN =  2
    LEFT =  3

class Entity(ABC):
    @property
    @abstractmethod
    def position(self) -> tuple[float, float]:
        raise NotImplementedError()

    @abstractmethod
    def update(self) -> None:
        raise NotImplementedError()
    
    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError()
    
    @abstractmethod
    def get_sprite(self, spritesheet: pygame.Surface) -> pygame.Surface:
        raise NotImplementedError()

class ScorePopup:
    def __init__(self, text: str, position: tuple[float, float], color: tuple[int, int, int]) -> None:
        self.text = text
        self.position = position
        self.timer = 60
        self.color = color
