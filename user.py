import pygame
import json
import os
import time

# --- CONFIGURATION ---
U_WIDTH, U_HEIGHT = 400, 750
COLOR_BG = (2, 4, 8)
COLOR_ACCENT = (0, 255, 180)  # Aegis Green
COLOR_CRITICAL = (255, 45, 45) # Riot Red
COLOR_COP = (0, 120, 255)      # Police Blue
COLOR_CIV = (200, 200, 200)    # Civilian Grey

class AegisUserApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((U_WIDTH, U_HEIGHT))
        pygame.display.set_caption("AEGIS - Field Terminal")
        self.font = pygame.font.SysFont("Courier", 14, bold=True)
        self.large_font = pygame.font.SysFont("Courier", 22, bold=True)
        
        self.logged_in = False
        self.current_user = None
        self.state_data = {"recent_events": [], "heat_map": []}
        self.radar_rect = pygame.Rect(20, 100, 360, 250)

    def verify_credentials(self, username, password):
        """Checks the users.json file for a match."""
        if not os.path.exists("users.json"):
            print("ERROR: users.json not found!")
            return False

        with open("users.json", "r") as f:
            data = json.load(f)
            for person in data["authorized_personnel"]:
                if person["username"] == username and person["password"] == password:
                    self.current_user = person
                    return True
        return False

    def login_screen(self):
        self.screen.fill(COLOR_BG)
        
        # Aegis Branding
        title = self.large_font.render("AEGIS LOGIN", True, COLOR_ACCENT)
        self.screen.blit(title, (U_WIDTH//2 - 70, 150))
        
        prompt = self.font.render("SYSTEM STATUS: ENCRYPTED", True, (100, 100, 100))
        self.screen.blit(prompt, (U_WIDTH//2 - 95, 190))

        # Login Button UI
        btn_rect = pygame.Rect(100, 300, 200, 50)
        pygame.draw.rect(self.screen, COLOR_ACCENT, btn_rect, 2)
        btn_txt = self.font.render("INITIATE SYNC", True, COLOR_ACCENT)
        self.screen.blit(btn_txt, (135, 318))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_rect.collidepoint(event.pos):
                    # Input via Console for presentation ease
                    print("\n" + "="*30)
                    print(" AEGIS SECURE GATEWAY")
                    print("="*30)
                    u = input("Username: ")
                    p = input("Password: ")
                    
                    if self.verify_credentials(u, p):
                        print(f"ACCESS GRANTED: Welcome {self.current_user['role']} {u}")
                        self.logged_in = True
                    else:
                        print("ACCESS DENIED: Unauthorized Credentials.")
        return True

    def draw_dashboard(self):
        self.screen.fill(COLOR_BG)
        
        # Load the latest simulation state
        if os.path.exists("aegis_state.json"):
            try:
                with open("aegis_state.json", "r") as f:
                    self.state_data = json.load(f)
            except: pass

        # Header with User Info
        role_color = COLOR_COP if self.current_user['role'] == "Cop" else COLOR_ACCENT
        header_txt = self.font.render(f"USER: {self.current_user['username']} | ROLE: {self.current_user['role']}", True, role_color)
        self.screen.blit(header_txt, (20, 20))
        
        # Radar Background
        pygame.draw.rect(self.screen, (5, 12, 15), self.radar_rect)
        pygame.draw.rect(self.screen, (30, 60, 50), self.radar_rect, 1)

        # Draw Heatmap (Hostility)
        for h in self.state_data.get("heat_map", []):
            hx = self.radar_rect.x + (h[0] / 1150) * self.radar_rect.width
            hy = self.radar_rect.y + (h[1] / 750) * self.radar_rect.height
            if h[2] > 0.4: # Hostility threshold
                alpha = int(h[2] * 150)
                s = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.circle(s, (255, 0, 0, alpha), (10, 10), 10)
                self.screen.blit(s, (hx-10, hy-10))

        # Draw Intervention Events
        for ev in self.state_data.get("recent_events", []):
            ex = self.radar_rect.x + (ev["pos"][0] / 1150) * self.radar_rect.width
            ey = self.radar_rect.y + (ev["pos"][1] / 750) * self.radar_rect.height
            ev_color = COLOR_CRITICAL if ev["type"] == "MISINFO" else COLOR_ACCENT
            pygame.draw.circle(self.screen, ev_color, (int(ex), int(ey)), 4)

        # Intervention Log
        log_y = 380
        self.screen.blit(self.font.render("INTERVENTION FEED:", True, (150, 150, 150)), (20, log_y))
        for i, ev in enumerate(reversed(self.state_data.get("recent_events", []))):
            if i > 12: break
            color = COLOR_CRITICAL if ev["type"] == "MISINFO" else COLOR_ACCENT
            msg = f"[{ev['timestamp']}] {ev['message']}"
            self.screen.blit(self.font.render(msg, True, color), (20, log_y + 30 + i*20))

    def run(self):
        running = True
        while running:
            if not self.logged_in:
                running = self.login_screen()
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: running = False
                self.draw_dashboard()
            
            pygame.display.flip()
            pygame.time.Clock().tick(30)
        pygame.quit()

if __name__ == "__main__":
    AegisUserApp().run()