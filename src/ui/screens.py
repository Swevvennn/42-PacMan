import pygame

from src.ui.menu import draw_text, SurfaceType


class NameInput:
    """Buffered text input limited to 10 alphanumeric or space characters."""

    def __init__(self, max_len: int = 10) -> None:
        """Build an empty input buffer with the given length cap."""
        self.buffer: str = ""
        self.max_len = max_len

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Process a pygame event and update the buffer.

        Args:
            event: The pygame event to process.

        Returns:
            True when the user pressed Enter and the buffer is non-empty.
        """
        if event.type != pygame.KEYDOWN:
            return False
        if event.key == pygame.K_RETURN:
            return len(self.buffer.strip()) > 0
        if event.key == pygame.K_BACKSPACE:
            self.buffer = self.buffer[:-1]
            return False
        ch = event.unicode
        if ch and len(self.buffer) < self.max_len:
            if ch.isalnum() or ch == " ":
                self.buffer += ch
        return False

    def text(self) -> str:
        """Return the trimmed buffer content."""
        return self.buffer.strip()


def draw_pause(screen: SurfaceType) -> None:
    """Draw the pause screen overlay."""
    screen.fill("black")
    w = screen.get_width()
    draw_text(screen, "Paused",                100, (w // 2, 120), "yellow")
    draw_text(screen, "[Space] Resume",         40, (w // 2, 300), "white")
    draw_text(screen, "[M] Back to main menu",  40, (w // 2, 360), "white")
    draw_text(screen, "[Esc] Quit",             40, (w // 2, 420), "white")
    pygame.display.flip()


def draw_game_over(screen: SurfaceType, score: int,
                   name_input: NameInput, cheats_used: bool = False) -> None:
    """Draw the Game Over screen with the highscore name prompt.

    Args:
        screen: Target surface.
        score: Final score to display.
        name_input: The name input buffer (ignored when ``cheats_used``).
        cheats_used: When True, the score is not eligible for the leaderboard.
    """
    screen.fill("black")
    w = screen.get_width()
    draw_text(screen, "Game Over",                90, (w // 2, 80),  "red")
    draw_text(screen, f"Final score: {score}",    50, (w // 2, 220), "white")
    if cheats_used:
        draw_text(screen, "Cheats were used.", 36, (w // 2, 320), "red")
        draw_text(screen, "Score will not be saved.",
                  32, (w // 2, 370), "white")
        draw_text(screen, "[Enter / Esc] Back to menu",
                  28, (w // 2, 470), "white")
    else:
        draw_text(screen, "Enter your name and press Enter:",
                  32, (w // 2, 320), "white")
        cursor = "_" if (pygame.time.get_ticks() // 400) % 2 == 0 else " "
        draw_text(screen, name_input.buffer + cursor,
                  60, (w // 2, 380), "yellow")
        draw_text(screen, "(10 chars max, letters / digits / spaces)",
                  22, (w // 2, 470), "white")
    pygame.display.flip()


def draw_victory(screen: SurfaceType, score: int,
                 name_input: NameInput, cheats_used: bool = False) -> None:
    """Draw the Victory screen with the highscore name prompt.

    Args:
        screen: Target surface.
        score: Final score to display.
        name_input: The name input buffer (ignored when ``cheats_used``).
        cheats_used: When True, the score is not eligible for the leaderboard.
    """
    screen.fill("black")
    w = screen.get_width()
    draw_text(screen, "Victory!",                 90, (w // 2, 80),  "yellow")
    draw_text(screen, "You cleared every level.", 36, (w // 2, 180), "white")
    draw_text(screen, f"Final score: {score}",    50, (w // 2, 240), "white")
    if cheats_used:
        draw_text(screen, "Cheats were used.", 36, (w // 2, 340), "red")
        draw_text(screen, "Score will not be saved.",
                  32, (w // 2, 390), "white")
        draw_text(screen, "[Enter / Esc] Back to menu",
                  28, (w // 2, 490), "white")
    else:
        draw_text(screen, "Enter your name and press Enter:",
                  32, (w // 2, 340), "white")
        cursor = "_" if (pygame.time.get_ticks() // 400) % 2 == 0 else " "
        draw_text(screen, name_input.buffer + cursor,
                  60, (w // 2, 400), "yellow")
        draw_text(screen, "(10 chars max, letters / digits / spaces)",
                  22, (w // 2, 490), "white")
    pygame.display.flip()
