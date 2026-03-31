import pygame
import threading
from connect_four import ConnectFour
from player import LLMPlayer

OLLAMA_BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

player_x = LLMPlayer(OLLAMA_BASE_URL, "llama3.2", API_KEY, "X")
player_o = LLMPlayer(OLLAMA_BASE_URL, "llama3.2", API_KEY, "O")

players = {
    "X": player_x,
    "O": player_o
}

pygame.init()

WIDTH = 600
HEIGHT = 750
CELL = 75

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

def compute_move():
    global pending_move, ai_thinking, winner, game_over

    current_mark = board.current_player
    player = players[current_mark]

    try:
        result = player.make_move(board)
        print(player.mark + " move result:" + str(result))

        move = result["move"]

        with move_lock:
            pending_move = move

    except Exception as e:
        print(f"\nError occurred: {e}")

        winner = "O" if current_mark == "X" else "X"
        game_over = True

    finally:
        ai_thinking = False


waiting_for_move = True

ai_thinking = False
pending_move = None
move_lock = threading.Lock()

running = True

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
                pending_move = None
                ai_thinking = False

    screen.fill(BLACK)

    draw_heading()
    draw_board()
    draw_reset_button()
    draw_winner()

    pygame.display.update()

    if pending_move is not None and not game_over:

        with move_lock:
            move = pending_move
            pending_move = None

        row, col, player_mark, win = board.move(move)
        board.print_board()

        if win:
            winner = player_mark
            game_over = True

    # ----- AI move happens AFTER rendering -----

    if not game_over and not ai_thinking:

        ai_thinking = True

        thread = threading.Thread(target=compute_move)
        thread.daemon = True
        thread.start()

pygame.quit()