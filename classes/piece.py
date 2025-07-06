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

    def draw(self, screen, cell_size):
        x = self.x * cell_size
        y = self.y * cell_size

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

    def get_available_moves(self):
        return self.valid_moves

    def calculate_valid_moves(self, board):
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
            pass

        return self.valid_moves
