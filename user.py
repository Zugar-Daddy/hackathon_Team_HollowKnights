import pygame
import json
import os
import time

# --- CONFIGURATION ---
U_WIDTH, U_HEIGHT = 450, 800
COLOR_BG = (2, 4, 10)
COLOR_TEXT = (0, 255, 180)  # Aegis Cyan
COLOR_CRITICAL = (255, 50, 50)
COLOR_TERMINAL_BG = (5, 10, 15)

class AegisUserApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((U_WIDTH, U_HEIGHT))
        pygame.display.set_caption("AEGIS - Field Terminal v1.1")
        self.font = pygame.font.SysFont("Courier", 14, bold=True)
        self.large_font = pygame.font.SysFont("Courier", 22, bold=True)
        
        self.logged_in = False
        self.current_user = None
        self.state_data = {"recent_events": [], "heat_map": []}
        
        self.minimap_rect = pygame.Rect(20, 60, 410, 250)
        self.terminal_rect = pygame.Rect(20, 340, 410, 430)

    def verify_login(self):
        """Standard JSON credential check via Console."""
        print("\n" + "="*35)
        print(" AEGIS SECURE GATEWAY - VERSION 1.1")
        print("="*35)
        u_input = input("USER AUTH ID: ")
        p_input = input("ACCESS KEY:   ")

        if os.path.exists("users.json"):
            with open("users.json", "r") as f:
                db = json.load(f)
                for person in db["authorized_personnel"]:
                    if person["username"] == u_input and person["password"] == p_input:
                        print(f"\n>> ACCESS GRANTED: Welcome, {person['role']}.")
                        self.current_user = person
                        return True
        print("\n>> ACCESS DENIED: INVALID CREDENTIALS.")
        return False

    def login_screen(self):
        """Displays the 'Locked' UI before authentication."""
        self.screen.fill(COLOR_BG)
        title = self.large_font.render("AEGIS SATELLITE LINK", True, COLOR_TEXT)
        self.screen.blit(title, (U_WIDTH//2 - 120, 250))
        
        btn_rect = pygame.Rect(100, 350, 250, 50)
        pygame.draw.rect(self.screen, COLOR_TEXT, btn_rect, 1)
        btn_txt = self.font.render("INITIALIZE AUTHENTICATION", True, COLOR_TEXT)
        self.screen.blit(btn_txt, (120, 368))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_rect.collidepoint(event.pos):
                    if self.verify_login():
                        self.logged_in = True
        return True

    def load_state(self):
        if os.path.exists("aegis_state.json"):
            try:
                with open("aegis_state.json", "r") as f:
                    self.state_data = json.load(f)
            except: pass

    def draw_dashboard(self):
        """The main surveillance interface."""
        self.load_state()
        self.screen.fill(COLOR_BG)
        
        # Header with Agent Info
        status = f"CONNECTED: {self.current_user['username']} ({self.current_user['role']})"
        self.screen.blit(self.font.render(status, True, COLOR_TEXT), (20, 25))
        
        # --- MINI-MAP ---
        pygame.draw.rect(self.screen, (10, 20, 25), self.minimap_rect)
        pygame.draw.rect(self.screen, COLOR_TEXT, self.minimap_rect, 1)
        
        heat_list = self.state_data.get("heat_map", [])
        for h in heat_list:
            mx = self.minimap_rect.x + (h[0] / 1150) * self.minimap_rect.width
            my = self.minimap_rect.y + (h[1] / 750) * self.minimap_rect.height
            color = COLOR_CRITICAL if h[2] > 0.6 else COLOR_TEXT
            pygame.draw.circle(self.screen, color, (int(mx), int(my)), 2)

        # --- TERMINAL ---
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
        while True:
            if not self.logged_in:
                if not self.login_screen(): break
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: return
                self.draw_dashboard()
            
            pygame.display.flip()
            pygame.time.Clock().tick(30)
        pygame.quit()

if __name__ == "__main__":
    AegisUserApp().run()
