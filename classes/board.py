import pygame
from .piece import Piece

LIGHT_SQUARE = (238, 238, 210)
DARK_SQUARE = (118, 150, 86)

class Board:
    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.pieces = {}
        self.initialize_pieces()

    def initialize_pieces(self):
        self.pieces = {}
        current_color = 'white'
        p_y = 6
        y = 7
        for _ in range(2):
            pieces = [Piece(current_color, 'pawn', i, p_y) for i in range(8)]
            pieces.append(Piece(current_color, 'rook', 0, y))
            pieces.append(Piece(current_color, 'knight', 1, y))
            pieces.append(Piece(current_color, 'bishop', 2, y))
            pieces.append(Piece(current_color, 'queen', 3, y))
            pieces.append(Piece(current_color, 'king', 4, y))
            pieces.append(Piece(current_color, 'bishop', 5, y))
            pieces.append(Piece(current_color, 'knight', 6, y))
            pieces.append(Piece(current_color, 'rook', 7, y))

            self.pieces[current_color] = pieces

            current_color = 'black'
            y = 0
            p_y = 1

    def __draw_board(self, screen):
        for i in range(8):
            for j in range(8):
                if (i + j) % 2 == 0:
                    pygame.draw.rect(screen, LIGHT_SQUARE, (j * self.cell_size, i * self.cell_size, self.cell_size, self.cell_size))
                else:
                    pygame.draw.rect(screen, DARK_SQUARE, (j * self.cell_size, i * self.cell_size, self.cell_size, self.cell_size))

    def __draw_pieces(self, screen):
        for color in self.pieces.keys():
            for piece in self.pieces[color]:
                piece.draw(screen, self.cell_size)

    def draw(self, screen):
        self.__draw_board(screen)
        self.__draw_pieces(screen)