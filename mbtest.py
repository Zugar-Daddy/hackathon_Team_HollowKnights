import pygame
import random
import math
import os

# --- SETTINGS & CONSTANTS ---
WIDTH, HEIGHT = 1100, 700
UI_WIDTH = 300
MAP_AREA = WIDTH - UI_WIDTH
FPS = 60
AGENT_COUNT = 50
APP_CHANCE = 0.6 

# Colors
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_UI_BG = (15, 15, 20)
COLOR_ACCENT = (0, 255, 150)
COLOR_DANGER = (255, 50, 50)

# --- ACTIVITY POOL ---
GTA_ACTIVITIES = [
    "Eating a Big Number 5", "Ignoring a call from Roman",
    "Looking for a Sprunk machine", "Driving to the Pay 'n' Spray",
    "Heading to the Malibu Club", "Buying a Cluckin' Bell Salad",
    "Stuck in traffic on LS Freeway", "Browsing Ammu-Nation catalog",
    "Waiting for a train at Unity Station", "Taking selfies at Vinewood Sign"
]

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
            # Generate a "City Grid" fallback if map.png is missing
            self.surface = pygame.Surface((MAP_AREA, HEIGHT))
            self.surface.fill(COLOR_BLACK)
            # Vertical streets
            for x in range(50, MAP_AREA, 150):
                pygame.draw.rect(self.surface, COLOR_WHITE, (x, 0, 40, HEIGHT))
            # Horizontal streets
            for y in range(50, HEIGHT, 150):
                pygame.draw.rect(self.surface, COLOR_WHITE, (0, y, MAP_AREA, 40))

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
        self.hostility = random.uniform(0.1, 0.4)
        self.activity = random.choice(GTA_ACTIVITIES)
        
        self.radius = 6
        self.spawn()
        
        # Movement Logic
        self.angle = random.choice([0, 90, 180, 270]) # Fixed initial angles
        self.speed = random.uniform(1.0, 2.2)
        self.state = "WALKING" # WALKING or IDLE
        self.timer = 0
        
    def spawn(self):
        for _ in range(500):
            rx, ry = random.randint(0, MAP_AREA), random.randint(0, HEIGHT)
            if self.mh.is_walkable(rx, ry):
                self.x, self.y = rx, ry
                return
        self.x, self.y = 100, 100

    def update(self):
        if self.state == "IDLE":
            self.timer -= 1
            if self.timer <= 0:
                self.state = "WALKING"
                # Pick a new direction after standing still
                self.angle = random.choice([0, 90, 180, 270])
        
        elif self.state == "WALKING":
            # Random chance to stop and "act like a human"
            if random.random() < 0.005: 
                self.state = "IDLE"
                self.timer = random.randint(30, 120) # Stay still for 0.5 to 2 seconds
                return

            rad = math.radians(self.angle)
            dx = math.cos(rad) * self.speed
            dy = math.sin(rad) * self.speed
            
            # Check collision with "black" space
            if self.mh.is_walkable(self.x + dx * 5, self.y + dy * 5):
                self.x += dx
                self.y += dy
            else:
                # Instead of bouncing like a particle, seek a new fixed angle (turn corner)
                possible_angles = [0, 90, 180, 270]
                random.shuffle(possible_angles)
                for a in possible_angles:
                    a_rad = math.radians(a)
                    if self.mh.is_walkable(self.x + math.cos(a_rad)*10, self.y + math.sin(a_rad)*10):
                        self.angle = a
                        break

    def draw(self, screen, is_selected):
        # Color based on hostility gradient
        r = int(255 * self.hostility)
        g = int(255 * (1 - self.hostility))
        color = (r, g, 50)

        if self.has_app:
            pygame.draw.circle(screen, (200, 200, 200), (int(self.x), int(self.y)), self.radius + 3, 1)
        
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)
        
        if is_selected:
            pygame.draw.circle(screen, COLOR_ACCENT, (int(self.x), int(self.y)), self.radius + 6, 2)

class Simulation:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("AEGIS SURVEILLANCE - NPC FREE WILL SIM")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Verdana", 14)
        self.header_font = pygame.font.SysFont("Verdana", 16, bold=True)
        
        self.mh = MapHandler()
        self.agents = [Agent(i, self.mh) for i in range(AGENT_COUNT)]
        self.selected = None

    def run(self):
        running = True
        while running:
            # Draw Background Map
            self.screen.blit(self.mh.surface, (0, 0))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    # Area button logic (Peacemaker/Riot)
                    if mx > MAP_AREA:
                        self.check_ui_click(my)
                    else:
                        # Blob Selection
                        self.selected = None
                        for a in self.agents:
                            if math.hypot(a.x - mx, a.y - my) < 15:
                                self.selected = a
                                break

            # Update and Draw Agents
            for a in self.agents:
                a.update()
                a.draw(self.screen, self.selected == a)

            self.draw_dashboard()
            pygame.display.flip()
            self.clock.tick(FPS)

    def check_ui_click(self, my):
        if not self.selected or not self.selected.has_app: return
        # Logic for buttons in side panel
        if 400 <= my <= 440:
            self.selected.hostility = max(0.0, self.selected.hostility - 0.2)
            self.selected.activity = "Consuming Aegis Content [Calming]"

    def draw_dashboard(self):
        # UI Sidebar Background
        pygame.draw.rect(self.screen, COLOR_UI_BG, (MAP_AREA, 0, UI_WIDTH, HEIGHT))
        pygame.draw.line(self.screen, (50, 50, 60), (MAP_AREA, 0), (MAP_AREA, HEIGHT), 2)

        x_start = MAP_AREA + 20
        # Global Metrics
        avg_host = sum(a.hostility for a in self.agents) / len(self.agents)
        self.screen.blit(self.header_font.render("SYSTEM STABILITY", True, (100, 100, 120)), (x_start, 20))
        pygame.draw.rect(self.screen, (40, 40, 50), (x_start, 45, 250, 15))
        pygame.draw.rect(self.screen, COLOR_ACCENT, (x_start, 45, 250 * (1-avg_host), 15))

        # Selected Target Info
        if self.selected:
            pygame.draw.line(self.screen, (50, 50, 60), (x_start, 100), (x_start+250, 100))
            if self.selected.has_app:
                self.screen.blit(self.header_font.render(f"TARGET: AGENT_{self.selected.id}", True, COLOR_ACCENT), (x_start, 120))
                self.screen.blit(self.font.render(f"STATUS: {self.selected.activity}", True, COLOR_WHITE), (x_start, 150))
                self.screen.blit(self.font.render(f"HOSTILITY: {int(self.selected.hostility*100)}%", True, COLOR_WHITE), (x_start, 180))
                
                # The Peacemaker Button
                btn_rect = pygame.Rect(x_start, 400, 250, 40)
                pygame.draw.rect(self.screen, (0, 60, 50), btn_rect)
                pygame.draw.rect(self.screen, COLOR_ACCENT, btn_rect, 1)
                self.screen.blit(self.font.render("DEPLOY HARMONY FEED", True, COLOR_WHITE), (x_start+45, 412))
            else:
                self.screen.blit(self.header_font.render("ACCESS DENIED", True, COLOR_DANGER), (x_start, 120))
                self.screen.blit(self.font.render("Unregistered Signal Detected.", True, (150, 150, 150)), (x_start, 150))
                self.screen.blit(self.font.render("Free Will override unavailable.", True, (150, 150, 150)), (x_start, 175))
        else:
            msg = self.font.render("Select a signal to monitor...", True, (80, 80, 90))
            self.screen.blit(msg, (x_start, HEIGHT // 2))

if __name__ == "__main__":
    Simulation().run()