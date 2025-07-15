import pygame
from classes import Board

WIDTH, HEIGHT = 640, 640
OFFSET = 350
ROWS, COLS = 8, 8
CELL_SIZE = WIDTH // COLS

GRAY = (128, 128, 128)


def main():
    pygame.init()

    screen = pygame.display.set_mode((WIDTH + (OFFSET * 2), HEIGHT))
    pygame.display.set_caption("Chess")
    clock = pygame.time.Clock()

    board = Board(CELL_SIZE, OFFSET)

    running = True
    game_over = False
    end_message_alpha = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not game_over:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    board.handle_click(mouse_x, mouse_y, OFFSET)

        screen.fill(GRAY)

        board.draw(screen, WIDTH, HEIGHT, OFFSET)

        if board.is_checkmate():
            # print(f"{board.current_turn} is in checkmate!")
            winner = 'BLACK' if board.current_turn == 'white' else 'WHITE'
            board._draw_end_message(
                screen, f'{winner} won by CHECKMATE', end_message_alpha)
            end_message_alpha = min(end_message_alpha + 1, 180)
            game_over = True
        elif board.is_stalemate():
            # print(f"{board.current_turn} is in stalemate!")
            board._draw_end_message(screen, 'STALEMATE', end_message_alpha)
            end_message_alpha = min(end_message_alpha + 1, 180)
            game_over = True

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
