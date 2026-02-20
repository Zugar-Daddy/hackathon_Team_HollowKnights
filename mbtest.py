import pygame
import random
import math
import os

# --- SETTINGS & CONSTANTS ---
WIDTH, HEIGHT = 1100, 700
UI_WIDTH = 300
MAP_AREA = WIDTH - UI_WIDTH
FPS = 60
AGENT_COUNT = 40
APP_CHANCE = 0.6  # 60% of population has the app

# Colors
COLOR_BLACK = (10, 10, 10)
COLOR_WHITE = (255, 255, 255)
COLOR_UI_BG = (20, 24, 30)
COLOR_ACCENT = (0, 255, 200)

# --- ACTIVITY POOL ---
GTA_ACTIVITIES = [
    "Eating a Big Number 5",
    "Ignoring a call from Roman",
    "Looking for a Sprunk machine",
    "Driving to the Pay 'n' Spray",
    "Heading to the Malibu Club",
    "Buying a Cluckin' Bell Salad",
    "Stuck in traffic on LS Freeway",
    "Browsing Ammu-Nation catalog"
]

class MapHandler:
    def __init__(self):
        self.surface = None
        self.mask = None
        self.load_map()

    def load_map(self):
        if os.path.exists("map.png"):
            self.surface = pygame.image.load("map.png").convert()
            # Scale to fit map area
            self.surface = pygame.transform.scale(self.surface, (MAP_AREA, HEIGHT))
        else:
            # Fallback: Create a simple procedural "city" if map.png is missing
            self.surface = pygame.Surface((MAP_AREA, HEIGHT))
            self.surface.fill(COLOR_BLACK)
            # Draw some "white spaces" (streets)
            pygame.draw.rect(self.surface, COLOR_WHITE, (50, 50, 100, 600))
            pygame.draw.rect(self.surface, COLOR_WHITE, (50, 300, 700, 100))
            pygame.draw.rect(self.surface, COLOR_WHITE, (600, 50, 100, 600))

        # Create a mask for collision (white = walkable)
        self.mask = pygame.mask.from_threshold(self.surface, COLOR_WHITE, (10, 10, 10))

    def is_walkable(self, x, y):
        if 0 <= x < MAP_AREA and 0 <= y < HEIGHT:
            return self.mask.get_at((int(x), int(y)))
        return False

class Agent:
    def __init__(self, id, map_handler):
        self.id = id
        self.mh = map_handler
        self.has_app = random.random() < APP_CHANCE
        self.type = random.choice(["NPC", "COP", "FELON"])
        
        # Stats
        self.hostility = random.uniform(0.1, 0.4)
        self.ideology = random.uniform(-1, 1)
        self.activity = random.choice(GTA_ACTIVITIES)
        
        # Physics
        self.radius = 6
        self.spawn()
        self.vel_x = random.uniform(-2, 2)
        self.vel_y = random.uniform(-2, 2)

    def spawn(self):
        # Find a valid white space to start
        for _ in range(100):
            rx = random.randint(0, MAP_AREA)
            ry = random.randint(0, HEIGHT)
            if self.mh.is_walkable(rx, ry):
                self.x, self.y = rx, ry
                return
        self.x, self.y = 100, 100 # Safety fallback

    def update(self):
        next_x = self.x + self.vel_x
        next_y = self.y + self.vel_y

        # Map Boundary / Wall Collision
        if not self.mh.is_walkable(next_x, next_y):
            self.vel_x *= -1
            self.vel_y *= -1
        else:
            self.x = next_x
            self.y = next_y

    def draw(self, screen, is_selected):
        # Color based on hostility (Green -> Red)
        r = int(255 * self.hostility)
        g = int(255 * (1 - self.hostility))
        color = (r, g, 50)

        if self.has_app:
            pygame.draw.circle(screen, COLOR_WHITE, (int(self.x), int(self.y)), self.radius + 2, 1)
        
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)
        
        if is_selected:
            pygame.draw.circle(screen, COLOR_ACCENT, (int(self.x), int(self.y)), self.radius + 5, 2)

class Simulation:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("AEGIS - Surveillance & Harmony")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Courier", 14)
        self.header_font = pygame.font.SysFont("Courier", 18, bold=True)
        
        self.mh = MapHandler()
        self.agents = [Agent(i, self.mh) for i in range(AGENT_COUNT)]
        self.selected = None

    def handle_collisions(self):
        # Basic elastic collision
        for i, a1 in enumerate(self.agents):
            for a2 in self.agents[i+1:]:
                dx = a1.x - a2.x
                dy = a1.y - a2.y
                dist = math.hypot(dx, dy)
                if dist < a1.radius + a2.radius:
                    # Swap velocities (simplified bounce)
                    a1.vel_x, a2.vel_x = a2.vel_x, a1.vel_x
                    a1.vel_y, a2.vel_y = a2.vel_y, a1.vel_y
                    
                    # Social Interaction Logic
                    if a1.hostility > 0.7 and random.random() < 0.1:
                        a2.hostility = min(1.0, a2.hostility + 0.1)

    def draw_ui(self):
        ui_rect = pygame.Rect(MAP_AREA, 0, UI_WIDTH, HEIGHT)
        pygame.draw.rect(self.screen, COLOR_UI_BG, ui_rect)
        pygame.draw.line(self.screen, COLOR_ACCENT, (MAP_AREA, 0), (MAP_AREA, HEIGHT), 2)

        x_off = MAP_AREA + 20
        if self.selected:
            title = "DATA STREAM: ENROLLED" if self.selected.has_app else "DATA STREAM: ENCRYPTED"
            color = COLOR_ACCENT if self.selected.has_app else (255, 50, 50)
            
            self.screen.blit(self.header_font.render(title, True, color), (x_off, 30))
            
            if self.selected.has_app:
                stats = [
                    f"ID: AGENT_{self.selected.id:04d}",
                    f"CLASS: {self.selected.type}",
                    f"HOSTILITY: {int(self.selected.hostility * 100)}%",
                    f"IDEOLOGY: {self.selected.ideology:.2f}",
                    "",
                    "CURRENT ACTIVITY:",
                    f"> {self.selected.activity}"
                ]
                for i, text in enumerate(stats):
                    self.screen.blit(self.font.render(text, True, COLOR_WHITE), (x_off, 80 + (i * 25)))
                
                # Peacemaker Button
                pygame.draw.rect(self.screen, (0, 100, 80), (x_off, 400, 200, 40))
                self.screen.blit(self.font.render("ACTIVATE PEACEMAKER", True, COLOR_WHITE), (x_off + 15, 412))
            else:
                self.screen.blit(self.font.render("TARGET NOT ENROLLED IN AEGIS", True, (150, 150, 150)), (x_off, 80))
                self.screen.blit(self.font.render("FREE WILL DETECTED", True, (150, 150, 150)), (x_off, 100))
        else:
            self.screen.blit(self.font.render("SELECT A TARGET ON MAP", True, (100, 100, 100)), (x_off, HEIGHT // 2))

    def run(self):
        running = True
        while running:
            self.screen.blit(self.mh.surface, (0, 0))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    self.selected = None
                    for a in self.agents:
                        if math.hypot(a.x - mx, a.y - my) < 15:
                            self.selected = a
                            break

            self.handle_collisions()
            for a in self.agents:
                a.update()
                a.draw(self.screen, self.selected == a)

            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    sim = Simulation()
    sim.run()