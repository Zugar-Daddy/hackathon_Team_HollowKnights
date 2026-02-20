import pygame
import random
from settings import Settings
from map_handler import MapNavigator
from agents import Agent, resolve_collision
from systems import InterventionSystem
from ui_handler import Dashboard

class AegisEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((Settings.WIDTH, Settings.HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.map_nav = MapNavigator(Settings.MAP_FILE)
        self.dashboard = Dashboard()
        self.agents = self.spawn_agents(50)
        
        self.selected_agent = None
        self.camera_offset = pygame.math.Vector2(0, 0)

    def spawn_agents(self, count):
        agents = []
        while len(agents) < count:
            rx, ry = random.randint(0, self.map_nav.width), random.randint(0, self.map_nav.height)
            if self.map_nav.is_walkable(rx, ry):
                has_app = random.random() < Settings.APP_PENETRATION_RATE
                agents.append(Agent(rx, ry, has_app))
        return agents

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(Settings.FPS)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                # Adjust mouse click for camera offset
                world_click = pygame.math.Vector2(mx, my) - self.camera_offset
                
                if event.button == 1: # Left Click: Select
                    self.selected_agent = None
                    for a in self.agents:
                        if a.pos.distance_to(world_click) < a.radius + 5:
                            self.selected_agent = a
                            break
                elif event.button == 3: # Right Click: Intervention
                    InterventionSystem.digital_peacemaker(self.agents, world_click)

    def update(self):
        for i, a1 in enumerate(self.agents):
            a1.update(self.map_nav)
            for a2 in self.agents[i+1:]:
                resolve_collision(a1, a2)
        
        # Camera Logic
        if self.selected_agent:
            # Center selected agent on screen (minus sidebar)
            target_x = (Settings.WIDTH - Settings.SIDEBAR_WIDTH) / 2 - self.selected_agent.pos.x
            target_y = Settings.HEIGHT / 2 - self.selected_agent.pos.y
            self.camera_offset = pygame.math.Vector2(target_x, target_y)
        else:
            self.camera_offset = pygame.math.Vector2(0, 0)

    def draw(self):
        self.screen.fill(Settings.COLOR_BG)
        self.map_nav.draw(self.screen, self.camera_offset)
        for a in self.agents:
            a.draw(self.screen, self.camera_offset)
        self.dashboard.draw(self.screen, self.selected_agent)
        pygame.display.flip()