import pygame

class MapNavigator:
    def __init__(self, filename):
        try:
            self.map_surface = pygame.image.load(filename).convert()
        except:
            # Fallback if map.png doesn't exist
            self.map_surface = pygame.Surface((2000, 2000))
            self.map_surface.fill((0, 0, 0))
            pygame.draw.rect(self.map_surface, (255, 255, 255), (100, 100, 1800, 1800), 50)
            
        self.width = self.map_surface.get_width()
        self.height = self.map_surface.get_height()

    def is_walkable(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            # Check if pixel is white (255, 255, 255)
            color = self.map_surface.get_at((int(x), int(y)))
            return color[0] > 200 and color[1] > 200 and color[2] > 200
        return False

    def draw(self, screen, offset):
        screen.blit(self.map_surface, offset)