import random
import sys
from typing import Any, Optional

import pygame

from src.maze.adapter import MazeAdapter, MazeGenerationError
from src.models.collectibles import Object
from src.models.entity import Direction, ScorePopup
from src.models.ghost import Ghost
from src.models.player import PacMan
from src.ui import menu, screens
from src.ui.game_view import GameView
from src.ui.screens import NameInput
from src.utils.cheats import Cheats
from src.utils.highscore import HighscoreManager
from src.utils.sounds import SoundManager


MENU = 0
PLAYING = 1
PAUSED = 2
GAME_OVER = 3
VICTORY = 4
HIGHSCORES = 5
INSTRUCTIONS = 6

NUM_LEVELS = 10
FPS = 60

FULL_SPEED = 0.075

REFERENCE_DOT_COUNT = 240
REFERENCE_MAZE_AREA = 18 * 18
MIN_LEVEL_TIME = 20


class GameController:
    """Own the whole game state and run the main loop."""

    def __init__(self, config: dict[str, Any]) -> None:
        """Initialise pygame and load every persistent piece of state.

        Args:
            config: The validated configuration dictionary.
        """
        self.config = config

        try:
            pygame.display.init()
            pygame.font.init()
            self.screen = pygame.display.set_mode(
                (0, 0), pygame.FULLSCREEN | pygame.SCALED)
            self.width, self.height = self.screen.get_size()
            pygame.display.set_caption("Pac-Man")
        except pygame.error as e:
            print(f"error: cannot initialize pygame display ({e})")
            sys.exit(1)

        self.clock = pygame.time.Clock()
        self.running = True

        self.highscore_mgr = HighscoreManager(
            str(config.get("highscore_filename", "highscores.json")),
        )
        self.cheats = Cheats()
        self.name_input: NameInput = NameInput()
        self.sounds = SoundManager()

        self.starting_lives: int = max(1, int(config.get("lives", 3)))
        self.level_max_time: int = max(10,
                                       int(config.get("level_max_time", 90)))
        self.current_level_max_time: int = self.level_max_time
        self.points_pacgum: int = int(config.get("points_per_pacgum", 10))
        self.points_super: int = int(config.get("points_per_super_pacgum", 50))
        self.points_ghost: int = int(config.get("points_per_ghost", 200))
        self.points_pacgum_active: int = self.points_pacgum
        self.points_super_active: int = self.points_super

        self.score: int = 0
        self.lives: int = self.starting_lives
        self.level: int = 1
        self.mode: int = MENU

        self.maze: Optional[MazeAdapter] = None
        self.view: Optional[GameView] = None
        self.pacman: Optional[PacMan] = None
        self.entities: list[Any] = []
        self.collectibles: list[Object] = []
        self.ghosts: list[Ghost] = []
        self.start_positions: dict[Any, tuple[float, float]] = {}

        self.tile_size: int = 0
        self.offset_x: int = 0
        self.offset_y: int = 0

        self.frightened_timer: int = 0
        self.frightened_duration: int = 0
        self.mode_timings: list[int] = []
        self.mode_index: int = 0
        self.mode_timer: int = 0
        self.scatter_mode: bool = True
        self.dots_eaten: int = 0
        self.fruits_spawned: int = 0
        self.active_fruit: Optional[Object] = None
        self.fruit_timer: int = 0
        self.effects: list[ScorePopup] = []
        self.ghosts_eaten_count: int = 0
        self.death_timer: int = 0
        self.base_ghost_speed: float = FULL_SPEED * 0.75
        self.base_pacman_speed: float = FULL_SPEED * 0.80
        self.level_timer: int = 0

    def _scale_collectible_values(self) -> None:
        """Scale pacgum / super-pacgum points so big mazes stay arcade-like.

        The total raw score from dots is kept close to
        ``REFERENCE_DOT_COUNT * points_per_pacgum``, which keeps fruit
        bonuses (100 to 5000) meaningful no matter the maze size.
        """
        dot_count = sum(1 for c in self.collectibles if c.name == "pacgum")
        super_count = sum(1 for c in self.collectibles
                          if c.name == "super_pacgum")
        if dot_count > 0:
            scale = REFERENCE_DOT_COUNT / dot_count
            self.points_pacgum_active = max(
                1, round(self.points_pacgum * scale)
            )
        else:
            self.points_pacgum_active = self.points_pacgum
        if super_count > 0:
            scale = max(1.0, 4.0 / super_count)
            self.points_super_active = max(
                1, round(self.points_super * scale)
            )
        else:
            self.points_super_active = self.points_super

    def _maze_size_for_level(self, level: int) -> tuple[int, int]:
        """Return the ``(width, height)`` for the given level number."""
        levels = self.config.get("level", [{"width": 21, "height": 21}])
        if not isinstance(levels, list) or not levels:
            return 21, 21
        idx = min(level - 1, len(levels) - 1)
        entry = levels[idx]
        return int(entry.get("width", 21)), int(entry.get("height", 21))

    def _time_limit_for_level(self, level: int) -> int:
        """Scale ``level_max_time`` to the area of the level's maze.

        The reference is a 21x21 maze, which keeps the configured value.
        Smaller mazes get proportionally less time, larger mazes more.
        """
        w, h = self._maze_size_for_level(level)
        scale = (w * h) / REFERENCE_MAZE_AREA
        return max(MIN_LEVEL_TIME, round(self.level_max_time * scale * 2))

    def _pacman_normal_speed(self) -> float:
        """Return Pac-Man's normal speed for the current level
        (arcade rates)."""
        lvl = self.level
        if lvl == 1:
            return FULL_SPEED * 0.80
        if lvl <= 4:
            return FULL_SPEED * 0.90
        if lvl <= 20:
            return FULL_SPEED * 1.00
        return FULL_SPEED * 0.90

    def _pacman_fright_speed(self) -> float:
        """Return Pac-Man's speed while a super-pacgum is active."""
        lvl = self.level
        if lvl == 1:
            return FULL_SPEED * 0.90
        if lvl <= 4:
            return FULL_SPEED * 0.95
        return FULL_SPEED * 1.00

    def _ghost_normal_speed(self) -> float:
        """Return the ghosts' normal chase/scatter speed
        for the current level."""
        lvl = self.level
        if lvl == 1:
            return FULL_SPEED * 0.75
        if lvl <= 4:
            return FULL_SPEED * 0.85
        return FULL_SPEED * 0.95

    def _ghost_fright_speed(self) -> float:
        """Return the ghosts' frightened speed for the current level."""
        lvl = self.level
        if lvl == 1:
            return FULL_SPEED * 0.50
        if lvl <= 4:
            return FULL_SPEED * 0.55
        if lvl <= 20:
            return FULL_SPEED * 0.60
        return self._ghost_normal_speed()

    def _elroy_thresholds(self) -> tuple[int, int]:
        """Return ``(elroy1, elroy2)`` dots-remaining thresholds for Blinky."""
        lvl = self.level
        if lvl == 1:
            return (20, 10)
        if lvl == 2:
            return (30, 15)
        if lvl <= 5:
            return (40, 20)
        if lvl <= 8:
            return (50, 25)
        if lvl <= 11:
            return (60, 30)
        if lvl <= 14:
            return (80, 40)
        if lvl <= 17:
            return (100, 50)
        return (120, 60)

    def _pacman_speed(self) -> float:
        """Return the current player speed, factoring in the speed cheat."""
        base = (self._pacman_fright_speed() if self.frightened_timer > 0
                else self._pacman_normal_speed())
        return base * (1.5 if self.cheats.fast_player else 1.0)

    def _start_level(self) -> bool:
        """Build the maze and spawn every entity for the current level.

        Returns:
            ``True`` on success, ``False`` if a fatal error happened.
        """
        maze_width, maze_height = self._maze_size_for_level(self.level)
        if self.level == 1:
            seed = int(self.config.get("seed", 42))
        else:
            seed = random.randint(1, 999_999)

        try:
            self.maze = MazeAdapter(maze_width, maze_height, seed)
        except MazeGenerationError as e:
            print(f"error: {e}")
            return False

        rows = len(self.maze.grid)
        cols = len(self.maze.grid[0])
        self.tile_size = min(self.width // cols, self.height // rows)
        self.offset_x = (self.width - (self.tile_size * cols)) // 2
        self.offset_y = (self.height - (self.tile_size * rows)) // 2

        try:
            self.view = GameView(self.maze, self.screen, self.tile_size,
                                 self.offset_x, self.offset_y)
        except (pygame.error, FileNotFoundError) as e:
            print(f"error: cannot load sprites ({e})")
            return False

        self.entities = []
        self.collectibles = []
        self.ghosts = []
        self.start_positions = {}
        pacman_spawn: tuple[int, int] = (cols // 2, rows // 2)

        for row_idx, row in enumerate(self.maze.grid):
            for col_idx, cell in enumerate(row):
                if cell == 4:
                    pacman_spawn = (col_idx, row_idx)
                    self.maze.grid[row_idx][col_idx] = 0
                elif cell == 3:
                    obj = Object("super_pacgum", (col_idx, row_idx))
                    self.maze.grid[row_idx][col_idx] = 0
                    self.entities.append(obj)
                    self.collectibles.append(obj)

        for row_idx, row in enumerate(self.maze.grid):
            for col_idx, cell in enumerate(row):
                if (abs(col_idx - pacman_spawn[0]) <= 1
                        and abs(row_idx - pacman_spawn[1]) <= 1):
                    continue
                if cell == 2:
                    obj = Object("pacgum", (col_idx, row_idx))
                    self.entities.append(obj)
                    self.collectibles.append(obj)

        self._scale_collectible_values()

        self.pacman = PacMan(pacman_spawn)
        self.pacman.speed = self._pacman_speed()
        self.start_positions[self.pacman] = (float(pacman_spawn[0]),
                                             float(pacman_spawn[1]))

        self.ghosts = [
            Ghost(1, "red", (cols - 2, 1)),
            Ghost(2, "pink", (1, rows - 2)),
            Ghost(3, "yellow", (cols - 2, rows - 2)),
            Ghost(4, "orange", (1, 1)),
        ]

        self.base_ghost_speed = self._ghost_normal_speed()
        for g in self.ghosts:
            self.start_positions[g] = (g.x, g.y)
            g.speed = self.base_ghost_speed

        self.entities.extend(self.ghosts)
        self.entities.append(self.pacman)

        for entity in self.entities:
            if isinstance(entity, Ghost):
                entity.is_chased = False

        self.frightened_timer = 0
        self.frightened_duration = max(180, 480 - (self.level - 1) * 30)

        self.mode_timings = [420, 1200, 420, 1200, 300, 1200, 300]
        self.mode_index = 0
        self.mode_timer = 0
        self.scatter_mode = True

        self.dots_eaten = 0
        self.fruits_spawned = 0
        self.active_fruit = None
        self.fruit_timer = 0
        self.effects = []
        self.ghosts_eaten_count = 0
        self.death_timer = 0
        self.level_timer = 0
        self.current_level_max_time = self._time_limit_for_level(self.level)
        self.sounds.stop_music()
        self.sounds.play_start()
        return True

    def _reset_positions(self) -> None:
        """Send the player and the ghosts back to their spawn positions."""
        if self.pacman is None:
            return
        spawn = self.start_positions[self.pacman]
        self.pacman.x, self.pacman.y = spawn[0], spawn[1]
        self.pacman.direction = Direction.RIGHT
        self.pacman.next_direction = Direction.RIGHT
        self.pacman.is_alive = True
        self.pacman.frame = 0
        self.pacman.anim_frame = 0.0
        self.pacman.nb_frames = 3
        self.pacman.speed = self._pacman_speed()

        for g in self.ghosts:
            gs = self.start_positions[g]
            g.x, g.y = gs[0], gs[1]
            g.respawn_timer = 0

    def _reset_after_death(self) -> None:
        """Reset positions and per-life state after losing a life."""
        self._reset_positions()
        self.frightened_timer = 0
        self.ghosts_eaten_count = 0
        self.death_timer = 0
        self.effects = []
        for g in self.ghosts:
            g.is_chased = False
            g.flashes = False
            g.respawn_timer = 0
        if (self.active_fruit is not None
           and self.active_fruit in self.entities):
            self.entities.remove(self.active_fruit)
        self.active_fruit = None
        self.fruit_timer = 0
        self.sounds.stop_music()
        self.sounds.stop_eyes()

    def _reset_game(self) -> None:
        """Reset the run state for a fresh game from the main menu."""
        self.score = 0
        self.lives = self.starting_lives
        self.level = 1
        self.cheats = Cheats()
        self.name_input = NameInput()
        if not self._start_level():
            self.running = False

    def _get_fruit_for_level(self, level: int) -> tuple[str, int]:
        """Return the ``(sprite_name, score)`` of the fruit for this level."""
        if level == 1:
            return "cherry", 100
        if level == 2:
            return "strawberry", 300
        if level <= 4:
            return "orange", 500
        if level <= 6:
            return "apple", 700
        if level <= 8:
            return "melon", 1000
        if level <= 10:
            return "galaxian", 2000
        if level <= 12:
            return "bell", 3000
        return "key", 5000

    def _spawn_fruit(self) -> None:
        """Drop a fruit on a random corridor cell, away from the player."""
        if self.maze is None or self.pacman is None:
            return
        fruit_name, score = self._get_fruit_for_level(self.level)
        rows = len(self.maze.grid)
        cols = len(self.maze.grid[0])

        pm_x, pm_y = round(self.pacman.x), round(self.pacman.y)
        candidates: list[tuple[int, int]] = []
        for y in range(rows):
            for x in range(cols):
                if self.maze.grid[y][x] == 1:
                    continue
                if abs(x - pm_x) + abs(y - pm_y) < 4:
                    continue
                candidates.append((x, y))

        if candidates:
            pos = random.choice(candidates)
        else:
            pos = (cols // 2, rows // 2)

        self.active_fruit = Object(fruit_name, pos)
        self.active_fruit.score_value = score
        self.entities.append(self.active_fruit)
        self.fruit_timer = max(480, (rows + cols) * 12)
        self.fruits_spawned += 1

    def _handle_menu_event(self, event: pygame.event.Event) -> None:
        """Process a single event when the main menu is showing."""
        if event.type == pygame.QUIT:
            self.running = False
            return
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_ESCAPE:
            self.running = False
        elif event.key == pygame.K_SPACE:
            self._reset_game()
            if self.running:
                self.mode = PLAYING
        elif event.key == pygame.K_h:
            self.mode = HIGHSCORES
        elif event.key == pygame.K_i:
            self.mode = INSTRUCTIONS

    def _handle_paused_event(self, event: pygame.event.Event) -> None:
        """Process a single event from the pause screen."""
        if event.type == pygame.QUIT:
            self.running = False
            return
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_SPACE:
            self.mode = PLAYING
        elif event.key == pygame.K_m:
            self.mode = MENU
        elif event.key == pygame.K_ESCAPE:
            self.running = False

    def _handle_simple_back_event(self, event: pygame.event.Event) -> None:
        """Shared event handler for screens that only accept Esc to leave."""
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.mode = MENU

    def _handle_name_entry_event(self, event: pygame.event.Event) -> None:
        """Process a key press from the Game Over or Victory name input.

        When cheats were used during the run, the name input is bypassed
        entirely and Enter/Esc simply returns to the main menu.
        """
        if event.type == pygame.QUIT:
            self.running = False
            return
        if self.cheats.was_used:
            if (event.type == pygame.KEYDOWN
                    and event.key in (pygame.K_RETURN, pygame.K_ESCAPE)):
                self.name_input = NameInput()
                self.mode = MENU
            return
        if self.name_input.handle_event(event):
            self.highscore_mgr.add(self.name_input.text(), self.score)
            self.highscore_mgr.save()
            self.name_input = NameInput()
            self.mode = MENU

    def _handle_playing_event(self, event: pygame.event.Event) -> None:
        """Process a single event during gameplay."""
        if event.type == pygame.QUIT:
            self.running = False
            return
        if event.type != pygame.KEYDOWN or self.pacman is None:
            return
        if event.key == pygame.K_ESCAPE:
            self.mode = PAUSED
            return

        action = self.cheats.handle_key(event.key)
        if action is not None:
            if action == "level_skip":
                self.collectibles = []
            elif action == "extra_life":
                self.lives += 1
                self.sounds.play_extend()
            elif action == "fast":
                self.pacman.speed = self._pacman_speed()
            return

        if event.key in (pygame.K_UP, pygame.K_w):
            self.pacman.next_direction = Direction.UP
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.pacman.next_direction = Direction.DOWN
        elif event.key in (pygame.K_LEFT, pygame.K_a):
            self.pacman.next_direction = Direction.LEFT
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self.pacman.next_direction = Direction.RIGHT

    def _advance_level(self) -> None:
        """Move to the next level or to the Victory screen."""
        if self.level >= NUM_LEVELS:
            self._enter_victory()
            return
        self.level += 1
        if not self._start_level():
            self.running = False
            return
        if self.view is not None:
            self.view.render(
                self.entities, self.score, self.lives, self.level,
                time_left=self.current_level_max_time,
                cheats_str=self.cheats.status_line(),
                effects=self.effects,
            )
        pygame.time.wait(500)
        pygame.event.clear()

    def _step_playing(self) -> None:
        """Advance the game by one frame while in PLAYING mode."""
        if self.maze is None or self.view is None or self.pacman is None:
            return

        if (self.frightened_timer == 0
                and self.mode_index < len(self.mode_timings)):
            self.mode_timer += 1
            if self.mode_timer >= self.mode_timings[self.mode_index]:
                self.mode_timer = 0
                self.mode_index += 1
                self.scatter_mode = not self.scatter_mode

        if self.frightened_timer > 0:
            self.frightened_timer -= 1
            should_flash = self.frightened_timer <= 180
            for entity in self.entities:
                if isinstance(entity, Ghost) and entity.is_chased:
                    entity.flashes = should_flash
            if self.frightened_timer == 0:
                for entity in self.entities:
                    if isinstance(entity, Ghost):
                        entity.is_chased = False
                        entity.flashes = False
                self.sounds.start_siren()
            else:
                self.sounds.start_fright()
        else:
            self.sounds.start_siren()

        self.pacman.speed = self._pacman_speed()

        if not any(g.respawn_timer > 0 for g in self.ghosts):
            self.sounds.stop_eyes()

        dots_remaining = len(self.collectibles)
        elroy1, elroy2 = self._elroy_thresholds()
        normal = self._ghost_normal_speed()
        fright = self._ghost_fright_speed()
        pac_normal = self._pacman_normal_speed()
        for g in self.ghosts:
            if g.is_chased:
                g.speed = fright
                continue
            if g.color == "red":
                if dots_remaining <= elroy2:
                    g.speed = pac_normal + FULL_SPEED * 0.05
                elif dots_remaining <= elroy1:
                    g.speed = pac_normal
                else:
                    g.speed = normal
            else:
                g.speed = normal

        for effect in self.effects[:]:
            effect.timer -= 1
            if effect.timer <= 0:
                self.effects.remove(effect)

        pm_x = round(self.pacman.x)
        pm_y = round(self.pacman.y)

        if self.active_fruit is not None:
            self.fruit_timer -= 1
            if self.fruit_timer <= 0:
                if self.active_fruit in self.entities:
                    self.entities.remove(self.active_fruit)
                self.active_fruit = None
            else:
                fx, fy = self.active_fruit.position
                if (round(fx), round(fy)) == (pm_x, pm_y):
                    val = int(getattr(self.active_fruit, "score_value", 0))
                    self.score += val
                    self.effects.append(
                        ScorePopup(str(val), self.active_fruit.position,
                                   (255, 184, 255))
                    )
                    if self.active_fruit in self.entities:
                        self.entities.remove(self.active_fruit)
                    self.active_fruit = None
                    self.sounds.play_eat_fruit()
        elif self.fruits_spawned < 2:
            if ((self.fruits_spawned == 0 and self.dots_eaten >= 70)
                    or (self.fruits_spawned == 1 and self.dots_eaten >= 170)):
                self._spawn_fruit()

        for entity in self.entities:
            entity.update()
            if isinstance(entity, Ghost):
                if entity.respawn_timer > 0:
                    entity.respawn_timer -= 1
                    continue

                dist2 = ((entity.x - self.pacman.x) ** 2
                         + (entity.y - self.pacman.y) ** 2)
                if dist2 < 0.25:
                    if entity.is_chased:
                        pts = self.points_ghost
                        self.score += pts
                        self.ghosts_eaten_count += 1
                        entity.is_chased = False
                        self.effects.append(
                            ScorePopup(str(pts), (entity.x, entity.y),
                                       (0, 255, 255))
                        )
                        entity.respawn_timer = 300
                        spawn = self.start_positions[entity]
                        entity.x, entity.y = spawn[0], spawn[1]
                        self.sounds.play_eat_ghost()
                        self.sounds.play_eyes()
                    elif self.pacman.is_alive and not self.cheats.invincible:
                        self.pacman.die()
                        self.lives -= 1
                        self.sounds.play_death()

                if self.cheats.freeze_ghosts:
                    continue

                others: list[tuple[int, int]] = []
                for g in self.ghosts:
                    if g is entity:
                        continue
                    cx, cy = round(g.x), round(g.y)
                    others.append((cx, cy))
                    if g.direction == Direction.UP:
                        others.append((cx, cy - 1))
                    elif g.direction == Direction.DOWN:
                        others.append((cx, cy + 1))
                    elif g.direction == Direction.LEFT:
                        others.append((cx - 1, cy))
                    elif g.direction == Direction.RIGHT:
                        others.append((cx + 1, cy))

                is_scatter = self.scatter_mode and self.frightened_timer == 0
                entity.move(self.maze.grid, self.pacman.position,
                            self.pacman.direction, others, scatter=is_scatter)
            elif hasattr(entity, "move") and not isinstance(entity, Ghost):
                entity.move(self.maze.grid)

        if not self.pacman.is_alive and self.pacman.frame == 6:
            self.death_timer += 1
            if self.death_timer >= 60:
                if self.lives > 0:
                    self._reset_after_death()
                else:
                    self._enter_game_over()
                    return

        pm_x = round(self.pacman.x)
        pm_y = round(self.pacman.y)

        if not self.collectibles:
            self._advance_level()
            return

        for entity in self.collectibles[:]:
            ex, ey = entity.position
            if (round(ex), round(ey)) != (pm_x, pm_y):
                continue
            if entity.name == "super_pacgum":
                self.score += self.points_super_active
                self.frightened_timer = self.frightened_duration
                self.dots_eaten += 1
                self.ghosts_eaten_count = 0
                for ghost in self.ghosts:
                    ghost.is_chased = True
                    ghost.flashes = False
                self.sounds.play_eat_super()
            elif entity.name == "pacgum":
                self.score += self.points_pacgum_active
                self.dots_eaten += 1
                self.sounds.play_eat_dot()
            self.collectibles.remove(entity)
            if entity in self.entities:
                self.entities.remove(entity)

        self.level_timer += 1
        if self.level_timer >= self.current_level_max_time * FPS:
            self.lives -= 1
            if self.lives <= 0:
                self._enter_game_over()
                return
            self._reset_after_death()
            self.level_timer = 0

        time_left = max(0, self.current_level_max_time
                        - self.level_timer // FPS)
        self.view.render(self.entities, self.score, self.lives, self.level,
                         time_left=time_left,
                         cheats_str=self.cheats.status_line(),
                         effects=self.effects)

    def _enter_game_over(self) -> None:
        """Switch to the Game Over screen with a fresh name input."""
        self.name_input = NameInput()
        self.mode = GAME_OVER
        self.sounds.stop_music()
        self.sounds.stop_eyes()

    def _enter_victory(self) -> None:
        """Switch to the Victory screen with a fresh name input."""
        self.name_input = NameInput()
        self.mode = VICTORY
        self.sounds.stop_music()
        self.sounds.stop_eyes()

    def run(self) -> None:
        """Main loop. Dispatch to the right handler based on ``self.mode``."""
        while self.running:
            if self.mode == MENU:
                menu.draw_main_menu(self.screen, self.highscore_mgr.top())
                for event in pygame.event.get():
                    self._handle_menu_event(event)

            elif self.mode == HIGHSCORES:
                menu.draw_highscores_screen(self.screen,
                                            self.highscore_mgr.top())
                for event in pygame.event.get():
                    self._handle_simple_back_event(event)

            elif self.mode == INSTRUCTIONS:
                menu.draw_instructions_screen(self.screen)
                for event in pygame.event.get():
                    self._handle_simple_back_event(event)

            elif self.mode == PLAYING:
                for event in pygame.event.get():
                    self._handle_playing_event(event)
                if self.mode == PLAYING:
                    self._step_playing()

            elif self.mode == PAUSED:
                screens.draw_pause(self.screen)
                for event in pygame.event.get():
                    self._handle_paused_event(event)

            elif self.mode == GAME_OVER:
                screens.draw_game_over(self.screen, self.score,
                                       self.name_input,
                                       cheats_used=self.cheats.was_used)
                for event in pygame.event.get():
                    self._handle_name_entry_event(event)

            elif self.mode == VICTORY:
                screens.draw_victory(self.screen, self.score, self.name_input,
                                     cheats_used=self.cheats.was_used)
                for event in pygame.event.get():
                    self._handle_name_entry_event(event)

            else:
                self.mode = MENU

            self.clock.tick(FPS)

        pygame.quit()
        sys.exit(0)
