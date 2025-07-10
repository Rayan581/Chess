import pygame
import os


class Piece:
    def __init__(self, color, name, x, y):
        self.color = color
        self.name = name
        self.x = x
        self.y = y
        self.texture = self.__load_texture()
        self.has_moved = False
        self.valid_moves = []

    def __load_texture(self):
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        piece_name = self.color + '-' + self.name
        texture_path = os.path.join(
            BASE_DIR, "pieces", self.color, f"{piece_name}.png")
        return pygame.image.load(texture_path).convert_alpha()

    def draw(self, screen, cell_size, board_flipped=False):
        x = self.x * cell_size
        y = self.y * cell_size
        # If the board is flipped, adjust the coordinates
        if board_flipped:
            x = (7 - self.x) * cell_size
            y = (7 - self.y) * cell_size

        scaled_texture = pygame.transform.scale(
            self.texture, (cell_size, cell_size))
        screen.blit(scaled_texture, (x, y))

    def move_to(self, x, y):
        self.x = x
        self.y = y

    def __rook_moves(self, board):
        self.valid_moves = []
        # Right, Left, Up, Down
        directions = [(1, 0), (-1, 0), (0, -1), (0, 1)]

        for dx, dy in directions:
            x, y = self.x + dx, self.y + dy
            while 0 <= x < 8 and 0 <= y < 8:
                piece = board.piece_at(x, y)
                if piece:
                    if piece.color != self.color:
                        self.valid_moves.append((x, y))  # capture enemy
                    break  # can't go further
                self.valid_moves.append((x, y))
                x += dx
                y += dy

    def __bishop_moves(self, board):
        self.valid_moves = []
        # Right-Up, Left-Up, Right-Down, Left-Down
        directions = [(1, -1), (-1, -1), (1, 1), (-1, 1)]

        for dx, dy in directions:
            x, y = self.x + dx, self.y + dy
            while 0 <= x < 8 and 0 <= y < 8:
                piece = board.piece_at(x, y)
                if piece:
                    if piece.color != self.color:
                        self.valid_moves.append((x, y))  # capture enemy
                    break  # can't go further
                self.valid_moves.append((x, y))
                x += dx
                y += dy

    def __queen_moves(self, board):
        self.valid_moves = []
        # Right, Left, Up, Down
        directions = [(1, 0), (-1, 0), (0, -1), (0, 1)]

        for dx, dy in directions:
            x, y = self.x + dx, self.y + dy
            while 0 <= x < 8 and 0 <= y < 8:
                piece = board.piece_at(x, y)
                if piece:
                    if piece.color != self.color:
                        self.valid_moves.append((x, y))  # capture enemy
                    break  # can't go further
                self.valid_moves.append((x, y))
                x += dx
                y += dy

        # Right-Up, Left-Up, Right-Down, Left-Down
        directions = [(1, -1), (-1, -1), (1, 1), (-1, 1)]

        for dx, dy in directions:
            x, y = self.x + dx, self.y + dy
            while 0 <= x < 8 and 0 <= y < 8:
                piece = board.piece_at(x, y)
                if piece:
                    if piece.color != self.color:
                        self.valid_moves.append((x, y))  # capture enemy
                    break  # can't go further
                self.valid_moves.append((x, y))
                x += dx
                y += dy

    def __knight_moves(self, board):
        self.valid_moves = []
        directions = [(2, -1), (2, 1), (-2, -1), (-2,  1),
                      (-1, -2), (1, -2), (-1, 2), (1, 2)]

        for dx, dy in directions:
            x, y = self.x + dx, self.y + dy
            if 0 <= x < 8 and 0 <= y < 8:
                piece = board.piece_at(x, y)
                if piece:
                    if piece.color != self.color:
                        self.valid_moves.append((x, y))  # capture enemy
                    continue
                self.valid_moves.append((x, y))

    def __pawn_moves(self, board):
        self.valid_moves = []
        direction = 1 if self.color == 'black' else -1

        one_move = (self.x, self.y + direction)
        two_move = (self.x, self.y + direction * 2)

        if not (0 <= one_move[1] < 8):
            return

        # Move forward one sqaure if empty
        if board.piece_at(*one_move) is None:
            self.valid_moves.append(one_move)

            # Move two square from starting row
            if not self.has_moved and board.piece_at(*two_move) is None:
                self.valid_moves.append(two_move)

        # Capture diagonally
        for dx in [-1, 1]:
            target_x = self.x + dx
            target_y = self.y + direction

            if 0 <= target_x < 8 and 0 <= target_y < 8:
                target_piece = board.piece_at(target_x, target_y)
                if target_piece and target_piece.color != self.color:
                    self.valid_moves.append((target_x, target_y))

    def __king_moves(self, board):
        self.valid_moves = []

        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue

                target_x = self.x + dx
                target_y = self.y + dy

                if 0 <= target_x < 8 and 0 <= target_y < 8:
                    target_piece = board.piece_at(target_x, target_y)
                    if target_piece is None or target_piece.color != self.color:
                        self.valid_moves.append((target_x, target_y))

        # Get moves of other player and remove the dangerous cells
        other_color = 'black' if self.color == 'white' else 'white'
        attacked_squares = board.get_attacked_squares(other_color)
        self.valid_moves = [
            move for move in self.valid_moves if move not in attacked_squares]
        
        # Add castling moves if applicable
        self.castle(board)

    def get_attacked_squares(self, board):
        attacked = []

        if self.name == 'pawn':
            direction = 1 if self.color == 'black' else -1
            for dx in [-1, 1]:
                target_x = self.x + dx
                target_y = self.y + direction
                if 0 <= target_x < 8 and 0 <= target_y < 8:
                    attacked.append((target_x, target_y))

        elif self.name == 'knight':
            directions = [(2, -1), (2, 1), (-2, -1), (-2, 1),
                          (-1, -2), (1, -2), (-1, 2), (1, 2)]
            for dx, dy in directions:
                x, y = self.x + dx, self.y + dy
                if 0 <= x < 8 and 0 <= y < 8:
                    attacked.append((x, y))

        elif self.name == 'bishop':
            attacked += self.__raycast_attacks(board,
                                               [(1, -1), (-1, -1), (1, 1), (-1, 1)])

        elif self.name == 'rook':
            attacked += self.__raycast_attacks(board,
                                               [(1, 0), (-1, 0), (0, 1), (0, -1)])

        elif self.name == 'queen':
            attacked += self.__raycast_attacks(board, [(1, 0), (-1, 0), (0, 1), (0, -1),
                                                       (1, -1), (-1, -1), (1, 1), (-1, 1)])

        elif self.name == 'king':
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if dx != 0 or dy != 0:
                        x, y = self.x + dx, self.y + dy
                        if 0 <= x < 8 and 0 <= y < 8:
                            attacked.append((x, y))

        return attacked

    def __raycast_attacks(self, board, directions):
        attacked = []
        for dx, dy in directions:
            x, y = self.x + dx, self.y + dy
            while 0 <= x < 8 and 0 <= y < 8:
                attacked.append((x, y))
                if board.piece_at(x, y):  # stop at first piece hit
                    break
                x += dx
                y += dy
        return attacked

    def __remove_invalid_moves(self, board):
        original_x, original_y = self.x, self.y

        for x, y in self.valid_moves[:]:
            # Temporarily remove any piece at the destination (simulate capture)
            captured_piece = board.piece_at(x, y)
            if captured_piece:
                board.pieces[captured_piece.color].remove(captured_piece)

            # Move this piece to new position
            self.x, self.y = x, y

            # Check if our king is now in check
            in_check = board.is_king_in_check(self.color)

            # Undo move
            self.x, self.y = original_x, original_y
            if captured_piece:
                board.pieces[captured_piece.color].append(captured_piece)
                captured_piece.x, captured_piece.y = x, y  # restore captured piece's position

            # Remove move if it puts the king in check
            if in_check:
                self.valid_moves.remove((x, y))

    def castle(self, board):
        if self.has_moved:
            return

        # Check for left rook
        left_rook = board.piece_at(0, self.y)
        if left_rook and left_rook.name == 'rook' and not left_rook.has_moved:
            if all(board.piece_at(x, self.y) is None for x in range(1, 4)) and \
               not board.is_king_in_check(self.color):
                original_x, original_y = self.x, self.y
                for x in [self.x - 1, self.x - 2]:
                    self.move_to(self.x + x, self.y)
                    if board.is_king_in_check(self.color):
                        self.move_to(original_x, original_y)
                        return
                    self.move_to(original_x, original_y)
                
                # If we reach here, castling is possible
                # Append the castling move
                self.valid_moves.append((self.x - 2, self.y))

        # Check for right rook
        right_rook = board.piece_at(7, self.y)
        if right_rook and right_rook.name == 'rook' and not right_rook.has_moved:
            if all(board.piece_at(x, self.y) is None for x in range(5, 7)) and \
               not board.is_king_in_check(self.color):
                original_x, original_y = self.x, self.y
                for x in [self.x + 1, self.x + 2]:
                    self.move_to(self.x + x, self.y)
                    if board.is_king_in_check(self.color):
                        self.move_to(original_x, original_y)
                        return
                    self.move_to(original_x, original_y)

                # If we reach here, castling is possible
                # Append the castling move
                self.valid_moves.append((self.x + 2, self.y))

        return

    def get_valid_moves(self, board):
        if self.name == 'rook':
            self.__rook_moves(board)
        elif self.name == 'bishop':
            self.__bishop_moves(board)
        elif self.name == 'queen':
            self.__queen_moves(board)
        elif self.name == 'knight':
            self.__knight_moves(board)
        elif self.name == 'pawn':
            self.__pawn_moves(board)
        elif self.name == 'king':
            self.__king_moves(board)

        self.__remove_invalid_moves(board)

        return self.valid_moves
