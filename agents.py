import pygame
import random
import math
from settings import Settings

class ActivityManager:
    GTA_STRINGS = [
        "Heading to Cluckin' Bell", "Ordering a Number 9 Large", 
        "Going bowling with Roman", "Eating a Big Number 5",
        "Ignoring a call from Roman", "Looking for a Sprunk machine",
        "Driving to the Pay 'n' Spray", "Heading to the Malibu Club",
        "Gone bowling with cousin", "Headed to the 'shoe'"
    ]

    @staticmethod
    def get_random_activity():
        return random.choice(ActivityManager.GTA_STRINGS)

class Agent:
    def __init__(self, x, y, has_app=False):
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * Settings.BASE_SPEED
        self.hostility = random.uniform(0, 1)  # 0.0 (Calm) to 1.0 (Violent)
        self.has_app = has_app
        self.activity = ActivityManager.get_random_activity()
        self.radius = Settings.AGENT_RADIUS
        self.is_pacified = False  # Used for "infectious calm" logic

    def update(self, map_nav):
        # Movement & Wall Bounce
        next_pos = self.pos + self.vel
        if not map_nav.is_walkable(next_pos.x, next_pos.y):
            # Simple reflection: reverse velocity on wall hit
            self.vel *= -1
        else:
            self.pos = next_pos

        # Update activity occasionally
        if random.random() < 0.001:
            self.activity = ActivityManager.get_random_activity()

    def get_color(self):
        # Gradient shift: Green (0,255,0) to Red (255,0,0)
        red = int(255 * self.hostility)
        green = int(255 * (1 - self.hostility))
        return (red, green, 0)

    def draw(self, screen, offset):
        draw_pos = self.pos + offset
        color = self.get_color()
        pygame.draw.circle(screen, color, (int(draw_pos.x), int(draw_pos.y)), self.radius)
        
        if self.has_app:
            # White ring for app-enabled users
            pygame.draw.circle(screen, (255, 255, 255), (int(draw_pos.x), int(draw_pos.y)), self.radius + 2, 1)

def resolve_collision(a1, a2):
    dist_vec = a1.pos - a2.pos
    distance = dist_vec.length()
    if distance < (a1.radius + a2.radius) and distance > 0:
        # Elastic collision velocity swap (simplified)
        a1.vel, a2.vel = a2.vel, a1.vel
        
        # Position correction to prevent sticking
        overlap = (a1.radius + a2.radius) - distance
        correction = dist_vec.normalize() * (overlap / 2)
        a1.pos += correction
        a2.pos -= correction

        # Digital Peacemaker "Infection" Logic
        if a1.is_pacified or a2.is_pacified:
            a1.hostility = max(0, a1.hostility - 0.2)
            a2.hostility = max(0, a2.hostility - 0.2)
            a1.is_pacified = a2.is_pacified = True