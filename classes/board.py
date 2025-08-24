import pygame
from .piece import Piece
from .sound_manager import SoundManager

LIGHT_SQUARE = (238, 238, 210)
DARK_SQUARE = (118, 150, 86)
SELECTED_COLOR = (255, 255, 102, 150)
TRANSPARENT_BLACK = (0, 0, 0, 70)

sounds = SoundManager()
sound_to_play = ''


class Board:
    def __init__(self, cell_size, offset_h, fen=None):
        self.cell_size = cell_size
        self.pieces = {}
        self.captured_pieces = {}
        self.valid_moves = {}
        self.board_flipped = False
        self.move_made = False
        self.valid_moves_dirty = True
        self.current_turn = 'white'
        self.selected_piece = None
        self.available_moves = []
        self.pawn_promotion = False
        self.en_passant_target = None
        self.move_history = []
        self.last_captured = None
        self.moved_piece_prev_coord = None
        if not fen:
            self.initialize_pieces()
        else:
            self.setup_from_fen(fen)

        self.piece_points = {
            'pawn': 1,
            'knight': 3,
            'bishop': 3,
            'rook': 5,
            'queen': 9
        }

        self.promotion_menu_buttons = {
            'queen': pygame.Rect(0, 0, cell_size, cell_size),
            'rook': pygame.Rect(0, 0, cell_size, cell_size),
            'bishop': pygame.Rect(0, 0, cell_size, cell_size),
            'knight': pygame.Rect(0, 0, cell_size, cell_size)
        }

        menu_left_offset_h = (offset_h - (cell_size * 4)) // 2
        self.promotion_menu_buttons['queen'].topleft = (
            menu_left_offset_h, cell_size * 3 + cell_size // 2)
        self.promotion_menu_buttons['rook'].topleft = (
            menu_left_offset_h + cell_size, cell_size * 3 + cell_size // 2)
        self.promotion_menu_buttons['bishop'].topleft = (
            menu_left_offset_h + cell_size * 2, cell_size * 3 + cell_size // 2)
        self.promotion_menu_buttons['knight'].topleft = (
            menu_left_offset_h + cell_size * 3, cell_size * 3 + cell_size // 2)

        sounds.play_sound('opening')

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

    def setup_from_fen(self, fen):
        """
        Setup board pieces based on the given FEN string.
        """
        self.pieces = {
            'white': [],
            'black': []
        }
        self.captured_pieces = {
            'white': [],
            'black': []
        }

        piece_map = {
            'p': 'pawn',
            'n': 'knight',
            'b': 'bishop',
            'r': 'rook',
            'q': 'queen',
            'k': 'king'
        }

        rows = fen.split()[0].split("/")  # only piece placement part
        for y, row in enumerate(rows):
            x = 0
            for char in row:
                if char.isdigit():
                    x += int(char)  # empty squares
                else:
                    color = "white" if char.isupper() else "black"
                    name = piece_map[char.lower()]
                    # create piece at (x, y)
                    new_piece = Piece(color, name, x, y)

                    self.pieces[color].append(new_piece)

                    x += 1
        self.__calculate_valid_moves()

    def _draw_font(self, screen, text, x, y, size, _font, color):
        font = pygame.font.Font(_font, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        screen.blit(text_surface, text_rect)

    def __draw_promotion_menu(self, screen):
        queen_texture = pygame.image.load(
            f'assets/pieces/{self.current_turn}/{self.current_turn}-queen.png')
        rook_texture = pygame.image.load(
            f'assets/pieces/{self.current_turn}/{self.current_turn}-rook.png')
        bishop_texture = pygame.image.load(
            f'assets/pieces/{self.current_turn}/{self.current_turn}-bishop.png')
        knight_texture = pygame.image.load(
            f'assets/pieces/{self.current_turn}/{self.current_turn}-knight.png')

        queen_texture = pygame.transform.scale(
            queen_texture, (self.cell_size, self.cell_size))
        rook_texture = pygame.transform.scale(
            rook_texture, (self.cell_size, self.cell_size))
        bishop_texture = pygame.transform.scale(
            bishop_texture, (self.cell_size, self.cell_size))
        knight_texture = pygame.transform.scale(
            knight_texture, (self.cell_size, self.cell_size))

        screen.blit(queen_texture,
                    self.promotion_menu_buttons['queen'].topleft)
        screen.blit(rook_texture, self.promotion_menu_buttons['rook'].topleft)
        screen.blit(bishop_texture,
                    self.promotion_menu_buttons['bishop'].topleft)
        screen.blit(knight_texture,
                    self.promotion_menu_buttons['knight'].topleft)
        for button in self.promotion_menu_buttons.values():
            pygame.draw.rect(screen, (0, 0, 0), button, 2)

    def __draw_board(self, screen, alpha_surface, width, height, offset_h, offset_v):
        for i in range(8):
            for j in range(8):
                cell_color = LIGHT_SQUARE if (i + j) % 2 == 0 else DARK_SQUARE
                if self.board_flipped:
                    i, j = 7 - i, 7 - j
                pygame.draw.rect(screen, cell_color, (j * self.cell_size + offset_h,
                                                      i * self.cell_size + offset_v, self.cell_size, self.cell_size))

        if self.selected_piece:
            x, y = self.selected_piece.x, self.selected_piece.y
            if self.board_flipped:
                x, y = 7 - x, 7 - y
            pygame.draw.rect(alpha_surface, SELECTED_COLOR, (x * self.cell_size,
                                                             y * self.cell_size, self.cell_size, self.cell_size))
            screen.blit(alpha_surface, (offset_h, offset_v))

        if self.available_moves:
            for move in self.available_moves:
                x, y = move
                if self.board_flipped:
                    x, y = 7 - x, 7 - y

                center_x = x * self.cell_size + self.cell_size // 2
                center_y = y * self.cell_size + self.cell_size // 2

                target = self.piece_at(*move)

                alpha_surface.fill((0, 0, 0, 0))  # Clear the alpha surface

                if target or (move == self.en_passant_target and self.selected_piece.name == 'pawn'):
                    circle_radius = int(self.cell_size * 0.5)
                    circle_thickness = 7
                    pygame.draw.circle(
                        alpha_surface, TRANSPARENT_BLACK, (center_x, center_y), circle_radius, width=circle_thickness)
                else:
                    circle_radius = int(self.cell_size * 0.17)
                    pygame.draw.circle(alpha_surface, TRANSPARENT_BLACK,
                                       (center_x, center_y), circle_radius)
                screen.blit(alpha_surface, (offset_h, offset_v))

        # Draw the a, b, c or 1, 2, 3 labels
        for i in range(8):
            label = chr(97 + i) if not self.board_flipped else chr(104 - i)
            self._draw_font(screen, label, self.cell_size * (i + 1) - 10 + offset_h, height - 10 + offset_v,
                            15, 'freesansbold.ttf', (0, 0, 0))

            label = str(i + 1) if self.board_flipped else str(8 - i)
            self._draw_font(screen, label, 10 + offset_h, self.cell_size * i + 10 + offset_v,
                            15, 'freesansbold.ttf', (0, 0, 0))

        if self.pawn_promotion:
            self.__draw_promotion_menu(screen)

    def __draw_pieces(self, screen, offset_h, offset_v):
        for color in self.pieces.keys():
            for piece in self.pieces[color]:
                piece.draw(screen, self.cell_size, offset_h,
                           offset_v, self.board_flipped)

    def __get_sorted_captured_pieces(self, color):
        return sorted(
            self.captured_pieces[color],
            key=lambda p: self.piece_points.get(p.name, 0),
            reverse=False
        )

    def __draw_captured_pieces(self, screen, width, height, offset_h, offset_v):
        from collections import defaultdict

        cell = self.cell_size
        piece_size = int(cell * 0.4)
        horizontal_stack_offset_h = 8  # space between pieces in same group

        def draw_stacked_groups(pieces, x_start, y_start):
            grouped = defaultdict(list)
            for piece in pieces:
                grouped[piece.name].append(piece)

            # Sort piece types by value
            sorted_groups = sorted(
                grouped.items(),
                key=lambda item: self.piece_points.get(item[0], 0),
                reverse=False
            )

            current_x = x_start
            for name, group in sorted_groups:
                for i, piece in enumerate(group):
                    icon = pygame.transform.scale(
                        piece.texture, (piece_size, piece_size))
                    screen.blit(
                        icon, (current_x + i * horizontal_stack_offset_h, y_start))

                # Move current_x forward based on how wide this group was
                group_width = len(group) * \
                    horizontal_stack_offset_h + piece_size
                group_spacing = -10
                current_x += group_width + group_spacing  # extra spacing between groups

        # Top row: black pieces captured by white
        captured_black = self.captured_pieces['white']
        draw_stacked_groups(captured_black, x_start=10,
                            y_start=offset_v + height // 2 - piece_size - 5)

        # Bottom row: white pieces captured by black
        captured_white = self.captured_pieces['black']
        y_start_bottom = 8 * cell - piece_size - 5
        draw_stacked_groups(captured_white, x_start=10,
                            y_start=offset_v + height // 2 + piece_size)

        pygame.draw.line(screen, (255, 255, 255), (10, offset_v +
                                                   height // 2 + 10), (offset_h - 10, offset_v + height // 2 + 10), 3)
        pygame.draw.line(screen, (0, 0, 0), (10, offset_v +
                                             height // 2 + 13), (offset_h - 10, offset_v + height // 2 + 13), 3)

    def draw(self, screen, width, height, offset_h, offset_v):
        alpha_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.__draw_board(screen, alpha_surface, width,
                          height, offset_h, offset_v)
        self.__draw_pieces(screen, offset_h, offset_v)
        self.__draw_captured_pieces(screen, width, height, offset_h, offset_v)

    def __promote(self, mouse_x, mouse_y):
        global sound_to_play

        for piece_name, button in self.promotion_menu_buttons.items():
            if button.collidepoint(mouse_x, mouse_y):
                # Replace the pawn with the selected piece
                new_piece = Piece(self.current_turn, piece_name,
                                  self.selected_piece.x, self.selected_piece.y)

                from_pos = (
                    self.moved_piece_prev_coord[0], self.moved_piece_prev_coord[1])
                to_pos = (new_piece.x, new_piece.y)
                promotion_letter = piece_name[0].upper()
                promotion_letter = 'N' if promotion_letter == 'K' else promotion_letter

                # Log promotion move in notation
                notation = self._get_notation(
                    self.selected_piece, from_pos, to_pos, promotion=promotion_letter)
                self.last_captured = None

                self.pieces[self.current_turn].remove(self.selected_piece)
                self.pieces[self.current_turn].append(new_piece)

                self.selected_piece = None
                self.current_turn = 'black' if self.current_turn == 'white' else 'white'
                self.pawn_promotion = False
                self.valid_moves_dirty = True
                self.move_made = True

                if self.is_king_in_check(self.current_turn):
                    notation += '+'
                    sound_to_play = 'capture'
                if self.is_checkmate():
                    notation = notation[:-1] + '#'
                    sound_to_play = 'checkmate'
                elif self.is_stalemate():
                    sound_to_play = 'stalemate'
                sounds.play_sound(sound_to_play)

                self.move_history.append(notation)
                print("Move:", notation)

    def handle_click(self, mouse_x, mouse_y, offset_h, offset_v):
        global sound_to_play
        sound_to_play = ''

        mouse_x -= offset_h
        mouse_y -= offset_v

        if self.pawn_promotion:
            self.__promote(mouse_x + offset_h, mouse_y + offset_v)
            return

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

            # If clicked on a valid move square, allow move
            elif (cell_x, cell_y) in self.available_moves:
                self._move_piece(cell_x, cell_y)
            else:
                # Clicked elsewhere: unselect
                self.selected_piece = None
                self.available_moves = []
        else:
            if piece and piece.color == self.current_turn:
                self.selected_piece = piece
                self.available_moves = piece.get_valid_moves(self)

        sounds.play_sound(sound_to_play)

    def _move_piece(self, x, y):
        global sound_to_play

        from_x, from_y = self.selected_piece.x, self.selected_piece.y
        to_x, to_y = x, y
        promotion = None

        self.last_captured = [False, self.piece_at(to_x, to_y) or (
            self.selected_piece.name == 'pawn' and (to_x, to_y) == self.en_passant_target)]
        self.moved_piece_prev_coord = (
            self.selected_piece.x, self.selected_piece.y)

        notation = self._get_notation(
            self.selected_piece, (from_x, from_y), (to_x, to_y), promotion)

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

                sound_to_play = 'castle'
        else:
            target_piece = self.piece_at(x, y)

            # En passant capture logic
            if self.selected_piece.name == 'pawn' and (x, y) == self.en_passant_target:
                direction = 1 if self.selected_piece.color == 'black' else -1
                target_piece = self.piece_at(x, y - direction)

            # Capture logic
            if target_piece:
                self.pieces[target_piece.color].remove(target_piece)
                self.captured_pieces[self.selected_piece.color].append(
                    target_piece)
                sound_to_play = 'capture'
            else:
                sound_to_play = 'move'

        # Check if en passant is available
        if self.selected_piece.name == 'pawn' and abs(self.selected_piece.y - y) == 2:
            self.en_passant_target = (x, (self.selected_piece.y + y) // 2)
        else:
            self.en_passant_target = None

        # Move piece
        self.selected_piece.move_to(x, y)

        self.selected_piece.has_moved = True

        # If the piece is a pawn and reaches the opposite end, promote it
        if self.selected_piece.name == 'pawn':
            if (self.selected_piece.color == 'white' and y == 0) or \
               (self.selected_piece.color == 'black' and y == 7):
                self.pawn_promotion = True
                self.available_moves = []
                self.last_captured[0] = True
                return

        self.last_captured = None if not self.last_captured[0] else self.last_captured

        # Reset selections
        self.selected_piece = None
        self.available_moves = []

        # Update board state
        self.valid_moves_dirty = True
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'
        self.move_made = True

        if self.is_king_in_check(self.current_turn):
            sound_to_play = 'check'
            notation += '+'
        if self.is_checkmate():
            sound_to_play = 'checkmate'
            notation = notation[:-1] + '#'
        elif self.is_stalemate():
            sound_to_play = 'stalemate'

        self.move_history.append(notation)
        print("Move: ", notation)

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
            valid_moves = piece.get_valid_moves(self)
            for move in valid_moves:
                original_pos = (piece.x, piece.y)
                captured = self.piece_at(*move)

                # Move piece
                piece.move_to(*move)
                if captured:
                    self.pieces[captured.color].remove(captured)

                # Check for check
                if not self.is_king_in_check(color):
                    # Undo the move
                    piece.move_to(*original_pos)
                    if captured:
                        self.pieces[captured.color].append(captured)

                    return False

                # Undo the move
                piece.move_to(*original_pos)
                if captured:
                    self.pieces[captured.color].append(captured)

        return True

    def is_stalemate(self):
        color = self.current_turn

        # If the king is in check, it's not a stalemate.
        if self.is_king_in_check(color):
            return False

        # Check if any piece of the current color has valid legal moves
        for piece in self.pieces[color]:
            for move in piece.get_valid_moves(self):
                # Temporarily make the move
                original_pos = (piece.x, piece.y)
                captured = self.piece_at(*move)

                piece.move_to(*move)
                if captured:
                    self.pieces[captured.color].remove(captured)

                # If the king is not in check after the move
                if not self.is_king_in_check(color):
                    # Undo the move and return False (not stalemate)
                    piece.move_to(*original_pos)
                    if captured:
                        self.pieces[captured.color].append(captured)
                    return False

                # Undo the move
                piece.move_to(*original_pos)
                if captured:
                    self.pieces[captured.color].append(captured)

        # No legal moves found and not in check → stalemate
        return True

    def _draw_end_message(self, screen, message, alpha):
        width, height = screen.get_size()

        # 1. Draw transparent black overlay
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))  # Black with 180 alpha
        screen.blit(overlay, (0, 0))

        # 2. Draw the message in center
        self._draw_font(screen, message, width // 2,
                        height // 2, 64, None, (255, 255, 255))
        self._draw_font(screen, 'Press R to Restart', width // 2,
                        height // 2 + 30, 44, None, (255, 255, 255))

    def _get_notation(self, piece, from_pos, to_pos, promotion=None):
        col_map = 'abcdefgh'
        from_x, from_y = from_pos
        to_x, to_y = to_pos

        # Handle castling
        if piece.name == 'king' and abs(from_x - to_x) == 2:
            return "O-O" if to_x > from_x else "O-O-O"

        # Piece letter
        piece_letter = {
            'pawn': '',
            'knight': 'N',
            'bishop': 'B',
            'rook': 'R',
            'queen': 'Q',
            'king': 'K'
        }.get(piece.name, '')

        # Detect if it's a capture
        is_capture = self.last_captured[1]

        # Disambiguation (only if needed)
        similar_pieces = [
            p for p in self.pieces[piece.color]
            if p.name == piece.name and p != piece and (to_x, to_y) in p.get_valid_moves(self)
        ]

        disambiguate = ""
        if similar_pieces:
            same_file = any(p.x == from_x for p in similar_pieces)
            same_rank = any(p.y == from_y for p in similar_pieces)
            if not same_file:
                disambiguate = col_map[from_x]
            elif not same_rank:
                disambiguate = str(8 - from_y)
            else:
                disambiguate = f"{col_map[from_x]}{8 - from_y}"

        # Compose notation
        notation = piece_letter + disambiguate
        if is_capture:
            if piece.name == 'pawn' and not disambiguate:
                notation += col_map[from_x]
            notation += "x"
        notation += f"{col_map[to_x]}{8 - to_y}"

        # Promotion
        if promotion:
            notation += f"={promotion.upper()}"

        return notation
