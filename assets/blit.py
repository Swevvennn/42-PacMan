import sys
import pygame

TEST_X = int(input("Enter X coordinate: ")) * 16
TEST_Y = int(input("Enter Y coordinate: ")) * 16
TEST_W = 16
TEST_H = 16

IMAGE_PATH = "PacManAssets_Map_TileSet.png"

def main():
    
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Sprite Cutter Tool")
    
    try:
        spritesheet = pygame.image.load(IMAGE_PATH).convert_alpha()
    except Exception as e:
        print(f"Error loading image: {e}")
        sys.exit(1)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        screen.fill((0, 0, 0))
        
        screen.blit(spritesheet, (0, 0))
        
        rect = pygame.Rect(TEST_X, TEST_Y, TEST_W, TEST_H)
        pygame.draw.rect(screen, (255, 0, 0), rect, 1)

        pygame.display.flip()
    print(f"Values to save: X={TEST_X}, Y={TEST_Y}, W={TEST_W}, H={TEST_H}")
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
