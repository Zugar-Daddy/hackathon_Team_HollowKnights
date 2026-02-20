import pygame
import random
import math
import os

# --- SETTINGS ---
WIDTH, HEIGHT = 1150, 750
UI_WIDTH = 320
MAP_AREA = WIDTH - UI_WIDTH
FPS = 60
AGENT_COUNT = 45
EYE_FADE_TIME = 2.0  # Time for eye animation

# Surveillance Aesthetic Colors
COLOR_BG = (2, 4, 8)
COLOR_WHITE = (255, 255, 255)
COLOR_ACCENT = (0, 255, 180)  
COLOR_DANGER = (255, 45, 45)  
COLOR_UI_PANEL = (10, 12, 18)

# Pedestrian Settings
MINSPEED = .6
MAXSPEED = 1.5

# --- SENTIENT PHRASES ---
GTA_PHRASES = [
    "Ordering a Number 9 Large...", "Ignoring a call from Roman.",
    "Looking for a Sprunk machine.", "Heading to the Malibu Club.",
    "Buying a Cluckin' Bell Salad.", "Browsing Ammu-Nation catalog.",
    "Taking a selfie at Vinewood.", "Driving a slow Faggio.",
    "Stuck in a 1-star chase.", "Watching Weazel News."
]

RIOT_PHRASES = [
    "Wasted. Re-spawning in anger.", "Forget the bowling, Roman!",
    "Commiting a hit and run.", "Grand Theft Auto in progress.",
    "Busting a Cluckin' Bell window.", "Aggressive jaywalking."
]

def clamp(val, min_v, max_v):
    return max(min_v, min(max_v, int(val)))

# --- NOTIFICATION SYSTEM ---
class Notification:
    def __init__(self, text, duration=3.0):
        self.text = text
        self.duration = duration * FPS
        self.timer = self.duration
        self.alpha = 255

    def update(self):
        self.timer -= 1
        self.alpha = clamp((self.timer / self.duration) * 255, 0, 255)
        return self.timer > 0

# --- PRETTY PULSE SYSTEM ---
class Pulse:
    def __init__(self, x, y, color, max_radius=30):
        self.x, self.y = x, y
        self.color = color
        self.radius = 2
        self.max_radius = max_radius
        self.alpha = 255

    def update(self):
        self.radius += 2.5
        self.alpha -= 10  
        return self.alpha > 0

    def draw(self, surface):
        if self.alpha > 0:
            s = pygame.Surface((int(self.radius*2), int(self.radius*2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, self.alpha), (int(self.radius), int(self.radius)), int(self.radius), 2)
            surface.blit(s, (int(self.x - self.radius), int(self.y - self.radius)))

# --- CAMERA ---
class Camera:
    def __init__(self):
        self.x, self.y = 0, 0
        self.zoom, self.target_zoom = 1.0, 1.0

    def update(self, target):
        if target:
            self.target_zoom = 2.2
            tx = target.x - (MAP_AREA / 2) / self.target_zoom
            ty = target.y - (HEIGHT / 2) / self.target_zoom
            self.x += (tx - self.x) * 0.1
            self.y += (ty - self.y) * 0.1
        else:
            self.target_zoom = 1.0
            self.x += (0 - self.x) * 0.1
            self.y += (0 - self.y) * 0.1
        
        self.zoom += (self.target_zoom - self.zoom) * 0.1
        self.x = max(0, min(self.x, MAP_AREA - MAP_AREA/self.zoom))
        self.y = max(0, min(self.y, HEIGHT - HEIGHT/self.zoom))

class MapHandler:
    def __init__(self):
        self.surface = pygame.Surface((MAP_AREA, HEIGHT))
        self.load_map()
        self.mask = pygame.mask.from_threshold(self.surface, COLOR_WHITE, (10, 10, 10))

    def load_map(self):
        if os.path.exists("anothermap.png"):
            img = pygame.image.load("anothermap.png").convert()
            self.surface = pygame.transform.scale(img, (MAP_AREA, HEIGHT))
        else:
            self.surface.fill((10, 10, 12))
            for i in range(0, MAP_AREA, 180): pygame.draw.rect(self.surface, COLOR_WHITE, (i, 0, 40, HEIGHT))
            for i in range(0, HEIGHT, 180): pygame.draw.rect(self.surface, COLOR_WHITE, (0, i, MAP_AREA, 40))

class Agent:
    def __init__(self, id, mh):
        self.id, self.mh = id, mh
        self.has_app = random.random() < 0.6
        self.hostility = random.uniform(0.1, 0.4)
        self.radius = 3
        self.x, self.y = 0.0, 0.0
        self.spawn()
        self.angle = random.choice([0, 90, 180, 270])
        self.speed = random.uniform(MINSPEED, MAXSPEED)
        self.state = "WALKING"
        self.timer = 0
        self.activity = random.choice(GTA_PHRASES)

    def spawn(self):
        for _ in range(1000):
            rx, ry = random.randint(10, MAP_AREA-10), random.randint(10, HEIGHT-10)
            if self.mh.mask.get_at((rx, ry)): self.x, self.y = float(rx), float(ry); return
        self.x, self.y = 100.0, 100.0

    def update(self, is_controlled, agents, pulses):
        old_x, old_y = self.x, self.y
        if is_controlled:
            keys = pygame.key.get_pressed()
            dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * self.speed
            dy = (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * self.speed
            self.x += dx; self.y += dy
        else:
            if self.state == "IDLE":
                self.timer -= 1
                if self.timer <= 0: 
                    self.state = "WALKING"; self.angle = random.choice([0, 90, 180, 270])
                    if self.hostility < 0.7: self.activity = random.choice(GTA_PHRASES)
            else:
                if random.random() < 0.005: 
                    self.state = "IDLE"; self.timer = 60
                rad = math.radians(self.angle)
                self.x += math.cos(rad) * self.speed; self.y += math.sin(rad) * self.speed

        if not (0 <= self.x < MAP_AREA and 0 <= self.y < HEIGHT) or not self.mh.mask.get_at((int(self.x), int(self.y))):
            self.x, self.y = old_x, old_y; self.angle = random.choice([0, 90, 180, 270])

        for other in agents:
            if other == self: continue
            dist = math.hypot(self.x - other.x, self.y - other.y)
            if dist < self.radius + other.radius:
                pulses.append(Pulse(self.x, self.y, (150, 150, 150), max_radius=20))
                overlap = (self.radius + other.radius) - dist
                ang = math.atan2(self.y - other.y, self.x - other.x)
                self.x += math.cos(ang) * overlap; self.y += math.sin(ang) * overlap
                return other
        return None

class Simulation:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.mh = MapHandler()
        self.cam = Camera()
        self.agents = [Agent(i, self.mh) for i in range(AGENT_COUNT)]
        self.pulses = []
        self.notifications = []
        self.selected = None
        self.logs = []
        self.clock = pygame.time.Clock()

        # Eye Graphic Setup
        self.eye_img = pygame.Surface((300, 300), pygame.SRCALPHA)
        pygame.draw.ellipse(self.eye_img, (255, 255, 255, 120), (20, 80, 260, 140))
        pygame.draw.circle(self.eye_img, (0, 255, 180, 180), (150, 150), 50)
        self.eye_timer = 0.0

    def add_log(self, msg, aid=-1):
        self.logs.append((msg, aid)); 
        if len(self.logs) > 15: self.logs.pop(0)

    def add_notification(self, text):
        self.notifications.append(Notification(text))

    def draw_world(self):
        world_surf = pygame.Surface((MAP_AREA, HEIGHT))
        world_surf.blit(self.mh.surface, (0, 0))
        
        heat_surf = pygame.Surface((MAP_AREA, HEIGHT), pygame.SRCALPHA)
        for a in self.agents:
            if a.hostility > 0.5:
                alpha = int(a.hostility * 80)
                pygame.draw.circle(heat_surf, (255, 0, 0, alpha), (int(a.x), int(a.y)), 45)
        world_surf.blit(heat_surf, (0, 0))

        for p in self.pulses[:]:
            if not p.update(): self.pulses.remove(p)
            else: p.draw(world_surf)

        for a in self.agents:
            r, g = clamp(255*a.hostility, 0, 255), clamp(255*(1-a.hostility), 0, 255)
            pygame.draw.circle(world_surf, (r, g, 50), (int(a.x), int(a.y)), a.radius)
            if a.has_app: pygame.draw.circle(world_surf, COLOR_WHITE, (int(a.x), int(a.y)), a.radius+2, 1)

        zoom = self.cam.zoom
        sub_rect = pygame.Rect(self.cam.x, self.cam.y, MAP_AREA/zoom, HEIGHT/zoom)
        scaled_view = pygame.transform.scale(world_surf.subsurface(sub_rect), (MAP_AREA, HEIGHT))
        self.screen.blit(scaled_view, (0, 0))

    def update_eye(self):
        if self.eye_timer > 0:
            self.eye_timer -= 1/FPS
            progress = self.eye_timer / EYE_FADE_TIME
            alpha = clamp(math.sin(progress * math.pi) * 200, 0, 255)
            
            temp_eye = self.eye_img.copy()
            temp_eye.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
            self.screen.blit(temp_eye, (MAP_AREA//2 - 150, HEIGHT//2 - 150))

    def render_notifications(self):
        f_notif = pygame.font.SysFont("Courier", 18, bold=True)
        for i, n in enumerate(self.notifications[:]):
            if not n.update():
                self.notifications.remove(n)
                continue
            text_surf = f_notif.render(f"!! {n.text} !!", True, COLOR_DANGER)
            text_surf.set_alpha(n.alpha)
            self.screen.blit(text_surf, (20, HEIGHT - 50 - (i * 30)))

    def run(self):
        while True:
            self.screen.fill(COLOR_BG)
            self.draw_world()
            
            # Sidebar UI
            pygame.draw.rect(self.screen, COLOR_UI_PANEL, (MAP_AREA, 0, UI_WIDTH, HEIGHT))
            f = pygame.font.SysFont("Courier", 14)
            self.screen.blit(f.render("[R] Induce Riot", True, COLOR_DANGER), (MAP_AREA+20, 20))
            self.screen.blit(f.render("[P] Digital Peace", True, COLOR_ACCENT), (MAP_AREA+20, 40))
            
            if self.selected:
                self.screen.blit(f.render(f"ENTITY: {self.selected.id:03}", True, COLOR_ACCENT), (MAP_AREA+20, 80))
                self.screen.blit(f.render(f"ACT: {self.selected.activity}", True, COLOR_WHITE), (MAP_AREA+20, 110))
            
            for i, (m, aid) in enumerate(reversed(self.logs)):
                self.screen.blit(f.render(f"> {m}", True, (120, 120, 130)), (MAP_AREA+20, HEIGHT - 30 - i*20))

            for event in pygame.event.get():
                if event.type == pygame.QUIT: return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    if mx < MAP_AREA:
                        w_mx = (mx / MAP_AREA) * (MAP_AREA / self.cam.zoom) + self.cam.x
                        w_my = (my / HEIGHT) * (HEIGHT / self.cam.zoom) + self.cam.y
                        
                        target = None
                        for a in self.agents:
                            if math.hypot(a.x-w_mx, a.y-w_my) < 15:
                                target = a
                                break
                        
                        if target:
                            if target.has_app:
                                if self.selected != target:
                                    self.selected = target
                                    self.eye_timer = EYE_FADE_TIME
                                    self.add_log(f"Linked: {target.id}", target.id)
                            else:
                                self.add_notification("ENCRYPTION ERROR: ACCESS DENIED")
                                self.add_log("Access Denied: Unencrypted Target")
                        else:
                            self.selected = None

                if event.type == pygame.KEYDOWN:
                    mx, my = pygame.mouse.get_pos()
                    w_mx = (mx / MAP_AREA) * (MAP_AREA / self.cam.zoom) + self.cam.x
                    w_my = (my / HEIGHT) * (HEIGHT / self.cam.zoom) + self.cam.y
                    
                    if event.key == pygame.K_r:
                        self.add_log("PROTOCOL: UNREST", -1)
                        self.pulses.append(Pulse(w_mx, w_my, COLOR_DANGER, max_radius=120))
                        for a in self.agents:
                            if math.hypot(a.x - w_mx, a.y - w_my) < 130:
                                a.hostility = 1.0
                                a.activity = random.choice(RIOT_PHRASES)
                                
                    if event.key == pygame.K_p:
                        self.add_log("PROTOCOL: HARMONY", -1)
                        self.pulses.append(Pulse(w_mx, w_my, COLOR_ACCENT, max_radius=120))
                        for a in self.agents:
                            if math.hypot(a.x - w_mx, a.y - w_my) < 130 and a.has_app:
                                a.hostility = 0.0
                                a.activity = "Feeling very compliant."

            self.cam.update(self.selected)
            for a in self.agents:
                hit = a.update(a == self.selected, self.agents, self.pulses)
                if hit and random.random() < 0.05: self.add_log(f"Contact: {a.id} vs {hit.id}", a.id)

            self.update_eye()
            self.render_notifications()
            pygame.display.flip(); self.clock.tick(FPS)

if __name__ == "__main__":
    Simulation().run()
