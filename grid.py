from config import *
from components import PowerSource, IntelligentBattery, IntelligentLoad
import pygame
from datetime import datetime, timedelta


class MicrogridAI:
    def __init__(self):
        self.init_components()
        self.time_of_day = 14.0
        self.real_time = datetime.now()
        self.time_speed = TIME_SPEED_DEFAULT
        self.running = True
        self.weather = {"solar": 1.0, "wind": 0.8, "clear": True}
        self.ai_analysis = []
        self.source_contribution = {}
        self.last_action = ""
        self.msg_timer = 0.0

    # -----------------------------------------------------------
    # Initialization
    # -----------------------------------------------------------
    def init_components(self):
        self.sources = [
            PowerSource("Solar PV (50 kW)", 150, 140, 50, YELLOW, "solar", 3),
            PowerSource("Wind (35 kW)", 380, 140, 35, CYAN, "wind", 2),
            PowerSource("Grid (100 kW)", 650, 140, 100, BLUE, "grid", 1),
            PowerSource("Diesel (40 kW)", 950, 140, 40, ORANGE, "diesel", 0),
        ]
        self.battery = IntelligentBattery(550, 320, 120)
        self.loads = [
            IntelligentLoad("🏠 Home A", 150, 520, 12, PURPLE),
            IntelligentLoad("🏠 Home B", 320, 520, 10, PURPLE),
            IntelligentLoad("🏭 Industrial", 500, 520, 45, ORANGE, True),
            IntelligentLoad("🏢 Commercial", 750, 520, 25, BLUE),
        ]

    # -----------------------------------------------------------
    # Simulation Update loop
    # -----------------------------------------------------------
    def update(self, dt):
        if not self.running:
            return

        # time scaling now references config.TIME_SCALE
        self.time_of_day += self.time_speed * dt * TIME_SCALE
        self.real_time += timedelta(seconds=dt * self.time_speed * TIME_SCALE)
        if self.time_of_day >= 24:
            self.time_of_day -= 24

        for s in self.sources:
            s.update(self.time_of_day, self.weather)
        for l in self.loads:
            l.update(self.time_of_day)

        self.ai_dispatch()
        if self.msg_timer > 0:
            self.msg_timer -= dt

    # -----------------------------------------------------------
    # Dispatch logic
    # -----------------------------------------------------------
    def ai_dispatch(self):
        demand = sum(l.current_demand for l in self.loads if l.active)
        available = 0
        self.source_contribution = {}

        for src in sorted(self.sources, key=lambda s: -s.priority):
            if src.active:
                contrib = min(src.current_power, demand - available)
                self.source_contribution[src.name] = max(contrib, 0)
                available += contrib

        net = available - demand
        self.battery.ai_optimize(net)

        for load in self.loads:
            if load.current_demand > 0:
                best = max(self.source_contribution.items(),
                           key=lambda x: x[1],
                           default=("Battery", 0))
                load.power_source = best[0]
                load.satisfaction = min(100, (available / demand) * 100) if demand else 100
        self.generate_ai_insights(demand, available)

    # -----------------------------------------------------------
    # Friendly AI text
    # -----------------------------------------------------------
    def generate_ai_insights(self, demand, generation):
        ren = sum(v for k, v in self.source_contribution.items()
                  if "Solar" in k or "Wind" in k) / max(demand, 1)
        msgs = []
        if ren > 0.7:
            msgs.append("✅ Running mostly on renewables — efficient and green.")
        elif ren < 0.3:
            msgs.append("⚠️ Grid heavy — consider shifting to solar/wind.")
        soc = self.battery.charge / self.battery.capacity
        if soc < 0.2:
            msgs.append("🔋 Battery low — using backup sources.")
        elif soc > 0.9:
            msgs.append("🔋 Battery full — ready for evening peak.")
        if not msgs:
            msgs.append("💡 System stable — balanced operation.")
        self.ai_analysis = msgs[-3:]

    # -----------------------------------------------------------
    # Inputs + user feedback messages
    # -----------------------------------------------------------
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if "1" <= event.unicode <= "4":
                idx = int(event.unicode) - 1
                self.sources[idx].active = not self.sources[idx].active
                name = self.sources[idx].name.split()[0]
                self.last_action = f"{name} turned {'ON' if self.sources[idx].active else 'OFF'}"
                self.msg_timer = 1.5

            elif event.unicode.lower() in "qwer":
                idx = "qwer".index(event.unicode.lower())
                self.loads[idx].active = not self.loads[idx].active
                name = self.loads[idx].name
                self.last_action = f"{name} {'connected' if self.loads[idx].active else 'disconnected'}"
                self.msg_timer = 1.5

            elif event.key == pygame.K_SPACE:
                self.running = not self.running
                self.last_action = "⏸ Paused" if not self.running else "▶ Resumed"
                self.msg_timer = 1.5

            elif event.key == pygame.K_UP:
                self.time_speed = min(MAX_TIME_SPEED, self.time_speed + 0.1)
                self.last_action = f"Speed ×{self.time_speed:.1f}"
                self.msg_timer = 1.5

            elif event.key == pygame.K_DOWN:
                self.time_speed = max(0.05, self.time_speed - 0.1)
                self.last_action = f"Speed ×{self.time_speed:.1f}"
                self.msg_timer = 1.5

    # -----------------------------------------------------------
    # Drawing sequence
    # -----------------------------------------------------------
    def draw(self, surface):
        from ui import create_fonts
        f = create_fonts()
        surface.fill((10, 10, 20))
        self.draw_background(surface)
        self.draw_grid(surface, f)
        self.draw_dashboard(surface, f)
        self.draw_panels(surface, f)
        self.draw_status(surface, f)
        self.draw_user_message(surface, f)

    def draw_background(self, surface):
        pygame.draw.line(surface, LIME, (120, 240), (1050, 240), 6)
        pygame.draw.line(surface, GREEN, (120, 240), (1050, 240), 3)

    def draw_grid(self, surface, f):
        for i, s in enumerate(self.sources):
            s.draw(surface, f["medium"], f["small"], i)
        self.battery.draw(surface, f["small"], f["medium"])
        for i, l in enumerate(self.loads):
            l.draw(surface, f["small"], f["medium"], f["tiny"], i)

    # -----------------------------------------------------------
    # Side dashboard (user‑friendly summary)
    # -----------------------------------------------------------
    def draw_dashboard(self, surface, f):
        px, py, pw, ph = WINDOW_WIDTH - 330, 80, 300, 500
        pygame.draw.rect(surface, (25, 25, 30), (px, py, pw, ph), border_radius=10)
        pygame.draw.rect(surface, LIME, (px, py, pw, ph), 2, border_radius=10)

        title = f["large"].render("SYSTEM OVERVIEW", True, LIME)
        surface.blit(title, (px + 30, py + 10))

        y = py + 60
        surface.blit(f["medium"].render("Power Generation", True, YELLOW), (px + 20, y))
        y += 28
        total = max(sum(self.source_contribution.values()), 0.001)
        for name, val in self.source_contribution.items():
            pct = val / total * 100
            line = f["small"].render(f"• {name[:14]:14} {val:6.1f} kW ({pct:3.0f}%)", True, WHITE)
            surface.blit(line, (px + 25, y))
            y += 22

        soc = self.battery.charge / self.battery.capacity * 100
        col = GREEN if soc > 60 else YELLOW if soc > 25 else RED
        y += 12
        surface.blit(f["medium"].render("Battery Status", True, ORANGE), (px + 20, y))
        y += 28
        bar = pygame.Rect(px + 25, y, 240, 18)
        pygame.draw.rect(surface, GRAY, bar)
        pygame.draw.rect(surface, col, (bar.x, bar.y, 240 * soc / 100, 18))
        valstr = f["small"].render(f"{soc:4.0f}% ({self.battery.ai_recommendation})", True, WHITE)
        surface.blit(valstr, (px + 30, y + 24))

        y += 65
        surface.blit(f["medium"].render("Active Loads", True, CYAN), (px + 20, y))
        y += 28
        for l in self.loads:
            if l.active:
                color = GREEN if l.satisfaction > 90 else YELLOW if l.satisfaction > 60 else RED
                txt = f["small"].render(
                    f"{'✓' if l.active else '✗'} {l.name[:10]:10} {l.current_demand:5.1f} kW",
                    True, color)
                surface.blit(txt, (px + 25, y))
                y += 22

    # -----------------------------------------------------------
    # AI insight panel
    # -----------------------------------------------------------
    def draw_panels(self, surface, f):
        ai_x, ai_y = 30, 450
        pygame.draw.rect(surface, (30, 30, 40), (ai_x, ai_y, 420, 120), border_radius=12)
        pygame.draw.rect(surface, LIME, (ai_x, ai_y, 420, 120), 2, border_radius=12)
        head = f["large"].render("🤖 AI INSIGHTS", True, LIME)
        surface.blit(head, (ai_x + 20, ai_y + 10))
        for i, msg in enumerate(self.ai_analysis):
            txt = f["medium"].render(msg, True, WHITE)
            surface.blit(txt, (ai_x + 25, ai_y + 45 + i * 28))

    # -----------------------------------------------------------
    # Bottom status bar
    # -----------------------------------------------------------
    def draw_status(self, surface, f):
        bar = pygame.Rect(0, WINDOW_HEIGHT - 60, WINDOW_WIDTH, 60)
        pygame.draw.rect(surface, (25, 25, 35), bar)
        h = int(self.time_of_day)
        m = int((self.time_of_day % 1) * 60)
        gen = sum(self.source_contribution.values())
        dem = sum(l.current_demand for l in self.loads)
        soc = self.battery.charge / self.battery.capacity * 100
        bal = gen - dem
        txt = f["large"].render(
            f"🕐 {h:02d}:{m:02d}  ⚡ Gen {gen:5.1f} kW  🏠 Demand {dem:5.1f} kW  📊 Bal {bal:+5.1f} kW  🔋 {soc:3.0f}%",
            True,
            LIME if bal >= 0 else YELLOW,
        )
        surface.blit(txt, (25, WINDOW_HEIGHT - 48))

    # -----------------------------------------------------------
    # Temporary floating messages
    # -----------------------------------------------------------
    def draw_user_message(self, surface, f):
        if self.msg_timer > 0 and self.last_action:
            alpha = min(255, int(255 * (self.msg_timer / 1.5)))
            surf = f["large"].render(self.last_action, True, (255, 255, 200))
            surf.set_alpha(alpha)
            surface.blit(surf,
                         (WINDOW_WIDTH // 2 - surf.get_width() // 2, 40))
