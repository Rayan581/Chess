import pygame
from .piece import Piece

LIGHT_SQUARE = (238, 238, 210)
DARK_SQUARE = (118, 150, 86)
SELECTED_COLOR = (255, 255, 102, 150)
GLOWY_RED = (255, 70, 70)


def draw_glow_square(screen, x, y, size, fill_color, glow_color, glow_thickness):
    # Draw the filled center square
    pygame.draw.rect(screen, fill_color, (x, y, size, size))

    # Draw the glow as fading rectangles
    for i in range(1, glow_thickness + 1):
        alpha = 255 * (1 - i / (glow_thickness + 1))
        glow_surf = pygame.Surface(
            (size + i * 2, size + i * 2), pygame.SRCALPHA)
        faded_color = (*glow_color, int(alpha))
        pygame.draw.rect(glow_surf, faded_color,
                         (0, 0, size + i * 2, size + i * 2), width=1)
        screen.blit(glow_surf, (x - i, y - i))


class Board:
    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.pieces = {}
        self.captured_pieces = {}
        self.initialize_pieces()
        self.current_turn = 'white'
        self.selected_piece = None
        self.available_moves = []

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
            self.captured_pieces[current_color] = []

            current_color = 'black'
            y = 0
            p_y = 1

    def __draw_board(self, screen, alpha_surface):
        for i in range(8):
            for j in range(8):
                cell_color = LIGHT_SQUARE if (i + j) % 2 == 0 else DARK_SQUARE
                pygame.draw.rect(screen, cell_color, (j * self.cell_size,
                                                      i * self.cell_size, self.cell_size, self.cell_size))

        if self.selected_piece:
            x, y = self.selected_piece.x, self.selected_piece.y
            pygame.draw.rect(alpha_surface, SELECTED_COLOR, (x * self.cell_size,
                                                             y * self.cell_size, self.cell_size, self.cell_size))
            screen.blit(alpha_surface, (0, 0))

        if self.available_moves:
            for move in self.available_moves:
                x, y = move
                cell_color = LIGHT_SQUARE if (x + y) % 2 == 0 else DARK_SQUARE
                draw_glow_square(screen, x * self.cell_size, y * self.cell_size,
                                 self.cell_size, cell_color, GLOWY_RED, 5)

    def __draw_pieces(self, screen):
        for color in self.pieces.keys():
            for piece in self.pieces[color]:
                piece.draw(screen, self.cell_size)

    def draw(self, screen, width, height):
        alpha_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.__draw_board(screen, alpha_surface)
        self.__draw_pieces(screen)

    def handle_click(self, mouse_x, mouse_y):
        cell_x = mouse_x // self.cell_size
        cell_y = mouse_y // self.cell_size

        piece = self.piece_at(cell_x, cell_y)

        if self.selected_piece:
            # Check if player clicked on another piece of the same color
            if piece and piece.color == self.current_turn:
                self.selected_piece = piece
                self.available_moves = piece.calculate_valid_moves(self)
                return
            # If clicked on a valid move square, allow move
            elif (cell_x, cell_y) in self.available_moves:
                self.__move_piece(cell_x, cell_y)
                self.current_turn = 'black' if self.current_turn == 'white' else 'white'
                return
            else:
                # Clicked elsewhere: unselect
                self.selected_piece = None
                self.available_moves = []
        else:
            if piece and piece.color == self.current_turn:
                self.selected_piece = piece
                self.available_moves = piece.calculate_valid_moves(self)

    def __move_piece(self, x, y):
        piece = self.piece_at(x, y)
        self.selected_piece.move_to(x, y)
        if piece:
            self.captured_pieces[self.selected_piece.color].append(piece)
            piece.move_to(-1000, -1000)

        self.selected_piece.has_moved = True
        self.selected_piece = None
        self.available_moves = []

    def piece_at(self, x, y):
        for clr in self.pieces.keys():
            for piece in self.pieces[clr]:
                if piece.x == x and piece.y == y:
                    return piece
        return None
