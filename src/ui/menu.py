from typing import Any, Union

import pygame

SurfaceType = Union[pygame.Surface, pygame.surface.Surface]


def draw_text(screen: SurfaceType, msg: str, size: int,
              center: tuple[int, int], color: Any) -> None:
    """Render a single line of text, horizontally centred on ``center``.

    Args:
        screen: Target surface.
        msg: Text to render.
        size: Font size in points.
        center: ``(centerx, top_y)`` position for the text.
        color: Anything pygame accepts as a colour.
    """
    font = pygame.font.SysFont("ArialBlack", size)
    surf = font.render(msg, True, color)
    rect = surf.get_rect(centerx=center[0], y=center[1])
    screen.blit(surf, rect)


def draw_main_menu(screen: SurfaceType,
                   highscores: list[dict[str, Any]]) -> None:
    """Draw the title, the four menu entries and the top scores.

    Args:
        screen: Target surface.
        highscores: Sorted list of ``{"name", "score"}`` entries.
    """
    screen.fill("black")
    w = screen.get_width()

    draw_text(screen, "Pac-Man", 100, (w // 2, 60), "yellow")

    draw_text(screen, "[Space] Start a new game", 36, (w // 2, 220), "white")
    draw_text(screen, "[H] Highscores",          36, (w // 2, 270), "white")
    draw_text(screen, "[I] Instructions",        36, (w // 2, 320), "white")
    draw_text(screen, "[Esc] Quit",              36, (w // 2, 370), "white")

    draw_text(screen, "Top scores", 30, (w // 2, 460), "yellow")
    if not highscores:
        draw_text(screen, "no scores yet", 24, (w // 2, 500), "white")
    else:
        y = 500
        for i, entry in enumerate(highscores[:5], start=1):
            line = f"{i}. {entry['name']} - {entry['score']} pts"
            draw_text(screen, line, 24, (w // 2, y), "white")
            y += 30

    pygame.display.flip()


def draw_highscores_screen(screen: SurfaceType,
                           highscores: list[dict[str, Any]]) -> None:
    """Draw the full top-10 highscores screen."""
    screen.fill("black")
    w = screen.get_width()

    draw_text(screen, "Highscores", 70, (w // 2, 60), "yellow")
    draw_text(screen, "[Esc] Back to menu", 28, (w // 2, 140), "white")

    if not highscores:
        draw_text(screen, "no scores yet", 36, (w // 2, 300), "white")
    else:
        y = 230
        for i, entry in enumerate(highscores, start=1):
            line = f"{i:>2}. {entry['name']:<10}  {entry['score']:>6} pts"
            draw_text(screen, line, 32, (w // 2, y), "white")
            y += 42

    pygame.display.flip()


def draw_instructions_screen(screen: SurfaceType) -> None:
    """Draw the controls / rules screen."""
    screen.fill("black")
    w = screen.get_width()

    draw_text(screen, "Instructions", 70, (w // 2, 60), "yellow")
    draw_text(screen, "[Esc] Back to menu", 28, (w // 2, 140), "white")

    lines = [
        "Move : arrow keys or WASD",
        "Pause : Esc",
        "Resume : Space",
        "Back to menu : M (from the pause screen)",
        "",
        "Eat pacgums to clear the level.",
        "Super-pacgums let you eat the ghosts for a short time.",
        "Each level has a time limit. If it runs out you lose a life.",
        "",
        "Cheat keys (for peer review):",
        "F1 invincibility   F2 skip level   F3 freeze ghosts",
        "F4 +1 life         F5 speed boost",
    ]
    y = 220
    for line in lines:
        draw_text(screen, line, 26, (w // 2, y), "white")
        y += 38

    pygame.display.flip()
