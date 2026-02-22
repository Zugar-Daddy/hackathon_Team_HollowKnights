import pygame
import json
import os
import time

# --- CONFIGURATION ---
U_WIDTH, U_HEIGHT = 450, 800
COLOR_BG = (2, 4, 10)
COLOR_TEXT = (0, 255, 180)  # Aegis Cyan
COLOR_CRITICAL = (255, 50, 50)
COLOR_WHITE = (255, 255, 255) # ADDED THIS LINE TO FIX THE ERROR
COLOR_TERMINAL_BG = (5, 10, 15)
COLOR_INPUT_BG = (15, 25, 35)

class AegisUserApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((U_WIDTH, U_HEIGHT))
        pygame.display.set_caption("AEGIS - Field Terminal v1.2")
        self.font = pygame.font.SysFont("Courier", 14, bold=True)
        self.large_font = pygame.font.SysFont("Courier", 22, bold=True)
        
        # Auth State
        self.logged_in = False
        self.current_user = None
        self.active_field = "username" 
        self.u_text = ""
        self.p_text = ""
        self.error_msg = ""
        
        # Simulation Data
        self.state_data = {"recent_events": [], "heat_map": []}
        self.minimap_rect = pygame.Rect(20, 60, 410, 250)
        self.terminal_rect = pygame.Rect(20, 340, 410, 430)

    def check_credentials(self):
        if os.path.exists("users.json"):
            with open("users.json", "r") as f:
                db = json.load(f)
                for person in db["authorized_personnel"]:
                    if person["username"] == self.u_text and person["password"] == self.p_text:
                        self.current_user = person
                        return True
        return False

    def draw_login_ui(self):
        self.screen.fill(COLOR_BG)
        
        title = self.large_font.render("AEGIS SATELLITE LINK", True, COLOR_TEXT)
        self.screen.blit(title, (U_WIDTH//2 - 130, 150))

        # Username Field
        u_label = self.font.render("PERSONNEL ID:", True, COLOR_TEXT)
        self.screen.blit(u_label, (75, 250))
        u_box = pygame.Rect(75, 275, 300, 40)
        border_u = COLOR_TEXT if self.active_field == "username" else (50, 80, 70)
        pygame.draw.rect(self.screen, COLOR_INPUT_BG, u_box)
        pygame.draw.rect(self.screen, border_u, u_box, 1)
        self.screen.blit(self.font.render(self.u_text + ("_" if self.active_field == "username" else ""), True, COLOR_WHITE), (85, 287))

        # Password Field
        p_label = self.font.render("ACCESS KEY:", True, COLOR_TEXT)
        self.screen.blit(p_label, (75, 340))
        p_box = pygame.Rect(75, 365, 300, 40)
        border_p = COLOR_TEXT if self.active_field == "password" else (50, 80, 70)
        pygame.draw.rect(self.screen, COLOR_INPUT_BG, p_box)
        pygame.draw.rect(self.screen, border_p, p_box, 1)
        masked_pass = "*" * len(self.p_text)
        self.screen.blit(self.font.render(masked_pass + ("_" if self.active_field == "password" else ""), True, COLOR_WHITE), (85, 377))

        # Error Message
        if self.error_msg:
            err = self.font.render(self.error_msg, True, COLOR_CRITICAL)
            self.screen.blit(err, (U_WIDTH//2 - err.get_width()//2, 430))

    def draw_dashboard(self):
        if os.path.exists("aegis_state.json"):
            try:
                with open("aegis_state.json", "r") as f:
                    self.state_data = json.load(f)
            except: pass

        self.screen.fill(COLOR_BG)
        status = f"CONNECTED: {self.current_user['username']} ({self.current_user['role']})"
        self.screen.blit(self.font.render(status, True, COLOR_TEXT), (20, 25))
        
        # Mini-Map
        pygame.draw.rect(self.screen, (10, 20, 25), self.minimap_rect)
        pygame.draw.rect(self.screen, COLOR_TEXT, self.minimap_rect, 1)
        for h in self.state_data.get("heat_map", []):
            mx = self.minimap_rect.x + (h[0] / 1600) * self.minimap_rect.width
            my = self.minimap_rect.y + (h[1] / 1200) * self.minimap_rect.height
            color = COLOR_CRITICAL if h[2] > 0.6 else COLOR_TEXT
            pygame.draw.circle(self.screen, color, (int(mx), int(my)), 2)

        # Terminal
        pygame.draw.rect(self.screen, COLOR_TERMINAL_BG, self.terminal_rect)
        pygame.draw.rect(self.screen, (40, 40, 50), self.terminal_rect, 1)
        self.screen.blit(self.font.render("--- INTERVENTION_LOG.sh ---", True, (100, 100, 110)), (30, 350))
        events = self.state_data.get("recent_events", [])
        for i, ev in enumerate(reversed(events)):
            if i > 18: break
            color = COLOR_CRITICAL if ev["type"] == "MISINFO" else COLOR_TEXT
            msg = f"[{ev['timestamp']}] {ev['message']} @ {ev['pos']}"
            self.screen.blit(self.font.render(msg, True, color), (35, 380 + i * 22))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if not self.logged_in:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_TAB:
                            self.active_field = "password" if self.active_field == "username" else "username"
                        elif event.key == pygame.K_BACKSPACE:
                            if self.active_field == "username": self.u_text = self.u_text[:-1]
                            else: self.p_text = self.p_text[:-1]
                        elif event.key == pygame.K_RETURN:
                            if self.check_credentials():
                                self.logged_in = True
                            else:
                                self.error_msg = "AUTHENTICATION FAILURE: ACCESS DENIED"
                        else:
                            if self.active_field == "username": self.u_text += event.unicode
                            else: self.p_text += event.unicode

            if not self.logged_in:
                self.draw_login_ui()
            else:
                self.draw_dashboard()
            
            pygame.display.flip()
            pygame.time.Clock().tick(30)
        pygame.quit()

if __name__ == "__main__":
    AegisUserApp().run()
