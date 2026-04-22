import pygame
import sys, os
sys.path.append(os.path.dirname(__file__))
from grid import MicrogridAI
from ui import draw_controls

pygame.init()
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🧠 Intelligent Microgrid Control System")
clock = pygame.time.Clock()

def main():
    grid = MicrogridAI()
    
    while True:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            grid.handle_input(event)
            
        if grid.running:
            grid.update(dt)
            
        grid.draw(screen)
        pygame.display.flip()

if __name__ == "__main__":
    main()
