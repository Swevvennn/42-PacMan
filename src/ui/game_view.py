import pygame
from src.models.entity import Entity, ScorePopup
from src.models.ghost import Ghost
from src.models.player import PacMan
from src.models.collectibles import Object

class GameView:
    def __init__(self, maze, screen: pygame.Surface, tile_size: int, offset_x: int, offset_y: int) -> None:
        self.maze = maze
        self.screen = screen
        self.tile_size = tile_size
        self.offset_x = offset_x
        self.offset_y = offset_y
        
        self.pac_man_spritesheet = pygame.image.load("assets/PacManAssets-PacMan.png").convert_alpha()
        self.ghost_spritesheet = pygame.image.load("assets/PacManAssets-Ghosts.png").convert_alpha()
        self.object_spritesheet = pygame.image.load("assets/PacManAssets-Items.png").convert_alpha()
        self.textures_spritesheet = pygame.image.load("assets/PacManAssets_Map_TileSet.png").convert_alpha()
        self.textures = {}
        self.load_textures(self.textures_spritesheet)
        self.font = pygame.font.Font(None, 48)
        self.popup_font = pygame.font.Font(None, 24)
        self.background_surface = pygame.Surface(self.screen.get_size())
        self._render_background()
    
    def _get_wall_mask(self, row_idx: int, col_idx: int) -> int:
        mask = 0
        if row_idx > 0 and self.maze.grid[row_idx - 1][col_idx] == 1:
            mask += 1
        if col_idx < len(self.maze.grid[0]) - 1 and self.maze.grid[row_idx][col_idx + 1] == 1:
            mask += 2
        if row_idx < len(self.maze.grid) - 1 and self.maze.grid[row_idx + 1][col_idx] == 1:
            mask += 4
        if col_idx > 0 and self.maze.grid[row_idx][col_idx - 1] == 1:
            mask += 8
        return mask

    def get_sprite(self, e: Entity) -> pygame.Surface:
        if isinstance(e, Ghost):
            return e.get_sprite(self.ghost_spritesheet)
        elif isinstance(e, PacMan):
            return e.get_sprite(self.pac_man_spritesheet)
        elif isinstance(e, Object):
            return e.get_sprite(self.object_spritesheet)
        else:
            raise ValueError(f"Unknown entity type: {type(e)}")

    def _render_background(self) -> None:
        self.background_surface.fill((0, 0, 0))

        small_size = self.tile_size // 2
        center_offset = (self.tile_size - small_size) // 2

        for row_idx, row in enumerate(self.maze.grid):
            for col_idx, cell in enumerate(row):
                px = (col_idx * self.tile_size) + self.offset_x
                py = (row_idx * self.tile_size) + self.offset_y
                
                if cell == 1:
                    mask = self._get_wall_mask(row_idx, col_idx)
                    cx = px + center_offset
                    cy = py + center_offset
                    
                    self.background_surface.blit(self.wall_textures[mask], (cx, cy))
                    
                    if mask & 1:
                        self.background_surface.blit(self.wall_textures[5], (cx, cy - small_size))
                    if mask & 2:
                        self.background_surface.blit(self.wall_textures[10], (cx + small_size, cy))
                    if mask & 4:
                        self.background_surface.blit(self.wall_textures[5], (cx, cy + small_size))
                    if mask & 8:
                        self.background_surface.blit(self.wall_textures[10], (cx - small_size, cy))
                        
                elif cell in self.textures:
                    self.background_surface.blit(self.textures[cell], (px + center_offset, py + center_offset))

    def render(self, entities: list[Entity], score: int = 0, lives: int = 3, level: int = 1, effects: list[ScorePopup] | None = None) -> None:
        if effects is None:
            effects = []
        self.screen.blit(self.background_surface, (0, 0))

        small_size = self.tile_size // 2
        center_offset = (self.tile_size - small_size) // 2

        for entity in entities:
            base_px = (entity.position[0] * self.tile_size) + self.offset_x
            base_py = (entity.position[1] * self.tile_size) + self.offset_y
            raw_sprite = self.get_sprite(entity)
            
            if isinstance(entity, Object):
                if entity.name in ["pacgum", "super_pacgum"]:
                    scaled_sprite = pygame.transform.scale(raw_sprite, (small_size, small_size))
                    self.screen.blit(scaled_sprite, (base_px + center_offset, base_py + center_offset))
                else:
                    scaled_sprite = pygame.transform.scale(raw_sprite, (self.tile_size, self.tile_size))
                    self.screen.blit(scaled_sprite, (base_px, base_py))
            else:
                scaled_sprite = pygame.transform.scale(raw_sprite, (self.tile_size, self.tile_size))
                self.screen.blit(scaled_sprite, (base_px, base_py))
        
        for effect in effects:
            text_surface = self.popup_font.render(effect.text, True, effect.color)
            px = (effect.position[0] * self.tile_size) + self.offset_x + (self.tile_size // 2) - (text_surface.get_width() // 2)
            py = (effect.position[1] * self.tile_size) + self.offset_y + (self.tile_size // 2) - (text_surface.get_height() // 2)
            self.screen.blit(text_surface, (px, py))
            
        score_surface = self.font.render(f"SCORE: {score}", True, (255, 255, 255))
        self.screen.blit(score_surface, (20, 20))
        lives_surface = self.font.render(f"LIVES: {lives}", True, (255, 255, 0))
        self.screen.blit(lives_surface, (20, 60))
        level_surface = self.font.render(f"LEVEL: {level}", True, (255, 255, 255))
        self.screen.blit(level_surface, (20, 100))

        pygame.display.flip()

    def load_textures(self, spritesheet: pygame.Surface) -> None:
        bases = {
            'wall':         spritesheet.subsurface(pygame.Rect(64, 48, 16, 16)).copy(),
            'angle':        spritesheet.subsurface(pygame.Rect(48, 48, 16, 16)).copy(),
            'end_wall':     spritesheet.subsurface(pygame.Rect(176, 64, 16, 16)).copy(),
            '3_ways':       spritesheet.subsurface(pygame.Rect(208, 48, 16, 16)).copy(),
            '4_ways':       spritesheet.subsurface(pygame.Rect(144, 176, 16, 16)).copy(),
            'alone_wall':   spritesheet.subsurface(pygame.Rect(128, 192, 16, 16)).copy(),
        }

        mask_map = {
            0:  ('alone_wall', 0),
            1:  ('end_wall', 90),
            2:  ('end_wall', 0),
            3:  ('angle', 90),
            4:  ('end_wall', 270),
            5:  ('wall', 90),
            6:  ('angle', 0),
            7:  ('3_ways', 0),
            8:  ('end_wall', 180),
            9:  ('angle', 180),
            10: ('wall', 0),
            11: ('3_ways', 90),
            12: ('angle', 270),
            13: ('3_ways', 180),
            14: ('3_ways', 270),
            15: ('4_ways', 0)
        }

        self.wall_textures = {}
        small_size = self.tile_size // 2
        for mask, (img_key, angle) in mask_map.items():
            img = bases[img_key]
            if angle != 0:
                img = pygame.transform.rotate(img, angle)
            self.wall_textures[mask] = pygame.transform.scale(img, (small_size, small_size))