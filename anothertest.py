import pygame
import random
import math

# --- Configuration ---
WIDTH, HEIGHT = 1000, 700
MAP_COLOR = (30, 30, 30)  # Dark gray/black
UI_WIDTH = 300
FPS = 60

# Agent Types
NPC = "NPC"
COP = "COP"
FELON = "FELON"

class Agent:
    def __init__(self, id):
        self.id = id
        self.type = random.choice([NPC, COP, FELON])
        self.has_app = random.random() > 0.4  # 60% have the app installed
        
        # Stats
        self.hostility = random.uniform(0, 1)
        self.ideology = random.uniform(-1, 1) # -1 to 1 scale
        
        # Physics
        self.radius = 8
        self.x = random.randint(50, WIDTH - UI_WIDTH - 50)
        self.y = random.randint(50, HEIGHT - 50)
        self.speed = random.uniform(1, 3)
        self.angle = random.uniform(0, math.pi * 2)

    def move(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

        # Bounce off walls
        if self.x < 0 or self.x > WIDTH - UI_WIDTH: self.angle = math.pi - self.angle
        if self.y < 0 or self.y > HEIGHT: self.angle = -self.angle

    def draw(self, screen, selected):
        # Color based on type
        color = (0, 255, 0) if self.type == NPC else (0, 100, 255) if self.type == COP else (255, 50, 50)
        
        # Highlight if app is installed
        if self.has_app:
            pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.radius + 2, 1)
        
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)
        
        if selected == self:
            pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), self.radius + 5, 2)

# --- Initialization ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 16)

agents = [Agent(i) for i in range(20)]
selected_agent = None

running = True
while running:
    screen.fill(MAP_COLOR)
    
    # 1. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            for a in agents:
                dist = math.hypot(a.x - mx, a.y - my)
                if dist < 15:
                    if a.has_app:
                        selected_agent = a
                    else:
                        print("Access Denied: App not installed on target.")

    # 2. Update Agents
    for a in agents:
        a.move()

    # 3. Drawing
    # Draw "White Spaces" (Paths/City Blocks) - Optional background logic
    pygame.draw.rect(screen, (50, 50, 50), (0, 0, WIDTH - UI_WIDTH, HEIGHT))

    for a in agents:
        a.draw(screen, selected_agent)

    # 4. Surveillance UI (Right Side)
    pygame.draw.rect(screen, (20, 20, 25), (WIDTH - UI_WIDTH, 0, UI_WIDTH, HEIGHT))
    pygame.draw.line(screen, (100, 100, 100), (WIDTH - UI_WIDTH, 0), (WIDTH - UI_WIDTH, HEIGHT), 2)
    
    if selected_agent:
        # Display Agent "App" Data
        header = font.render(f"MONITORING: {selected_agent.id}", True, (255, 255, 0))
        type_txt = font.render(f"CLASS: {selected_agent.type}", True, (200, 200, 200))
        host_txt = font.render(f"HOSTILITY: {selected_agent.hostility:.2f}", True, (200, 200, 200))
        ideo_txt = font.render(f"IDEOLOGY: {selected_agent.ideology:.2f}", True, (200, 200, 200))
        
        screen.blit(header, (WIDTH - UI_WIDTH + 20, 30))
        screen.blit(type_txt, (WIDTH - UI_WIDTH + 20, 70))
        screen.blit(host_txt, (WIDTH - UI_WIDTH + 20, 100))
        screen.blit(ideo_txt, (WIDTH - UI_WIDTH + 20, 130))
        
        # Mock Manipulation Buttons
        pygame.draw.rect(screen, (100, 0, 0), (WIDTH - UI_WIDTH + 20, 200, 200, 30))
        btn_txt = font.render("PUSH PROPAGANDA", True, (255, 255, 255))
        screen.blit(btn_txt, (WIDTH - UI_WIDTH + 40, 205))
    else:
        instr = font.render("Select target with [App Installed]", True, (100, 100, 100))
        screen.blit(instr, (WIDTH - UI_WIDTH + 20, HEIGHT // 2))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()