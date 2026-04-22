from config import *
import pygame

def create_fonts():
    return {
        'title': pygame.font.Font(None, FONT_SIZES['title']),
        'large': pygame.font.Font(None, FONT_SIZES['large']),
        'medium': pygame.font.Font(None, FONT_SIZES['medium']),
        'small': pygame.font.Font(None, FONT_SIZES['small']),
        'tiny': pygame.font.Font(None, FONT_SIZES['tiny'])
    }

def draw_controls(surface, fonts):
    controls = [
        "1-4: Toggle Sources  |  Q-W-E-R: Toggle Loads",
        "↑↓: Speed  |  SPACE: Pause"
    ]
    
    for i, text in enumerate(controls):
        control_text = fonts['small'].render(text, True, YELLOW)
        surface.blit(control_text, (WINDOW_WIDTH - 350, 30 + i*25))
