from datetime import datetime
import re
import pygame
import os
from classes import Board

WIDTH, HEIGHT = 640, 640
OFFSET_H = 350
OFFSET_V = 50
ROWS, COLS = 8, 8
CELL_SIZE = WIDTH // COLS

GRAY = (50, 50, 50)
TOTAL_TIME = 600  # Time in seconds
FLIP_DELAY_MS = 600  # Delay in milliseconds


def parse_move(board, notation):
    current_color = board.current_turn

    piece_map = {
        'K': 'king',
        'Q': 'queen',
        'R': 'rook',
        'B': 'bishop',
        'N': 'knight'
    }

    # Regex pattern to match standard notation
    pattern = r'^(?P<piece>[KQRBN])?'         # Optional piece letter
    pattern += r'(?P<origin_file>[a-h])?'      # Optional disambiguation file
    pattern += r'(?P<origin_rank>[1-8])?'      # Optional disambiguation rank
    pattern += r'(x)?'                         # Optional capture indicator
    pattern += r'(?P<dest_file>[a-h])'         # Destination file
    pattern += r'(?P<dest_rank>[1-8])'         # Destination rank
    pattern += r'(=?(?P<promotion>[QRBN]))?'   # Optional promotion
    pattern += r'(?P<check>[+#])?$'            # Optional check/checkmate

    match = re.match(pattern, notation)
    if not match:
        raise ValueError(f"Invalid move notation: {notation}")

    piece_letter = match.group('piece')
    origin_file = match.group('origin_file')
    origin_rank = match.group('origin_rank')
    dest_file = match.group('dest_file')
    dest_rank = match.group('dest_rank')
    promotion = match.group('promotion')

    piece_name = piece_map.get(piece_letter, 'pawn')
    dest_x = ord(dest_file) - ord('a')
    dest_y = 8 - int(dest_rank)

    candidates = []

    for piece in board.pieces[current_color]:
        if piece.name != piece_name:
            continue

        # Disambiguation filter
        if origin_file and piece.x != ord(origin_file) - ord('a'):
            continue
        if origin_rank and piece.y != 8 - int(origin_rank):
            continue

        valid_moves = piece.get_valid_moves(board)
        if (dest_x, dest_y) in valid_moves:
            candidates.append(piece)

    if len(candidates) == 1:
        return [(candidates[0].x, candidates[0].y), (dest_x, dest_y), promotion]
    elif len(candidates) > 1:
        raise Exception(
            f"Ambiguous move: {notation}, multiple pieces can go there.")
    else:
        raise Exception(f"No valid piece found for: {notation}")


def make_moves(moves_list, board):
    for move in moves_list:
        current_coords, next_coords, _ = parse_move(board, move)
        board.selected_piece = board.piece_at(*current_coords)
        board.available_moves = board.selected_piece.get_valid_moves(board)
        x, y = next_coords
        board._move_piece(x, y)


def format_time(seconds):
    minutes = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{minutes:02}:{secs:02}"


def generate_pgn(move_list, white_name="White", black_name="Black", result="*", termination="", time_control="0"):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")

    headers = [
        f'[Event "Vs. Player"]',
        f'[Site "Pygame Chess"]',
        f'[Date "{date_str}"]',
        f'[White "{white_name}"]',
        f'[Black "{black_name}"]',
        f'[Result "{result}"]',
        f'[WhiteElo "10"]',
        f'[BlackElo "10"]',
        f'[TimeControl "{time_control}"]',
        f'[Termination "{termination}"]'
    ]

    # Format moves into numbered PGN
    pgn_moves = []
    for i in range(0, len(move_list), 2):
        turn_num = i // 2 + 1
        white_move = move_list[i]
        black_move = move_list[i + 1] if i + 1 < len(move_list) else ""
        pgn_moves.append(f"{turn_num}. {white_move} {black_move}".strip())

    pgn_body = " ".join(pgn_moves)
    return "\n".join(headers) + "\n" + pgn_body + (f" {result}" if not pgn_body.endswith(result) else "")


def draw_time(white_time, black_time, screen):
    font = pygame.font.Font('assets/fonts/DANKMONO-REGULAR.OTF', 84)

    white_time_text = font.render(
        f"{format_time(white_time)}", True, (255, 255, 255))
    black_time_text = font.render(
        f"{format_time(black_time)}", True, (0, 0, 0))

    screen.blit(white_time_text, (OFFSET_H + WIDTH +
                                  (OFFSET_H // 2 - font.size(format_time(white_time))[0] // 2), OFFSET_V + HEIGHT // 2 - 90))
    screen.blit(black_time_text, (OFFSET_H + WIDTH +
                                  (OFFSET_H // 2 - font.size(format_time(black_time))[0] // 2), OFFSET_V + HEIGHT // 2 + 50))

    pygame.draw.line(screen, (255, 255, 255), (OFFSET_H + WIDTH + 10, OFFSET_V +
                     HEIGHT // 2 + 10), (OFFSET_H * 2 + WIDTH - 10, OFFSET_V + HEIGHT // 2 + 10), 3)
    pygame.draw.line(screen, (0, 0, 0), (OFFSET_H + WIDTH + 10, OFFSET_V +
                     HEIGHT // 2 + 13), (OFFSET_H * 2 + WIDTH - 10, OFFSET_V + HEIGHT // 2 + 13), 3)


def main():
    pygame.init()

    screen = pygame.display.set_mode(
        (WIDTH + (OFFSET_H * 2), HEIGHT + (OFFSET_V * 2)))
    pygame.display.set_caption("Chess")
    clock = pygame.time.Clock()

    board = Board(CELL_SIZE, OFFSET_H)

    running = True
    game_over = False
    end_message_alpha = 0
    white_time = black_time = TOTAL_TIME
    last_tick = pygame.time.get_ticks()
    pgn_saved = False
    result = ""
    termination = ""
    flip_timer = 0

    # moves_list = ['e4', 'e5', 'Nf3', 'Nc6']
    # make_moves(moves_list, board)

    def restart_game():
        board.initialize_pieces()
        board.current_turn = 'white'
        board.selected_piece = None
        board.available_moves = []
        board.valid_moves_dirty = True
        board.board_flipped = False
        board.captured_pieces = {'white': [], 'black': []}
        board.en_passant_target = None
        board.move_history = []
        board.last_captured = None
        board.moved_piece_prev_coord = None
        board.move_made = False

        nonlocal game_over, end_message_alpha
        game_over = False
        end_message_alpha = 0

        nonlocal white_time, black_time, last_tick, flip_timer
        flip_timer = 0
        white_time = black_time = TOTAL_TIME
        last_tick = pygame.time.get_ticks()

        nonlocal pgn_saved, result, winner, termination
        pgn_saved = False
        result = ""
        termination = ""

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game_over:
                    restart_game()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not game_over:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    board.handle_click(mouse_x, mouse_y, OFFSET_H, OFFSET_V)

        if board.move_made:
            flip_timer = pygame.time.get_ticks() + FLIP_DELAY_MS
            board.move_made = False

        if flip_timer and now >= flip_timer:
            board.board_flipped = not board.board_flipped
            flip_timer = 0

        if not game_over:
            now = pygame.time.get_ticks()
            delta_time = (now - last_tick) / 1000
            last_tick = now

            if board.current_turn == 'white':
                white_time -= delta_time
            else:
                black_time -= delta_time

        screen.fill(GRAY)

        board.draw(screen, WIDTH, HEIGHT, OFFSET_H, OFFSET_V)

        if white_time <= 0:
            board._draw_end_message(
                screen, "BLACK won by TIME OUT", end_message_alpha)
            termination = "BLACK won on time"
            result = "0-1"
            end_message_alpha = min(end_message_alpha + 5, 180)
            game_over = True
        elif black_time <= 0:
            board._draw_end_message(
                screen, "WHITE won by TIME OUT", end_message_alpha)
            termination = "WHITE won on time"
            result = "1-0"
            end_message_alpha = min(end_message_alpha + 5, 180)
            game_over = True

        draw_time(white_time, black_time, screen)

        if board.is_checkmate():
            # print(f"{board.current_turn} is in checkmate!")
            winner = 'BLACK' if board.current_turn == 'white' else 'WHITE'
            if winner == 'BLACK':
                result = '0-1'
            else:
                result = '1-0'

            board._draw_end_message(
                screen, f'{winner} won by CHECKMATE', end_message_alpha)
            end_message_alpha = min(end_message_alpha + 5, 180)
            termination = f'{winner} won by checkmate'
            game_over = True
        elif board.is_stalemate():
            # print(f"{board.current_turn} is in stalemate!")
            board._draw_end_message(screen, 'STALEMATE', end_message_alpha)
            end_message_alpha = min(end_message_alpha + 5, 180)
            game_over = True
            termination = "Game drawn by stalemate"
            result = "1/2-1/2"

        if game_over and not pgn_saved:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            os.makedirs("games", exist_ok=True)
            filename = f"game_{timestamp}.pgn"
            filepath = os.path.join("games", filename)

            pgn = generate_pgn(board.move_history, "WHITE",
                               "BLACK", result, termination, str(TOTAL_TIME))
            with open(filepath, "w", encoding="utf-8") as file:
                file.write(pgn)
            pgn_saved = True

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
