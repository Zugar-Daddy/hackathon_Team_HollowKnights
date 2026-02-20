import pygame

class Settings:
    # Screen Dimensions
    WIDTH = 1280
    HEIGHT = 720
    SIDEBAR_WIDTH = 300
    
    # Map & Simulation
    MAP_FILE = "map.png"  # Ensure this is a white-path/black-wall image
    FPS = 60
    
    # NPC Parameters
    AGENT_RADIUS = 6
    APP_PENETRATION_RATE = 0.35  # 35% of NPCs have the app
    BASE_SPEED = 2.0
    
    # System Colors
    COLOR_WHITE = (255, 255, 255)
    COLOR_BLACK = (0, 0, 0)
    COLOR_BG = (20, 20, 25)
    COLOR_UI_TEXT = (0, 255, 65)  # "Hacker" Green