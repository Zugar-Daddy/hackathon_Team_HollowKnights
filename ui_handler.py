import pygame
from settings import Settings

class Dashboard:
    def __init__(self):
        self.font = pygame.font.SysFont("Courier New", 16)
        self.rect = pygame.Rect(Settings.WIDTH - Settings.SIDEBAR_WIDTH, 0, Settings.SIDEBAR_WIDTH, Settings.HEIGHT)

    def draw(self, screen, selected_agent):
        # Draw background panel
        pygame.draw.rect(screen, (10, 10, 15), self.rect)
        pygame.draw.line(screen, Settings.COLOR_UI_TEXT, (self.rect.left, 0), (self.rect.left, Settings.HEIGHT), 2)
        
        header = self.font.render("AEGIS SURVEILLANCE v1.0", True, Settings.COLOR_UI_TEXT)
        screen.blit(header, (self.rect.left + 10, 20))

        if selected_agent:
            if selected_agent.has_app:
                stats = [
                    f"STATUS: ENROLLED",
                    f"HOSTILITY: {int(selected_agent.hostility * 100)}%",
                    f"ACTIVITY: {selected_agent.activity}",
                    f"COORDS: {int(selected_agent.pos.x)}, {int(selected_agent.pos.y)}"
                ]
            else:
                stats = ["ERROR: ENCRYPTED", "TARGET NOT ENROLLED"]
            
            for i, text in enumerate(stats):
                line = self.font.render(text, True, Settings.COLOR_UI_TEXT)
                screen.blit(line, (self.rect.left + 10, 100 + (i * 30)))
        else:
            prompt = self.font.render("SELECT TARGET...", True, (100, 100, 100))
            screen.blit(prompt, (self.rect.left + 10, 100))