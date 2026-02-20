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
COLOR_WHITE = (255, 255, 255)
COLOR_ACCENT = (0, 255, 180)
COLOR_DANGER = (255, 45, 45)
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
        if os.path.exists("mbmap.png"):
            img = pygame.image.load("mbmap.png").convert()
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
        # Ensure x and y exist immediately
        self.x, self.y = 0, 0
        self.spawn()
        
        self.angle = random.choice([0, 90, 180, 270])
        self.speed = random.uniform(1.2, 2.8)
        self.state = "WALKING"
        self.timer = 0
        self.activity = random.choice(["Eating No. 5", "Ignoring Roman", "Seeking Sprunk"])

    def spawn(self):
        for _ in range(1000):
            rx, ry = random.randint(10, MAP_AREA-10), random.randint(10, HEIGHT-10)
            if self.mh.is_walkable(rx, ry):
                self.x, self.y = float(rx), float(ry)
                return
        # Hard fallback to center if no white space found
        self.x, self.y = float(MAP_AREA//2), float(HEIGHT//2)

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

        # Agent Collision
        for other in agents:
            if other == self: continue
            dist = math.hypot(self.x - other.x, self.y - other.y)
            if dist < self.radius + other.radius:
                # Resolve overlap
                overlap = (self.radius + other.radius) - dist
                angle = math.atan2(self.y - other.y, self.x - other.x)
                self.x += math.cos(angle) * overlap
                self.y += math.sin(angle) * overlap
                return other 
        return None

class Simulation:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
        pygame.display.set_caption("AEGIS SURVEILLANCE")
        self.mh = MapHandler()
        self.agents = [Agent(i, self.mh) for i in range(AGENT_COUNT)]
        self.selected = None
        self.logs = ["Aegis System Online...", "Searching for unencrypted signals..."]
        self.clock = pygame.time.Clock()
        
        # Eye Overlay Surface
        self.eye_img = pygame.Surface((300, 300), pygame.SRCALPHA)
        pygame.draw.ellipse(self.eye_img, (255, 255, 255, 120), (20, 80, 260, 140))
        pygame.draw.circle(self.eye_img, (0, 255, 180, 180), (150, 150), 50)
        pygame.draw.circle(self.eye_img, (0, 0, 0, 200), (150, 150), 20)
        
        self.eye_alpha = 0
        self.eye_timer = 0.0

    def add_log(self, msg):
        self.logs.append(msg)
        if len(self.logs) > 18: self.logs.pop(0)

    def draw_ui(self):
        # UI Structure
        pygame.draw.rect(self.screen, COLOR_UI_PANEL, (MAP_AREA, 0, UI_WIDTH, 320))
        pygame.draw.line(self.screen, COLOR_ACCENT, (MAP_AREA, 320), (WIDTH, 320), 2)
        pygame.draw.rect(self.screen, (5, 5, 10), (MAP_AREA, 322, UI_WIDTH, HEIGHT - 322))
        
        f_hdr = pygame.font.SysFont("Courier", 18, bold=True)
        f_std = pygame.font.SysFont("Courier", 14)

        if self.selected:
            self.screen.blit(f_hdr.render("SIGNAL: CONNECTED", True, COLOR_ACCENT), (MAP_AREA+20, 20))
            self.screen.blit(f_std.render(f"ENTITY_ID: {self.selected.id:03d}", True, COLOR_WHITE), (MAP_AREA+20, 60))
            
            # Hostility Bar
            h_val = self.selected.hostility
            r_ui = max(0,min(255,int(255*h_val)))
            g_ui = max(0,min(255,int(255* (1-h_val))))
            h_col = (r_ui,g_ui,0)
            self.screen.blit(f_std.render(f"THREAT LEVEL:", True, COLOR_WHITE), (MAP_AREA+20, 95))
            pygame.draw.rect(self.screen, (40, 40, 40), (MAP_AREA+20, 115, 200, 10))
            pygame.draw.rect(self.screen, h_col, (MAP_AREA+20, 115, int(200*h_val), 10))
            
            self.screen.blit(f_std.render(f"ACTIVITY: {self.selected.activity}", True, COLOR_WHITE), (MAP_AREA+20, 145))
            self.screen.blit(f_std.render("> OVERRIDE ENABLED", True, COLOR_ACCENT), (MAP_AREA+20, 280))
        else:
            self.screen.blit(f_hdr.render("NO SIGNAL SELECTED", True, (100, 100, 100)), (MAP_AREA+20, 20))

        # Render Log
        for i, log in enumerate(reversed(self.logs)):
            color = (150, 150, 150) if i > 0 else COLOR_ACCENT
            self.screen.blit(f_std.render(f"> {log}", True, color), (MAP_AREA+15, HEIGHT - 30 - (i * 20)))

    def update_eye(self):
        if self.eye_timer > 0:
            self.eye_timer -= 1/FPS
            progress = self.eye_timer / EYE_FADE_TIME
            # Smooth bell-curve alpha
            alpha = max(0,min(255,int(math.sin(progress * math.pi) * 200)))
            
            temp_eye = self.eye_img.copy()
            temp_eye.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
            self.screen.blit(temp_eye, (MAP_AREA//2 - 150, HEIGHT//2 - 150))

    def run(self):
        while True:
            self.screen.fill(COLOR_BG)
            self.screen.blit(self.mh.surface, (0, 0))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    if mx < MAP_AREA:
                        old_s = self.selected
                        self.selected = None
                        for a in self.agents:
                            if math.hypot(a.x - mx, a.y - my) < 20:
                                if a.has_app:
                                    self.selected = a
                                    if self.selected != old_s:
                                        self.eye_timer = EYE_FADE_TIME
                                        self.add_log(f"Linked to Agent {a.id}")
                                else:
                                    self.add_log("Access Denied: Unencrypted Target")
                                break

            # Update Agents
            for a in self.agents:
                target = a.update(a == self.selected, self.agents)
                if target and random.random() < 0.05:
                    if a == self.selected or target == self.selected:
                        phrase = random.choice(LOG_PHRASES)
                        self.add_log(phrase)
                        if "Hostility++" in phrase:
                            a.hostility = min(1.0, a.hostility + 0.1)

            # Draw Agents
            for a in self.agents:
                r = max(0,min(255,int(255*a.hostility)))
                g = max(0,min(255,int(255* (1-a.hostility))))

                color = (r,g,50)
                pos = (int(a.x), int(a.y))
                pygame.draw.circle(self.screen, color, pos, a.radius)
                if a.has_app: pygame.draw.circle(self.screen, COLOR_WHITE, pos, a.radius+2, 1)
                if a == self.selected: pygame.draw.circle(self.screen, COLOR_ACCENT, pos, a.radius+5, 2)

            self.draw_ui()
            self.update_eye()
            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    Simulation().run()