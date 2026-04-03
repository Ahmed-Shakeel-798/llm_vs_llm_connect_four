import pygame
import threading
from connect_four import ConnectFour
from player import LLMPlayer

OLLAMA_BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

player_x = LLMPlayer(OLLAMA_BASE_URL, "llama3.2", API_KEY, "X")
player_o = LLMPlayer(OLLAMA_BASE_URL, "llama3.2", API_KEY, "O")

board = ConnectFour()

players = {
    "X": player_x,
    "O": player_o
}

FPS = 30

WIDTH = 1000
HEIGHT = 650
CELL = 70

TOTAL_PARTS = 4

part_width = WIDTH // TOTAL_PARTS

LEFT_WIDTH = part_width - 10
RIGHT_WIDTH = part_width - 10

BOARD_WIDTH = (part_width * 2) # 600
BOARD_HEIGHT = board.ROWS * CELL

offset_x = LEFT_WIDTH + 10 + ( (BOARD_WIDTH - board.COLS * CELL) // 2) 
offset_y = 100

pygame.init()

clock = pygame.time.Clock()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Connect Four")

BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)

LEFT_TEXT_BOX = pygame.Rect(5, offset_y, LEFT_WIDTH, BOARD_HEIGHT)
RIGHT_TEXT_BOX = pygame.Rect(5 + LEFT_WIDTH + 5 + BOARD_WIDTH + 5, offset_y, RIGHT_WIDTH, BOARD_HEIGHT)

lines_X = ["Player X Logs", "----------------"]
lines_O = ["Player O Logs", "----------------"]

scroll_X = 0
scroll_O = 0

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
        

aiThinkingMessageFont = pygame.font.SysFont(None, 28)

def draw_ai_thinking():
    if not ai_thinking:
        return

    player = board.current_player

    # Text parts
    text_before = aiThinkingMessageFont.render("Player ", True, WHITE)
    text_after = aiThinkingMessageFont.render(" is thinking...", True, WHITE)

    # Color for X / O
    if player == "X":
        color = RED
    else:
        color = YELLOW

    text_player = aiThinkingMessageFont.render(player, True, color)

    # Compute total width
    total_width = (
        text_before.get_width()
        + text_player.get_width()
        + text_after.get_width()
    )

    start_x = (WIDTH - total_width) // 2
    y = HEIGHT - 120

    # Draw sequentially
    screen.blit(text_before, (start_x, y))
    screen.blit(text_player, (start_x + text_before.get_width(), y))
    screen.blit(
        text_after,
        (start_x + text_before.get_width() + text_player.get_width(), y)
    )


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


TEXT_BOX = pygame.Rect(50, 750, 500, 80) # x, y, width, height

lines = []
scroll_offset = 0
log_font = pygame.font.SysFont(None, 22)
line_height = 18

def wrap_text(text, font, max_width):
    words = text.split(" ")
    lines = []
    current = ""

    for word in words:
        test_line = current + (" " if current else "") + word
        width, _ = font.size(test_line)

        if width <= max_width:
            current = test_line
        else:
            lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines

def add_text(player, text):
    if player == "X":
        wrapped = wrap_text(text, log_font, LEFT_TEXT_BOX.width - 10)
        lines_X.extend(wrapped)
    else:
        wrapped = wrap_text(text, log_font, RIGHT_TEXT_BOX.width - 10)
        lines_O.extend(wrapped)

def draw_text_box(rect, lines, scroll):
    pygame.draw.rect(screen, GRAY, rect)
    pygame.draw.rect(screen, WHITE, rect, 2)

    clip = screen.get_clip()
    screen.set_clip(rect)

    y = rect.y - scroll

    for i, line in enumerate(lines):

        # Header styling (first line)
        if i == 0:
            text_surface = log_font.render(line, True, WHITE)
        else:
            text_surface = log_font.render(line, True, BLACK)

        screen.blit(text_surface, (rect.x + 5, y))
        y += line_height

    screen.set_clip(clip)


waiting_for_move = True

ai_thinking = False
pending_move = None
move_lock = threading.Lock()

running = True

while running:

    for event in pygame.event.get():

        if event.type == pygame.MOUSEBUTTONDOWN:

            mouse_pos = pygame.mouse.get_pos()

            if LEFT_TEXT_BOX.collidepoint(mouse_pos):
                if event.button == 4:
                    scroll_X = max(0, scroll_X - 20)
                elif event.button == 5:
                    max_scroll = max(0, len(lines_X) * line_height - LEFT_TEXT_BOX.height)
                    scroll_X = min(max_scroll, scroll_X + 20)

            elif RIGHT_TEXT_BOX.collidepoint(mouse_pos):
                if event.button == 4:
                    scroll_O = max(0, scroll_O - 20)
                elif event.button == 5:
                    max_scroll = max(0, len(lines_O) * line_height - RIGHT_TEXT_BOX.height)
                    scroll_O = min(max_scroll, scroll_O + 20)

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
    draw_ai_thinking()
    draw_reset_button()
    draw_winner()
    draw_text_box(LEFT_TEXT_BOX, lines_X, scroll_X)
    draw_text_box(RIGHT_TEXT_BOX, lines_O, scroll_O)

    pygame.display.update()

    if pending_move is not None and not game_over:

        with move_lock:
            move = pending_move
            pending_move = None

        add_text(board.current_player, f"plays column {move}")
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

    # FPS limiter
    clock.tick(FPS)

pygame.quit()