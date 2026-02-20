import pygame
import random
import math
import os

# --- SETTINGS ---
WIDTH, HEIGHT = 1150, 750
UI_WIDTH = 320
MAP_AREA = WIDTH - UI_WIDTH
FPS = 60
AGENT_COUNT = 40
EYE_FADE_TIME = 2.0  # Seconds for the eye overlay to fade

# Colors
COLOR_BG = (3, 5, 8)
COLOR_WHITE = (240, 240, 240)
COLOR_ACCENT = (0, 255, 180)
COLOR_DANGER = (255, 45, 45)
COLOR_GRID = (15, 20, 30)
COLOR_UI_PANEL = (10, 12, 18)

# --- INTERACTION PHRASES ---
LOG_PHRASES = [
    "Conflict detected: Hostility++",
    "Social friction: Anxiety levels rising",
    "Aegis Protocol: Subliminal calming active",
    "Data Packet intercepted: Subject hungry",
    "Proximity Alert: Potential radicalization",
    "Interaction Log: Mundane chatter",
    "Ideology check: Status Quo maintained",
    "Collision Event: Physical boundaries tested",
    "Aegis Sync: App user influencing peer",
    "Subject Variance: Behavior within 5% of norm"
]

class MapHandler:
    def __init__(self):
        self.surface = pygame.Surface((MAP_AREA, HEIGHT))
        self.surface.fill((10, 10, 12))
        self.load_map()
        self.mask = pygame.mask.from_threshold(self.surface, COLOR_WHITE, (10, 10, 10))

    def load_map(self):
        if os.path.exists("map.png"):
            img = pygame.image.load("map.png").convert()
            self.surface = pygame.transform.scale(img, (MAP_AREA, HEIGHT))
        else:
            # Fallback Grid
            for i in range(0, MAP_AREA, 200):
                pygame.draw.rect(self.surface, COLOR_WHITE, (i, 0, 60, HEIGHT))
            for i in range(0, HEIGHT, 200):
                pygame.draw.rect(self.surface, COLOR_WHITE, (0, i, MAP_AREA, 60))

    def is_walkable(self, x, y):
        if 0 <= x < MAP_AREA and 0 <= y < HEIGHT:
            return self.mask.get_at((int(x), int(y)))
        return False

class Agent:
    def __init__(self, id, map_handler):
        self.id = id
        self.mh = map_handler
        self.has_app = random.random() < 0.6
        self.hostility = random.uniform(0.0, 1.0)
        self.radius = 8
        self.spawn()
        self.angle = random.choice([0, 90, 180, 270])
        self.speed = random.uniform(1.0, 2.5)
        self.state = "WALKING"
        self.timer = 0
        self.activity = random.choice(["Eating No. 5", "Ignoring Roman", "Seeking Sprunk"])

    def spawn(self):
        for _ in range(500):
            rx, ry = random.randint(10, MAP_AREA-10), random.randint(10, HEIGHT-10)
            if self.mh.is_walkable(rx, ry):
                self.x, self.y = rx, ry
                return

    def update(self, is_controlled, agents):
        old_x, old_y = self.x, self.y
        
        if is_controlled:
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            if keys[pygame.K_LEFT]: dx = -self.speed
            if keys[pygame.K_RIGHT]: dx = self.speed
            if keys[pygame.K_UP]: dy = -self.speed
            if keys[pygame.K_DOWN]: dy = self.speed
            self.x += dx
            self.y += dy
        else:
            if self.state == "IDLE":
                self.timer -= 1
                if self.timer <= 0: self.state = "WALKING"
            else:
                if random.random() < 0.005:
                    self.state = "IDLE"
                    self.timer = random.randint(30, 90)
                rad = math.radians(self.angle)
                self.x += math.cos(rad) * self.speed
                self.y += math.sin(rad) * self.speed

        # Wall Collision
        if not self.mh.is_walkable(self.x, self.y):
            self.x, self.y = old_x, old_y
            self.angle = random.choice([0, 90, 180, 270])

        # Agent Collision Logic (Even for controlled)
        for other in agents:
            if other == self: continue
            dist = math.hypot(self.x - other.x, self.y - other.y)
            if dist < self.radius + other.radius:
                # Push back
                overlap = (self.radius + other.radius) - dist
                angle = math.atan2(self.y - other.y, self.x - other.x)
                self.x += math.cos(angle) * overlap
                self.y += math.sin(angle) * overlap
                return other # Return the agent we hit for the log
        return None

class Simulation:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.mh = MapHandler()
        self.agents = [Agent(i, self.mh) for i in range(AGENT_COUNT)]
        self.selected = None
        self.logs = ["System Initialized...", "Awaiting User Input..."]
        self.clock = pygame.time.Clock()
        
        # Eye Overlay Setup
        self.eye_img = None
        if os.path.exists("eye.png"):
            self.eye_img = pygame.image.load("eye.png").convert_alpha()
        else:
            # Create a placeholder eye
            self.eye_img = pygame.Surface((200, 200), pygame.SRCALPHA)
            pygame.draw.ellipse(self.eye_img, (255, 255, 255, 150), (20, 50, 160, 100))
            pygame.draw.circle(self.eye_img, (0, 255, 180, 200), (100, 100), 40)
        
        self.eye_alpha = 0
        self.eye_timer = 0

    def add_log(self, msg):
        self.logs.append(msg)
        if len(self.logs) > 15: self.logs.pop(0)

    def draw_ui(self):
        # Stats Window (Top)
        pygame.draw.rect(self.screen, COLOR_UI_PANEL, (MAP_AREA, 0, UI_WIDTH, 300))
        pygame.draw.line(self.screen, COLOR_ACCENT, (MAP_AREA, 300), (WIDTH, 300), 2)
        
        # Log Window (Bottom)
        pygame.draw.rect(self.screen, (5, 5, 8), (MAP_AREA, 302, UI_WIDTH, HEIGHT - 302))
        
        f_hdr = pygame.font.SysFont("Courier", 18, bold=True)
        f_std = pygame.font.SysFont("Courier", 14)

        if self.selected:
            # Top Window Stats
            self.screen.blit(f_hdr.render("TARGET DATA", True, COLOR_ACCENT), (MAP_AREA + 20, 20))
            self.screen.blit(f_std.render(f"ID: {self.selected.id:03d}", True, COLOR_WHITE), (MAP_AREA+20, 60))
            host_col = (255, 255 - (255*self.selected.hostility), 0)
            self.screen.blit(f_std.render(f"HOSTILITY: {int(self.selected.hostility*100)}%", True, host_col), (MAP_AREA+20, 90))
            self.screen.blit(f_std.render(f"STATUS: {self.selected.activity}", True, COLOR_WHITE), (MAP_AREA+20, 120))
            self.screen.blit(f_std.render(f"APP INSTALLED: {self.selected.has_app}", True, COLOR_ACCENT), (MAP_AREA+20, 150))
        
        # Bottom Window Logs
        for i, log in enumerate(reversed(self.logs)):
            color = (150, 150, 150) if i > 0 else COLOR_ACCENT
            self.screen.blit(f_std.render(f"> {log}", True, color), (MAP_AREA+15, HEIGHT - 30 - (i * 22)))

    def handle_eye_effect(self):
        if self.eye_timer > 0:
            self.eye_timer -= 1/FPS
            # Fade in then out logic
            half = EYE_FADE_TIME / 2
            if self.eye_timer > half: # Fading in
                self.eye_alpha = int(255 * (1 - (self.eye_timer - half)/half))
            else: # Fading out
                self.eye_alpha = int(255 * (self.eye_timer / half))
            
            temp_eye = self.eye_img.copy()
            temp_eye.fill((255, 255, 255, self.eye_alpha), special_flags=pygame.BLEND_RGBA_MULT)
            self.screen.blit(temp_eye, (MAP_AREA//2 - 100, HEIGHT//2 - 100))

    def run(self):
        while True:
            self.screen.fill(COLOR_BG)
            self.screen.blit(self.mh.surface, (0, 0))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    old_selected = self.selected
                    self.selected = None
                    for a in self.agents:
                        if math.hypot(a.x - mx, a.y - my) < 20:
                            if a.has_app:
                                self.selected = a
                                if self.selected != old_selected:
                                    self.eye_timer = EYE_FADE_TIME
                                    self.add_log(f"Linked to Agent {a.id}")
                            else:
                                self.add_log("Connection Refused: Target Encrypted")
                            break

            # Update Agents
            for a in self.agents:
                collided_with = a.update(a == self.selected, self.agents)
                if collided_with and random.random() < 0.05: # Log some collisions
                    if a == self.selected or collided_with == self.selected:
                        self.add_log(random.choice(LOG_PHRASES))
                        if collided_with.hostility > 0.7:
                            a.hostility = min(1.0, a.hostility + 0.05)
                            self.add_log("Hostility++ via proximity")

            # Draw
            for a in self.agents:
                color = (int(255*a.hostility), int(255*(1-a.hostility)), 50)
                pygame.draw.circle(self.screen, color, (int(a.x), int(a.y)), a.radius)
                if a.has_app: pygame.draw.circle(self.screen, COLOR_WHITE, (int(a.x), int(a.y)), a.radius+2, 1)
                if a == self.selected: pygame.draw.circle(self.screen, COLOR_ACCENT, (int(a.x), int(a.y)), a.radius+5, 2)

            self.draw_ui()
            self.handle_eye_effect()
            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    Simulation().run()