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
        self.valid_moves = {}
        self.board_flipped = False
        self.valid_moves_dirty = True
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
            self.__calculate_valid_moves()

            current_color = 'black'
            y = 0
            p_y = 1

    def __draw_board(self, screen, alpha_surface):
        for i in range(8):
            for j in range(8):
                cell_color = LIGHT_SQUARE if (i + j) % 2 == 0 else DARK_SQUARE
                if self.board_flipped:
                    i, j = 7 - i, 7 - j
                pygame.draw.rect(screen, cell_color, (j * self.cell_size,
                                                      i * self.cell_size, self.cell_size, self.cell_size))

        if self.selected_piece:
            x, y = self.selected_piece.x, self.selected_piece.y
            if self.board_flipped:
                x, y = 7 - x, 7 - y
            pygame.draw.rect(alpha_surface, SELECTED_COLOR, (x * self.cell_size,
                                                             y * self.cell_size, self.cell_size, self.cell_size))
            screen.blit(alpha_surface, (0, 0))

        if self.available_moves:
            for move in self.available_moves:
                x, y = move
                if self.board_flipped:
                    x, y = 7 - x, 7 - y
                cell_color = LIGHT_SQUARE if (x + y) % 2 == 0 else DARK_SQUARE
                draw_glow_square(screen, x * self.cell_size, y * self.cell_size,
                                 self.cell_size, cell_color, GLOWY_RED, 5)

    def __draw_pieces(self, screen):
        for color in self.pieces.keys():
            for piece in self.pieces[color]:
                piece.draw(screen, self.cell_size, self.board_flipped)

    def draw(self, screen, width, height):
        alpha_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.__draw_board(screen, alpha_surface)
        self.__draw_pieces(screen)

    def handle_click(self, mouse_x, mouse_y):
        cell_x = mouse_x // self.cell_size
        cell_y = mouse_y // self.cell_size

        if self.board_flipped:
            cell_x = 7 - cell_x
            cell_y = 7 - cell_y

        piece = self.piece_at(cell_x, cell_y)

        if self.selected_piece:
            # Check if player clicked on another piece of the same color
            if piece and piece.color == self.current_turn:
                self.selected_piece = piece
                self.available_moves = piece.get_valid_moves(self)
                return
            # If clicked on a valid move square, allow move
            elif (cell_x, cell_y) in self.available_moves:
                self.__move_piece(cell_x, cell_y)

                return
            else:
                # Clicked elsewhere: unselect
                self.selected_piece = None
                self.available_moves = []
        else:
            if piece and piece.color == self.current_turn:
                self.selected_piece = piece
                self.available_moves = piece.get_valid_moves(self)

    def __move_piece(self, x, y):
        # Move the king to castle
        if self.selected_piece.name == 'king' and abs(self.selected_piece.x - x) > 1:
            rook_x = 0 if x < self.selected_piece.x else 7
            rook_y = y
            rook = self.piece_at(rook_x, rook_y)
            if rook and rook.name == 'rook' and not rook.has_moved:
                # Move the rook to the correct position
                new_rook_x = x - 1 if x > self.selected_piece.x else x + 1
                rook.move_to(new_rook_x, y)
                rook.has_moved = True
        else:
            target_piece = self.piece_at(x, y)

            # Capture logic
            if target_piece:
                self.pieces[target_piece.color].remove(target_piece)
                self.captured_pieces[self.selected_piece.color].append(
                    target_piece)
                target_piece.move_to(-1000, -1000)  # Exile the poor thing

        # Move piece
        self.selected_piece.move_to(x, y)
        self.selected_piece.has_moved = True

        # Reset selections
        self.selected_piece = None
        self.available_moves = []

        # Update board state
        self.valid_moves_dirty = True
        self.board_flipped = not self.board_flipped
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'

    def piece_at(self, x, y):
        for clr in self.pieces.keys():
            for piece in self.pieces[clr]:
                if piece.x == x and piece.y == y:
                    return piece
        return None

    def __calculate_valid_moves(self):
        for color in self.pieces.keys():
            self.valid_moves[color] = []
            for piece in self.pieces[color]:
                self.valid_moves[color].extend(piece.get_valid_moves(self))

    def get_valid_moves(self, color):
        if self.valid_moves_dirty:
            self.valid_moves_dirty = False
            self.__calculate_valid_moves()
        return self.valid_moves.get(color, [])

    def get_attacked_squares(self, color):
        attacked = set()
        for piece in self.pieces.get(color, []):
            attacked.update(piece.get_attacked_squares(self))
        return attacked

    def is_king_in_check(self, color):
        enemy_color = 'black' if color == 'white' else 'white'
        enemy_attacks = self.get_attacked_squares(enemy_color)

        # Find the king
        for piece in self.pieces[color]:
            if piece.name == 'king':
                king_pos = (piece.x, piece.y)
                break
        else:
            # Uhh... the king is missing?! Do we call the FBI?
            return False

        return king_pos in enemy_attacks
    
    def is_checkmate(self):
        color = self.current_turn
        if not self.is_king_in_check(color):
            return False

        for piece in self.pieces[color]:
            for move in piece.get_valid_moves(self):
                # Temporarily move the piece
                original_pos = (piece.x, piece.y)
                piece.move_to(*move)

                # Check if the king is still in check
                if not self.is_king_in_check(color):
                    # Undo the move
                    piece.move_to(*original_pos)
                    return False

                # Undo the move
                piece.move_to(*original_pos)

        return True

    def reset(self):
        self.initialize_pieces()
        self.current_turn = 'white'
        self.selected_piece = None
        self.available_moves = []
        self.board_flipped = False
        self.valid_moves_dirty = True
        self.captured_pieces = {color: [] for color in self.pieces.keys()}
