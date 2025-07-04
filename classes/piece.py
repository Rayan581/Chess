import pygame
import os

class Piece:
    def __init__(self, color, name, x, y):
        self.color = color
        self.name = name
        self.x = x
        self.y = y
        self.texture = self.load_texture()

    def load_texture(self):
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        piece_name = self.color + '-' + self.name
        texture_path = os.path.join(BASE_DIR, "pieces", self.color, f"{piece_name}.png")
        return pygame.image.load(texture_path).convert_alpha()
    
    def draw(self, screen, cell_size):
        x = self.x * cell_size
        y = self.y * cell_size

        scaled_texture = pygame.transform.scale(self.texture, (cell_size, cell_size))
        screen.blit(scaled_texture, (x, y))