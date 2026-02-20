import pygame
import random
import math
import os

# --- SETTINGS ---
WIDTH, HEIGHT = 1100, 700
UI_WIDTH = 300
MAP_AREA = WIDTH - UI_WIDTH
FPS = 60
AGENT_COUNT = 45

# Surveillance Aesthetic Colors
COLOR_BG = (5, 10, 15)
COLOR_WHITE = (255, 255, 255)
COLOR_ACCENT = (0, 255, 180)
COLOR_DANGER = (255, 40, 40)
COLOR_GRID = (15, 25, 35)

class MapHandler:
    def __init__(self):
        self.surface = None
        self.mask = None
        self.load_map()

    def load_map(self):
        if os.path.exists("map.png"):
            self.surface = pygame.image.load("map.png").convert()
            self.surface = pygame.transform.scale(self.surface, (MAP_AREA, HEIGHT))
        else:
            # Generate fallback: Dark city with white boulevards
            self.surface = pygame.Surface((MAP_AREA, HEIGHT))
            self.surface.fill((10, 10, 12))
            for i in range(0, MAP_AREA, 180):
                pygame.draw.rect(self.surface, COLOR_WHITE, (i, 0, 50, HEIGHT))
            for i in range(0, HEIGHT, 180):
                pygame.draw.rect(self.surface, COLOR_WHITE, (0, i, MAP_AREA, 50))

        self.mask = pygame.mask.from_threshold(self.surface, COLOR_WHITE, (10, 10, 10))

    def is_walkable(self, x, y):
        if 0 <= x < MAP_AREA and 0 <= y < HEIGHT:
            return self.mask.get_at((int(x), int(y)))
        return False

class Agent:
    def __init__(self, id, map_handler):
        self.id = id
        self.mh = map_handler
        self.has_app = random.random() < 0.6
        
        # Fixed Hostility Gradient: Ensuring we get Reds and Greens
        # 0.0 is pure calm (Green), 1.0 is pure riot (Red)
        self.hostility = random.uniform(0.0, 1.0)
        
        self.radius = 7
        self.x, self.y = 0, 0
        self.spawn()
        
        self.angle = random.choice([0, 90, 180, 270])
        self.speed = random.uniform(0.7, 2.3) 
        self.state = "WALKING"
        self.timer = 0
        self.activity = random.choice([
            "Eating a Big Number 5", "Ignoring Roman's Call", 
            "Buying Sprunk", "Heading to Malibu Club"
        ])

    def spawn(self):
        for _ in range(500):
            rx, ry = random.randint(10, MAP_AREA-10), random.randint(10, HEIGHT-10)
            if self.mh.is_walkable(rx, ry):
                self.x, self.y = rx, ry
                return

    def update(self, is_controlled):
        if is_controlled:
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            if keys[pygame.K_LEFT]: dx = -self.speed * 1.5
            if keys[pygame.K_RIGHT]: dx = self.speed * 1.5
            if keys[pygame.K_UP]: dy = -self.speed * 1.5
            if keys[pygame.K_DOWN]: dy = self.speed * 1.5
            
            if self.mh.is_walkable(self.x + dx*3, self.y + dy*3):
                self.x += dx
                self.y += dy
            return

        if self.state == "IDLE":
            self.timer -= 1
            if self.timer <= 0:
                self.state = "WALKING"
                self.angle = random.choice([0, 90, 180, 270])
        else:
            if random.random() < 0.005:
                self.state = "IDLE"
                self.timer = random.randint(40, 120)
                return

            rad = math.radians(self.angle)
            nx, ny = self.x + math.cos(rad)*self.speed, self.y + math.sin(rad)*self.speed
            
            if self.mh.is_walkable(nx + math.cos(rad)*12, ny + math.sin(rad)*12):
                self.x, self.y = nx, ny
            else:
                self.angle = random.choice([0, 90, 180, 270])

class Camera:
    def __init__(self):
        self.target_zoom = 1.0
        self.current_zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0

    def update(self, target_pos):
        if target_pos:
            self.target_zoom = 2.2
            # Calculate centering logic
            dest_x = target_pos[0] - (MAP_AREA / 2) / self.target_zoom
            dest_y = target_pos[1] - (HEIGHT / 2) / self.target_zoom
            self.offset_x += (dest_x - self.offset_x) * 0.08
            self.offset_y += (dest_y - self.offset_y) * 0.08
        else:
            self.target_zoom = 1.0
            self.offset_x += (0 - self.offset_x) * 0.08
            self.offset_y += (0 - self.offset_y) * 0.08
        
        self.current_zoom += (self.target_zoom - self.current_zoom) * 0.08

class Simulation:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.mh = MapHandler()
        self.camera = Camera()
        self.agents = [Agent(i, self.mh) for i in range(AGENT_COUNT)]
        self.selected = None
        self.ui_scale = 0.0 
        self.clock = pygame.time.Clock()

    def draw_world(self):
        # Create world surface
        world_surf = pygame.Surface((MAP_AREA, HEIGHT))
        world_surf.blit(self.mh.surface, (0,0))
        
        # Draw Background Grid for style
        for x in range(0, MAP_AREA, 40):
            pygame.draw.line(world_surf, COLOR_GRID, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, 40):
            pygame.draw.line(world_surf, COLOR_GRID, (0, y), (MAP_AREA, y))

        for a in self.agents:
            # FIXED GRADIENT: Hostility 1.0 = Red, 0.0 = Green
            r = int(255 * a.hostility)
            g = int(255 * (1 - a.hostility))
            b = 50
            
            pygame.draw.circle(world_surf, (r, g, b), (int(a.x), int(a.y)), a.radius)
            if a.has_app:
                pygame.draw.circle(world_surf, COLOR_WHITE, (int(a.x), int(a.y)), a.radius+3, 1)

        # Apply Camera Zoom/Offset
        zoom = self.camera.current_zoom
        view_w, view_h = int(MAP_AREA / zoom), int(HEIGHT / zoom)
        
        sub_rect = pygame.Rect(self.camera.offset_x, self.camera.offset_y, view_w, view_h)
        sub_rect = sub_rect.clamp(pygame.Rect(0, 0, MAP_AREA, HEIGHT))
        
        view_surf = world_surf.subsurface(sub_rect)
        scaled_view = pygame.transform.scale(view_surf, (MAP_AREA, HEIGHT))
        self.screen.blit(scaled_view, (0, 0))

    def draw_ui(self):
        target_s = 1.0 if self.selected else 0.0
        self.ui_scale += (target_s - self.ui_scale) * 0.1
        
        if self.ui_scale > 0.01:
            ui_x = WIDTH - (UI_WIDTH * self.ui_scale)
            pygame.draw.rect(self.screen, (10, 15, 20), (ui_x, 0, UI_WIDTH, HEIGHT))
            pygame.draw.line(self.screen, COLOR_ACCENT, (ui_x, 0), (ui_x, HEIGHT), 3)
            
            if self.selected:
                f_hdr = pygame.font.SysFont("Courier", 22, bold=True)
                f_std = pygame.font.SysFont("Courier", 16)
                
                self.screen.blit(f_hdr.render("TARGET DATA", True, COLOR_ACCENT), (ui_x + 25, 40))
                self.screen.blit(f_std.render(f"ID: AEGIS_{self.selected.id:03d}", True, COLOR_WHITE), (ui_x + 25, 80))
                self.screen.blit(f_std.render(f"HOSTILITY: {int(self.selected.hostility*100)}%", True, COLOR_WHITE), (ui_x + 25, 110))
                self.screen.blit(f_std.render(f"ACTIVITY: ", True, COLOR_ACCENT), (ui_x + 25, 150))
                self.screen.blit(f_std.render(self.selected.activity, True, COLOR_WHITE), (ui_x + 25, 175))
                
                msg = "OVERRIDE ACTIVE (ARROWS)" if self.selected.has_app else "HACK FAILED: NO APP"
                self.screen.blit(f_std.render(msg, True, (150, 150, 150)), (ui_x + 25, 250))

    def draw_scanlines(self):
        for y in range(0, HEIGHT, 4):
            pygame.draw.line(self.screen, (0, 0, 0, 50), (0, y), (WIDTH, y))

    def run(self):
        while True:
            self.screen.fill(COLOR_BG)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    if mx < MAP_AREA:
                        # Convert screen click to zoomed world coordinates
                        zoom = self.camera.current_zoom
                        world_mx = (mx / MAP_AREA) * (MAP_AREA / zoom) + self.camera.offset_x
                        world_my = (my / HEIGHT) * (HEIGHT / zoom) + self.camera.offset_y
                        self.selected = None
                        for a in self.agents:
                            if math.hypot(a.x - world_mx, a.y - world_my) < 15:
                                self.selected = a
                                break

            target_pos = (self.selected.x, self.selected.y) if self.selected else None
            self.camera.update(target_pos)
            
            for a in self.agents:
                a.update(is_controlled=(a == self.selected and a.has_app))

            self.draw_world()
            self.draw_ui()
            self.draw_scanlines()
            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    Simulation().run()