import pygame
from classes import Board

WIDTH, HEIGHT = 640, 640
OFFSET = 350
ROWS, COLS = 8, 8
CELL_SIZE = WIDTH // COLS

GRAY = (128, 128, 128)
TOTAL_TIME = 600


def format_time(seconds):
    minutes = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{minutes:02}:{secs:02}"


def main():
    pygame.init()

    screen = pygame.display.set_mode((WIDTH + (OFFSET * 2), HEIGHT))
    pygame.display.set_caption("Chess")
    clock = pygame.time.Clock()

    board = Board(CELL_SIZE, OFFSET)

    running = True
    game_over = False
    end_message_alpha = 0
    white_time = black_time = TOTAL_TIME
    last_tick = pygame.time.get_ticks()

    def restart_game():
        board.initialize_pieces()
        board.current_turn = 'white'
        board.selected_piece = None
        board.available_moves = []
        board.valid_moves_dirty = True
        board.board_flipped = False
        board.captured_pieces = {'white': [], 'black': []}
        board.en_passant_target = None
        nonlocal game_over, end_message_alpha
        game_over = False
        end_message_alpha = 0
        nonlocal white_time, black_time, last_tick
        white_time = black_time = TOTAL_TIME
        last_tick = pygame.time.get_ticks()

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
                    board.handle_click(mouse_x, mouse_y, OFFSET)

        if not game_over:
            now = pygame.time.get_ticks()
            delta_time = (now - last_tick) / 1000
            last_tick = now

            if board.current_turn == 'white':
                white_time -= delta_time
            else:
                black_time -= delta_time

        screen.fill(GRAY)

        board.draw(screen, WIDTH, HEIGHT, OFFSET)

        if white_time <= 0:
            board._draw_end_message(
                screen, "BLACK won by TIME OUT", end_message_alpha)
            end_message_alpha = min(end_message_alpha + 5, 180)
            game_over = True
        elif black_time <= 0:
            board._draw_end_message(
                screen, "WHITE won by TIME OUT", end_message_alpha)
            end_message_alpha = min(end_message_alpha + 5, 180)
            game_over = True

        font = pygame.font.Font(None, 36)

        white_time_text = font.render(
            f"White: {format_time(white_time)}", True, (255, 255, 255))
        black_time_text = font.render(
            f"Black: {format_time(black_time)}", True, (255, 255, 255))

        screen.blit(white_time_text, (OFFSET + WIDTH + 10, HEIGHT // 2 - 90))
        screen.blit(black_time_text, (OFFSET + WIDTH + 10, HEIGHT // 2 + 50))

        if board.is_checkmate():
            # print(f"{board.current_turn} is in checkmate!")
            winner = 'BLACK' if board.current_turn == 'white' else 'WHITE'
            board._draw_end_message(
                screen, f'{winner} won by CHECKMATE', end_message_alpha)
            end_message_alpha = min(end_message_alpha + 5, 180)
            game_over = True
        elif board.is_stalemate():
            # print(f"{board.current_turn} is in stalemate!")
            board._draw_end_message(screen, 'STALEMATE', end_message_alpha)
            end_message_alpha = min(end_message_alpha + 5, 180)
            game_over = True

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
