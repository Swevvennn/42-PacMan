import pygame


class Cheats:
    """Cheat flags and key handler used for peer review.

    Attributes:
        invincible: When True, ghosts cannot kill the player.
        freeze_ghosts: When True, ghosts stop moving.
        fast_player: When True, the player moves faster.
    """

    def __init__(self) -> None:
        """Initialise every flag to False."""
        self.invincible: bool = False
        self.freeze_ghosts: bool = False
        self.fast_player: bool = False
        self.was_used: bool = False

    def handle_key(self, key: int) -> str | None:
        """Map a pygame key to a cheat action.

        Args:
            key: The pygame key code received from a KEYDOWN event.

        Returns:
            ``"invincibility"`` / ``"freeze"`` / ``"fast"`` when a toggle has
            just changed, ``"level_skip"`` / ``"extra_life"`` for one-shot
            cheats handled by the engine, ``None`` if the key is not a cheat.
        """
        if key == pygame.K_F1:
            self.invincible = not self.invincible
            self.was_used = True
            return "invincibility"
        if key == pygame.K_F2:
            self.was_used = True
            return "level_skip"
        if key == pygame.K_F3:
            self.freeze_ghosts = not self.freeze_ghosts
            self.was_used = True
            return "freeze"
        if key == pygame.K_F4:
            self.was_used = True
            return "extra_life"
        if key == pygame.K_F5:
            self.fast_player = not self.fast_player
            self.was_used = True
            return "fast"
        return None

    def status_line(self) -> str:
        """Return a short summary of the active flags, for the HUD."""
        parts: list[str] = []
        if self.invincible:
            parts.append("INV")
        if self.freeze_ghosts:
            parts.append("FRZ")
        if self.fast_player:
            parts.append("FAST")
        return " ".join(parts)
