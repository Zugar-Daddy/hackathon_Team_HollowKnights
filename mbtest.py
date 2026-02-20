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
EYE_FADE_TIME = 4.0 

# Colors
COLOR_BG = (3, 5, 8)
COLOR_WHITE = (255, 255, 255)
COLOR_ACCENT = (0, 255, 180)
COLOR_DANGER = (255, 45, 45)
COLOR_UI_PANEL = (10, 12, 18)

# --- HELPER ---
def clamp_color(val):
    return max(0, min(255, int(val)))

LOG_PHRASES = [
    "Conflict detected: Hostility++",
    "Social friction: Anxiety levels rising",
    "Aegis Protocol: Subliminal calming active",
    "Data Packet intercepted: Subject hungry",
    "Proximity Alert: Potential radicalization",
    "Interaction Log: Mundane chatter",
    "Aegis Sync: App user influencing peer"
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
            for i in range(0, MAP_AREA, 200):
                pygame.draw.rect(self.surface, COLOR_WHITE, (i, 0, 60, HEIGHT))
            for i in range(0, HEIGHT, 200):
                pygame.draw.rect(self.surface, COLOR_WHITE, (0, i, MAP_AREA, 60))

class Agent:
    def __init__(self, id, map_handler):
        self.id = id
        self.mh = map_handler
        self.has_app = random.random() < 0.6
        self.hostility = random.uniform(0.0, 1.0)
        self.radius = 8
        self.x, self.y = 0.0, 0.0
        self.spawn()
        self.angle = random.choice([0, 90, 180, 270])
        self.speed = random.uniform(1.2, 2.5)
        self.state = "WALKING"
        self.timer = 0
        self.activity = random.choice(["Eating No. 5", "Ignoring Roman", "Seeking Sprunk"])

    def spawn(self):
        for _ in range(1000):
            rx, ry = random.randint(10, MAP_AREA-10), random.randint(10, HEIGHT-10)
            if self.mh.mask.get_at((rx, ry)):
                self.x, self.y = float(rx), float(ry)
                return
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
                    self.state = "IDLE"; self.timer = random.randint(30, 90)
                rad = math.radians(self.angle)
                self.x += math.cos(rad) * self.speed
                self.y += math.sin(rad) * self.speed

        if not (0 <= self.x < MAP_AREA and 0 <= self.y < HEIGHT) or not self.mh.mask.get_at((int(self.x), int(self.y))):
            self.x, self.y = old_x, old_y
            self.angle = random.choice([0, 90, 180, 270])

        for other in agents:
            if other == self: continue
            dist = math.hypot(self.x - other.x, self.y - other.y)
            if dist < self.radius + other.radius:
                overlap = (self.radius + other.radius) - dist
                angle = math.atan2(self.y - other.y, self.x - other.x)
                self.x += math.cos(angle) * overlap
                self.y += math.sin(angle) * overlap
                return other 
        return None

class Camera:
    def __init__(self):
        self.x, self.y = 0, 0
        self.zoom = 1.0
        self.target_zoom = 1.0

    def update(self, target_agent):
        if target_agent:
            self.target_zoom = 2.0
            tx = target_agent.x - (MAP_AREA / 2) / self.target_zoom
            ty = target_agent.y - (HEIGHT / 2) / self.target_zoom
            self.x += (tx - self.x) * 0.1
            self.y += (ty - self.y) * 0.1
        else:
            self.target_zoom = 1.0
            self.x += (0 - self.x) * 0.1
            self.y += (0 - self.y) * 0.1
        
        self.zoom += (self.target_zoom - self.zoom) * 0.1
        # Boundary clamping
        self.x = max(0, min(self.x, MAP_AREA - MAP_AREA/self.zoom))
        self.y = max(0, min(self.y, HEIGHT - HEIGHT/self.zoom))

class Simulation:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
        self.mh = MapHandler()
        self.camera = Camera()
        self.agents = [Agent(i, self.mh) for i in range(AGENT_COUNT)]
        self.selected = None
        self.logs = ["Aegis Online...", "Protocol: Surveillance"]
        self.clock = pygame.time.Clock()
        
        self.eye_img = pygame.Surface((300, 300), pygame.SRCALPHA)
        pygame.draw.ellipse(self.eye_img, (255, 255, 255, 120), (20, 80, 260, 140))
        pygame.draw.circle(self.eye_img, (0, 255, 180, 180), (150, 150), 50)
        self.eye_timer = 0.0

    def add_log(self, msg):
        self.logs.append(msg); 
        if len(self.logs) > 18: self.logs.pop(0)

    def draw(self):
        # 1. Render World to a Surface
        world_surf = pygame.Surface((MAP_AREA, HEIGHT))
        world_surf.blit(self.mh.surface, (0,0))
        for a in self.agents:
            r = clamp_color(255 * a.hostility)
            g = clamp_color(255 * (1 - a.hostility))
            pygame.draw.circle(world_surf, (r, g, 50), (int(a.x), int(a.y)), a.radius)
            if a.has_app: pygame.draw.circle(world_surf, COLOR_WHITE, (int(a.x), int(a.y)), a.radius+2, 1)

        # 2. Camera Transform
        zoom = self.camera.zoom
        view_w, view_h = int(MAP_AREA / zoom), int(HEIGHT / zoom)
        sub_rect = pygame.Rect(self.camera.x, self.camera.y, view_w, view_h)
        view_surf = world_surf.subsurface(sub_rect)
        scaled_view = pygame.transform.scale(view_surf, (MAP_AREA, HEIGHT))
        self.screen.blit(scaled_view, (0, 0))

        # 3. UI and Eye
        self.draw_ui()
        if self.eye_timer > 0:
            self.eye_timer -= 1/FPS
            alpha = clamp_color(math.sin((self.eye_timer/EYE_FADE_TIME) * math.pi) * 255)
            eye_copy = self.eye_img.copy()
            eye_copy.fill((255,255,255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
            self.screen.blit(eye_copy, (MAP_AREA//2 - 150, HEIGHT//2 - 150))

    def draw_ui(self):
        pygame.draw.rect(self.screen, COLOR_UI_PANEL, (MAP_AREA, 0, UI_WIDTH, 320))
        pygame.draw.rect(self.screen, (5, 5, 10), (MAP_AREA, 322, UI_WIDTH, HEIGHT - 322))
        f_std = pygame.font.SysFont("Courier", 14)
        if self.selected:
            h_val = self.selected.hostility
            h_col = (clamp_color(255*h_val), clamp_color(255*(1-h_val)), 0)
            self.screen.blit(f_std.render(f"ID: {self.selected.id:03d}", True, COLOR_ACCENT), (MAP_AREA+20, 40))
            pygame.draw.rect(self.screen, h_col, (MAP_AREA+20, 100, int(200*h_val), 10))
            self.screen.blit(f_std.render(f"ACTIVITY: {self.selected.activity}", True, COLOR_WHITE), (MAP_AREA+20, 140))
        for i, log in enumerate(reversed(self.logs)):
            color = COLOR_ACCENT if i == 0 else (130, 130, 130)
            self.screen.blit(f_std.render(f"> {log}", True, color), (MAP_AREA+15, HEIGHT - 30 - (i * 20)))

    def run(self):
        while True:
            self.screen.fill(COLOR_BG)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    if mx < MAP_AREA:
                        world_mx = (mx / MAP_AREA) * (MAP_AREA / self.camera.zoom) + self.camera.x
                        world_my = (my / HEIGHT) * (HEIGHT / self.camera.zoom) + self.camera.y
                        old_s = self.selected; self.selected = None
                        for a in self.agents:
                            if math.hypot(a.x - world_mx, a.y - world_my) < 15:
                                if a.has_app:
                                    self.selected = a
                                    if self.selected != old_s: self.eye_timer = EYE_FADE_TIME; self.add_log(f"Linked: {a.id}")
                                else: self.add_log("Encryption Error")
                                break
            self.camera.update(self.selected)
            for a in self.agents:
                hit = a.update(a == self.selected, self.agents)
                if hit and random.random() < 0.05:
                    phrase = random.choice(LOG_PHRASES)
                    self.add_log(phrase)
                    if "++" in phrase: a.hostility = min(1.0, a.hostility + 0.1)
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    Simulation().run()
