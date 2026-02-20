import pygame
from settings import Settings

class InterventionSystem:
    @staticmethod
    def riot_inducer(agents, click_pos, radius=150):
        for agent in agents:
            if agent.pos.distance_to(click_pos) < radius:
                agent.hostility = min(1.0, agent.hostility + 0.5)
                agent.is_pacified = False

    @staticmethod
    def digital_peacemaker(agents, click_pos, radius=200):
        for agent in agents:
            if agent.has_app and agent.pos.distance_to(click_pos) < radius:
                agent.hostility = 0.0
                agent.is_pacified = True  # Starts the "infection"