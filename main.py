import pygame
from classes import Board

WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
CELL_SIZE = WIDTH // COLS


def main():
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess")
    clock = pygame.time.Clock()

    board = Board(CELL_SIZE)

    running = True
    game_over = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    board.handle_click(mouse_x, mouse_y)

        if board.is_checkmate():
            print(f"{board.current_turn} is in checkmate!")
            game_over = True
        elif board.is_stalemate():
            print(f"{board.current_turn} is in stalemate!")
            game_over = True

        board.draw(screen, WIDTH, HEIGHT)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
