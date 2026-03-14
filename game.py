import pygame
from connect_four import ConnectFour
from player import LLMPlayer

player_x = LLMPlayer("llama3.2", "X")
player_o = LLMPlayer("llama3.2", "O")

players = {
    "X": player_x,
    "O": player_o
}

pygame.init()

WIDTH = 800
HEIGHT = 850
CELL = 100

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Connect Four")

BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)

board = ConnectFour()

BOARD_WIDTH = board.COLS * CELL
BOARD_HEIGHT = board.ROWS * CELL

offset_x = (WIDTH - BOARD_WIDTH) // 2
offset_y = (HEIGHT - BOARD_HEIGHT) // 2 + 40

font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 36)

winner = None
game_over = False

reset_button = pygame.Rect(WIDTH // 2 - 75, HEIGHT - 80, 150, 50)


def draw_heading():
    text = font.render("Connect 4 <3", True, WHITE)
    text_rect = text.get_rect(center=(WIDTH // 2, 40))
    screen.blit(text, text_rect)


def draw_board():
    for r in range(board.ROWS):
        for c in range(board.COLS):

            rect_x = offset_x + c * CELL
            rect_y = offset_y + r * CELL

            # Draw board tile
            pygame.draw.rect(
                screen,
                BLUE,
                (rect_x, rect_y, CELL, CELL)
            )

            # Draw empty hole
            pygame.draw.circle(
                screen,
                BLACK,
                (rect_x + CELL // 2, rect_y + CELL // 2),
                CELL // 2 - 5
            )

            piece = board.board[r][c]

            if piece == "X":
                pygame.draw.circle(
                    screen,
                    RED,
                    (rect_x + CELL // 2, rect_y + CELL // 2),
                    CELL // 2 - 5
                )

            elif piece == "O":
                pygame.draw.circle(
                    screen,
                    YELLOW,
                    (rect_x + CELL // 2, rect_y + CELL // 2),
                    CELL // 2 - 5
                )


def draw_reset_button():
    pygame.draw.rect(screen, GRAY, reset_button)
    text = small_font.render("Reset", True, BLACK)
    text_rect = text.get_rect(center=reset_button.center)
    screen.blit(text, text_rect)


def draw_winner():
    if winner:
        popup = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 80, 400, 160)
        pygame.draw.rect(screen, WHITE, popup)
        pygame.draw.rect(screen, BLACK, popup, 3)

        text = font.render(f"{winner} wins!", True, BLACK)
        text_rect = text.get_rect(center=popup.center)

        screen.blit(text, text_rect)


running = True
waiting_for_move = True

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:

            mouse_pos = event.pos

            if reset_button.collidepoint(mouse_pos):
                board.reset()
                winner = None
                game_over = False
                waiting_for_move = True

    screen.fill(BLACK)

    draw_heading()
    draw_board()
    draw_reset_button()
    draw_winner()

    pygame.display.update()

    # ----- AI move happens AFTER rendering -----

    if not game_over and waiting_for_move:

        waiting_for_move = False

        current_mark = board.current_player
        player = players[current_mark]

        print(f"\nPlayer {current_mark}'s turn")

        try:
            result = player.make_move(board)

            print("LLM response:")
            print(result)

            move = result["move"]

            row, col, player_mark, win = board.move(move)
            board.print_board()

            if win:
                winner = player_mark
                game_over = True

        except Exception as e:
            print(f"\nError occurred: {e}")

            winner = "O" if current_mark == "X" else "X"
            print(f"Player {winner} wins by opponent error.")

            game_over = True

        waiting_for_move = True

pygame.quit()