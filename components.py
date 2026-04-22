from config import *
import pygame
import math
import random
from datetime import datetime, timedelta

class PowerSource:
    def __init__(self, name, x, y, max_power, color, source_type, priority=0):
        self.name = name
        self.x, self.y = x, y
        self.max_power = max_power
        self.current_power = 0
        self.color = color
        self.source_type = source_type
        self.priority = priority
        self.active = True
        self.cost_per_kwh = {"solar": 0.04, "wind": 0.05, "grid": 0.12, "diesel": 0.15}[source_type]
        
    def update(self, time_of_day, weather):
        if not self.active:
            self.current_power = 0
            return
            
        if self.source_type == "solar":
            solar_factor = max(0, math.sin((time_of_day % 24) * math.pi / 12))
            weather_factor = weather["solar"] * (1.0 if weather["clear"] else 0.3)
            self.current_power = self.max_power * solar_factor * weather_factor
            
        elif self.source_type == "wind":
            self.current_power = self.max_power * weather["wind"] * random.uniform(0.4, 1.2)
            
        elif self.source_type == "diesel":
            self.current_power = self.max_power * 0.9  # High reliability
            
        else:  # grid
            self.current_power = self.max_power
            
    def draw(self, surface, font_medium, font_small, index):
        x_offset = index * 200 + 150
        rect = pygame.Rect(x_offset-70, self.y-50, 140, 100)
        pygame.draw.rect(surface, DARK_GRAY, rect, border_radius=12)
        
        status_color = GREEN if self.active and self.current_power > 0 else RED
        pygame.draw.rect(surface, status_color, rect, 4, border_radius=12)
        
        # Icons
        icons = {"solar": "☀️", "wind": "💨", "grid": "🔌", "diesel": "🔋"}
        icon = icons.get(self.source_type, "⚡")
        
        name_text = font_small.render(f"{icon} {self.name}", True, WHITE)
        surface.blit(name_text, (x_offset - name_text.get_width()//2, self.y+10))
        
        power_text = font_medium.render(f"{self.current_power:.1f}kW", True, status_color)
        surface.blit(power_text, (x_offset - power_text.get_width()//2, self.y+45))

class IntelligentBattery:
    def __init__(self, x, y, capacity):
        self.x, self.y = x, y
        self.capacity = capacity
        self.charge = capacity * 0.6
        self.max_charge = 25
        self.max_discharge = 30
        self.current_flow = 0
        self.ai_recommendation = "HOLD"
        self.forecast_demand = 0
        
    def ai_optimize(self, net_power):
        if net_power > 5:
            self.ai_recommendation = "CHARGE"
            return min(net_power * 0.8, self.max_charge)
        elif net_power < -10 and self.charge / self.capacity > 0.2:
            self.ai_recommendation = "DISCHARGE"
            return min(abs(net_power), self.max_discharge)
        self.ai_recommendation = "HOLD"
        return 0
        
    def draw(self, surface, font_small, font_medium):
        rect = pygame.Rect(self.x-60, self.y-45, 120, 90)
        pygame.draw.rect(surface, DARK_GRAY, rect, border_radius=12)
        pygame.draw.rect(surface, ORANGE, rect, 4, border_radius=12)
        
        soc = self.charge / self.capacity
        bar_w = int(100 * soc)
        bar_color = GREEN if soc > 0.5 else YELLOW if soc > 0.2 else RED
        pygame.draw.rect(surface, bar_color, (self.x-45, self.y-25, bar_w, 20))
        
        soc_text = font_medium.render(f"{soc*100:.0f}%", True, WHITE)
        surface.blit(soc_text, (self.x - soc_text.get_width()//2, self.y-28))
        
        ai_text = font_small.render(f"🤖 {self.ai_recommendation}", True, LIME)
        surface.blit(ai_text, (self.x - ai_text.get_width()//2, self.y+35))

class IntelligentLoad:
    def __init__(self, name, x, y, base_demand, color, critical=False):
        self.name = name
        self.x, self.y = x, y
        self.base_demand = base_demand
        self.current_demand = base_demand
        self.color = color
        self.critical = critical
        self.power_source = "Unknown"
        self.satisfaction = 100
        self.priority = 10 if critical else 5
        self.active = True
        
    def update(self, time_of_day):
        if not self.active:
            self.current_demand = 0
            return
            
        factor = 1.0
        if "Home" in self.name:
            if 17 <= time_of_day <= 22: factor = 1.6
            elif 0 <= time_of_day <= 6: factor = 0.4
        elif "Industrial" in self.name:
            if 8 <= time_of_day <= 18: factor = 1.4
            else: factor = 0.3
            
        self.current_demand = self.base_demand * factor * random.uniform(0.9, 1.1)
        
    def draw(self, surface, font_small, font_medium, font_tiny, index):
        x_offset = 150 + index * 170
        rect = pygame.Rect(x_offset-65, self.y-45, 130, 90)
        pygame.draw.rect(surface, DARK_GRAY, rect, border_radius=12)
        
        sat_color = GREEN if self.satisfaction > 95 else YELLOW if self.satisfaction > 80 else RED
        pygame.draw.rect(surface, sat_color, rect, 4, border_radius=12)
        
        # Source badge
        source_icon = "🔌" if "Grid" in self.power_source else "☀️" if "Solar" in self.power_source else "💨"
        source_text = font_tiny.render(f"{source_icon} {self.power_source[:12]}...", True, CYAN)
        surface.blit(source_text, (x_offset - source_text.get_width()//2, self.y+25))
        
        name_text = font_small.render(self.name, True, WHITE)
        surface.blit(name_text, (x_offset - name_text.get_width()//2, self.y))
        
        demand_text = font_medium.render(f"{self.current_demand:.1f}kW", True, sat_color)
        surface.blit(demand_text, (x_offset - demand_text.get_width()//2, self.y+50))
