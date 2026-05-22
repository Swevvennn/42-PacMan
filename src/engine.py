import sys
import pygame
from src.ui.game_view import GameView
from src.maze.adapter import MazeAdapter
from src.models.player import PacMan
from src.models.ghost import Ghost
from src.models.collectibles import Object
from src.models.entity import Direction, ScorePopup
import random
import math

class GameController:
    def __init__(self, config: dict) -> None:
        pygame.display.init()
        pygame.font.init()
        info = pygame.display.Info()
        self.width = info.current_w
        self.height = info.current_h
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.running = True
        self.score = 0
        self.lives = 3
        self.config = config
        self.level = 1
        self.mode = 0
        self._start_level()

    def _start_level(self) -> None:
        level_config = self.config.get("level", [{"width": 21, "height": 21}])[0]
        maze_width = level_config.get("width", 21)
        maze_height = level_config.get("height", 21)

        seed = self.config.get("seed", 42) if self.level == 1 else random.randint(0, 999999)
        self.maze = MazeAdapter(maze_width, maze_height, seed)

        rows = len(self.maze.grid)
        cols = len(self.maze.grid[0])
        self.tile_size = min(self.width // cols, self.height // rows)
        self.offset_x = (self.width - (self.tile_size * cols)) // 2
        self.offset_y = (self.height - (self.tile_size * rows)) // 2

        self.view = GameView(self.maze, self.screen, self.tile_size, self.offset_x, self.offset_y)

        self.entities = []
        self.collectibles = []
        self.ghosts = []
        self.start_positions = {}
        pacman_spawn = (cols // 2, rows // 2)

        for row_idx, row in enumerate(self.maze.grid):
            for col_idx, cell in enumerate(row):
                if cell == 4:
                    pacman_spawn = (col_idx, row_idx)
                    self.maze.grid[row_idx][col_idx] = 0
                elif cell == 3:
                    obj = Object("super_pacgum", (col_idx, row_idx))
                    self.entities.append(obj)
                    self.collectibles.append(obj)

        for row_idx, row in enumerate(self.maze.grid):
            for col_idx, cell in enumerate(row):
                if abs(col_idx - pacman_spawn[0]) <= 1 and abs(row_idx - pacman_spawn[1]) <= 1:
                    continue
                if cell == 2:
                    obj = Object("pacgum", (col_idx, row_idx))
                    self.entities.append(obj)
                    self.collectibles.append(obj)

        self.pacman = PacMan(pacman_spawn)
        self.start_positions[self.pacman] = pacman_spawn

        self.ghosts = [
            Ghost(1, "red", (cols - 2, 1)),
            Ghost(2, "pink", (1, rows - 2)),
            Ghost(3, "yellow", (cols - 2, rows - 2)),
            Ghost(4, "orange", (1, 1))
        ]

        self.base_ghost_speed = min(0.08, 0.04 + (self.level - 1) * 0.005)

        for g in self.ghosts:
            self.start_positions[g] = (g.x, g.y)
            g.speed = self.base_ghost_speed

        self.entities.extend(self.ghosts)
        self.entities.append(self.pacman)

        for entity in self.entities:
            if isinstance(entity, Ghost):
                entity.is_chased = False
        self.frightened_timer = 0

        self.mode_timings = [420, 1200, 420, 1200, 300, 1200, 300]
        self.mode_index = 0
        self.mode_timer = 0
        self.scatter_mode = True
        self.frightened_duration = max(180, 480 - (self.level - 1) * 30)

        self.dots_eaten = 0
        self.fruits_spawned = 0
        self.active_fruit = None
        self.fruit_timer = 0
        self.effects: list[ScorePopup] = []
        self.ghosts_eaten_count = 0
        self.death_timer = 0

    def _reset_positions(self) -> None:
        self.pacman.x, self.pacman.y = float(self.start_positions[self.pacman][0]), float(self.start_positions[self.pacman][1])
        self.pacman.direction = Direction.RIGHT
        self.pacman.next_direction = Direction.RIGHT
        self.pacman.is_alive = True
        self.pacman.frame = 0
        self.pacman.anim_frame = 0.0
        self.pacman.nb_frames = 3

        for g in self.ghosts:
            g.x, g.y = float(self.start_positions[g][0]), float(self.start_positions[g][1])
            g.path = []
            g.respawn_timer = 0

    def _get_fruit_for_level(self, level: int) -> tuple[str, int]:
        if level == 1: return "cherry", 100
        elif level == 2: return "strawberry", 300
        elif level <= 4: return "orange", 500
        elif level <= 6: return "apple", 700
        elif level <= 8: return "melon", 1000
        elif level <= 10: return "galaxian", 2000
        elif level <= 12: return "bell", 3000
        else: return "key", 5000

    def _spawn_fruit(self) -> None:
        fruit_name, score = self._get_fruit_for_level(self.level)
        rows = len(self.maze.grid)
        cols = len(self.maze.grid[0])
        pos = (cols // 2, rows // 2)
        self.active_fruit = Object(fruit_name, pos)
        self.active_fruit.score_value = score
        self.entities.append(self.active_fruit)
        self.fruit_timer = 600
        self.fruits_spawned += 1
    
    def _print_text(self, pos: tuple[int, int] | list[int, int], size: int,
                    msg: str, color: str | tuple[int, int, int] | list[int, int, int]):
        font = pygame.font.SysFont('ArialBlack', size)
        text = font.render(msg, True, color)
        text_pos = text.get_rect(centerx = pos[0],
                                    y = pos[1])
        self.screen.blit(text,text_pos)

    def run(self) -> None:
        while self.running:
            match self.mode:
                case 0:
                    self.screen.fill('black')

                    self._print_text((150, 10), 25, 'Press Esc to quit the game', 'white')
                    self._print_text((1920/2, 100), 100, 'Pac-Man', 'yellow')
                    self._print_text((1920/2, 300), 50, 'Press Space to start a game', 'white')

                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            self.running = False
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                self.running = False
                            elif event.key == pygame.K_SPACE:
                                self.mode = 1
                    
                    pygame.display.flip()

                case 1:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            self.running = False
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                self.mode = 2
                            elif event.key == pygame.K_UP:
                                self.pacman.next_direction = Direction.UP
                            elif event.key == pygame.K_DOWN:
                                self.pacman.next_direction = Direction.DOWN
                            elif event.key == pygame.K_LEFT:
                                self.pacman.next_direction = Direction.LEFT
                            elif event.key == pygame.K_RIGHT:
                                self.pacman.next_direction = Direction.RIGHT

                    if self.frightened_timer == 0 and self.mode_index < len(self.mode_timings):
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

                    dots_remaining = len(self.collectibles)
                    for g in self.ghosts:
                        if g.color == "red":
                            if dots_remaining <= 10:
                                g.speed = self.base_ghost_speed * 1.10
                            elif dots_remaining <= 20:
                                g.speed = self.base_ghost_speed * 1.05
                            else:
                                g.speed = self.base_ghost_speed

                    for effect in self.effects[:]:
                        effect.timer -= 1
                        if effect.timer <= 0:
                            self.effects.remove(effect)

                    if self.active_fruit:
                        self.fruit_timer -= 1
                        if self.fruit_timer <= 0:
                            self.entities.remove(self.active_fruit)
                            self.active_fruit = None
                        else:
                            fx, fy = self.active_fruit.position
                            if (round(fx), round(fy)) == (pm_x, pm_y):
                                self.score += self.active_fruit.score_value
                                self.effects.append(ScorePopup(str(self.active_fruit.score_value), self.active_fruit.position, (255, 184, 255)))
                                self.entities.remove(self.active_fruit)
                                self.active_fruit = None
                    elif self.fruits_spawned < 2:
                        if (self.fruits_spawned == 0 and self.dots_eaten >= 70) or \
                        (self.fruits_spawned == 1 and self.dots_eaten >= 170):
                            self._spawn_fruit()

                    for entity in self.entities:
                        entity.update()
                        if isinstance(entity, Ghost):
                            if entity.respawn_timer > 0:
                                entity.respawn_timer -= 1
                                continue

                            if (entity.x - self.pacman.x)**2 + (entity.y - self.pacman.y)**2 < 0.25:
                                if entity.is_chased:
                                    points = 200 * (2 ** self.ghosts_eaten_count)
                                    self.score += points
                                    self.ghosts_eaten_count += 1
                                    entity.is_chased = False
                                    self.effects.append(ScorePopup(str(points), (entity.x, entity.y), (0, 255, 255)))
                                    entity.respawn_timer = 300
                                    entity.x, entity.y = float(self.start_positions[entity][0]), float(self.start_positions[entity][1])
                                elif self.pacman.is_alive:
                                    self.pacman.die()
                                    self.lives -= 1
                            other_ghosts_pos = []
                            for g in self.ghosts:
                                if g is not entity:
                                    cx, cy = round(g.x), round(g.y)
                                    other_ghosts_pos.append((cx, cy))
                                    if g.direction == Direction.UP:
                                        other_ghosts_pos.append((cx, cy - 1))
                                    elif g.direction == Direction.DOWN:
                                        other_ghosts_pos.append((cx, cy + 1))
                                    elif g.direction == Direction.LEFT:
                                        other_ghosts_pos.append((cx - 1, cy))
                                    elif g.direction == Direction.RIGHT:
                                        other_ghosts_pos.append((cx + 1, cy))

                            is_scatter = self.scatter_mode and self.frightened_timer == 0
                            entity.move(self.maze.grid, self.pacman.position, self.pacman.direction, other_ghosts_pos, scatter=is_scatter)
                        elif hasattr(entity, 'move') and not isinstance(entity, Ghost):
                            entity.move(self.maze.grid)

                    if not self.pacman.is_alive and self.pacman.frame == 6:
                        self.death_timer += 1
                        if self.death_timer >= 60:
                            self.death_timer = 0
                            if self.lives > 0:
                                self._reset_positions()
                            else:
                                self.running = False

                    pm_x, pm_y = round(self.pacman.x), round(self.pacman.y)

                    if not self.collectibles:
                        self.level += 1
                        self._start_level()
                        pygame.time.wait(1000)
                        continue

                    for entity in self.collectibles[:]:
                        ex, ey = entity.position
                        if (round(ex), round(ey)) == (pm_x, pm_y):
                            if entity.name == "super_pacgum":
                                self.score += 50
                                self.frightened_timer = self.frightened_duration
                                self.dots_eaten += 1
                                self.ghosts_eaten_count = 0
                                for ghost in self.ghosts:
                                    ghost.is_chased = True
                                    ghost.flashes = False
                            elif entity.name == "pacgum":
                                self.score += 10
                                self.dots_eaten += 1

                            self.collectibles.remove(entity)
                            self.entities.remove(entity)

                    self.view.render(self.entities, self.score, self.lives, self.level, self.effects)
                
                case 2:
                    self.screen.fill('black')

                    self._print_text((150, 10), 25, 'Press Esc to quit the game', 'white')
                    self._print_text((1920/2, 100), 100, 'Pac-Man', 'yellow')
                    self._print_text((1920/2, 300), 50, 'Press Space to resume', 'white')
                    self._print_text((1920/2, 400), 100, 'Game Paused', 'white')

                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            self.running = False
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                self.running = False
                            elif event.key == pygame.K_SPACE:
                                self.mode = 1

                    pygame.display.flip()
                
                case 3:
                    self.screen.fill('black')

                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            self.running = False
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                pass

                case 4:
                    self.screen.fill('black')
                    
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            self.running = False
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                pass

                case _:
                    self.mode = 0

            self.clock.tick(60)

        pygame.quit()
        sys.exit(0)
