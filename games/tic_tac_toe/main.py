import pygame
import sys
import copy
from dashboard import dashboard_loop

pygame.init()

# Constants
WIDTH, HEIGHT = 500, 600
ROWS, COLS = 3, 3
SQSIZE = WIDTH // COLS
LINE_WIDTH = 5
CIRCLE_WIDTH = 15
CROSS_WIDTH = 20
RADIUS = SQSIZE // 4
OFFSET = 40

# Colors
# BG_COLOR = (28, 170, 156)
# LINE_COLOR = (23, 145, 135)
# CIRCLE_COLOR = (239, 231, 200)
# CROSS_COLOR = (66, 66, 66)
# WIN_LINE_COLOR = (255, 0, 0)
# TEXT_COLOR = (255, 255, 255)
# SUGGEST_COLOR = (255, 255, 0)

BG_COLOR = (34, 40, 49)
LINE_COLOR = (57, 62, 70)
CIRCLE_COLOR = (0, 173, 181)
CROSS_COLOR = (238, 238, 238)
TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR = (60, 60, 90)
BUTTON_HOVER_COLOR = (90, 90, 130)
SUGGEST_COLOR = (255, 215, 0)
WIN_LINE_COLOR = (255, 99, 71)


screen_width = 800
screen_height = 600
# Screen
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Tic Tac Toe")

# Fonts
FONT = pygame.font.SysFont(None, 40)
BIG_FONT = pygame.font.SysFont(None, 50)

# Game variables
board = [[None]*3 for _ in range(3)]
player = "X"
game_over = False
winner = None
win_line = None
suggested_move = None
ai_delay_timer = 0


MARGIN_LEFT = 140  # Set the left margin value

def draw_board():
    screen.fill(BG_COLOR)

    # Draw grid lines
    for i in range(1, 3):
        pygame.draw.line(screen, LINE_COLOR, (MARGIN_LEFT, i * SQSIZE), (MARGIN_LEFT + WIDTH, i * SQSIZE), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (i * SQSIZE + MARGIN_LEFT, 0), (i * SQSIZE + MARGIN_LEFT, WIDTH), LINE_WIDTH)

    # Draw symbols (X and O)
    for row in range(ROWS):
        for col in range(COLS):
            x_center = col * SQSIZE + SQSIZE // 2 + MARGIN_LEFT
            y_center = row * SQSIZE + SQSIZE // 2
            if board[row][col] == "X":
                pygame.draw.line(screen, CROSS_COLOR,
                                 (x_center - OFFSET, y_center - OFFSET),
                                 (x_center + OFFSET, y_center + OFFSET), CROSS_WIDTH)
                pygame.draw.line(screen, CROSS_COLOR,
                                 (x_center - OFFSET, y_center + OFFSET),
                                 (x_center + OFFSET, y_center - OFFSET), CROSS_WIDTH)
            elif board[row][col] == "O":
                pygame.draw.circle(screen, CIRCLE_COLOR,
                                   (x_center, y_center), RADIUS, CIRCLE_WIDTH)

    # Highlight suggested move
    if suggested_move and not game_over:
        row, col = suggested_move
        pygame.draw.rect(screen, SUGGEST_COLOR,
                         (col * SQSIZE + 10 + MARGIN_LEFT, row * SQSIZE + 10, SQSIZE - 20, SQSIZE - 20), 3)

    # Winning line
    if win_line:
        pygame.draw.line(screen, WIN_LINE_COLOR, win_line[0], win_line[1], 10)

    # End game message
    if game_over:
        msg = f"Player {winner} wins!" if winner else "It's a draw!"
        text = BIG_FONT.render(msg, True, TEXT_COLOR)
        screen.blit(text, (MARGIN_LEFT + WIDTH // 2 - text.get_width() // 2, WIDTH + 10))

        # Restart & Dashboard Buttons
        restart_y = HEIGHT - 50
        button_width = 180
        button_height = 40
        gap = 20
        restart_x = WIDTH // 2 - button_width - gap // 2 + MARGIN_LEFT
        dashboard_x = WIDTH // 2 + gap // 2 + MARGIN_LEFT

        # Restart Button
        restart_rect = pygame.Rect(restart_x, restart_y, button_width, button_height)
        pygame.draw.rect(screen, BUTTON_COLOR, restart_rect, border_radius=12)
        rtext = FONT.render("Restart", True, TEXT_COLOR)
        screen.blit(rtext, (restart_x + button_width // 2 - rtext.get_width() // 2, restart_y + 8))

        # Dashboard Button
        dashboard_rect = pygame.Rect(dashboard_x, restart_y, button_width, button_height)
        pygame.draw.rect(screen, BUTTON_COLOR, dashboard_rect, border_radius=12)
        dtext = FONT.render("Dashboard", True, TEXT_COLOR)
        screen.blit(dtext, (dashboard_x + button_width // 2 - dtext.get_width() // 2, restart_y + 8))

        return restart_rect, None, dashboard_rect

    # Suggest Move Button
    suggest_rect = pygame.Rect(WIDTH // 2 - 100 + MARGIN_LEFT, HEIGHT - 80, 220, 50)
    pygame.draw.rect(screen, BUTTON_COLOR, suggest_rect, border_radius=12)
    stex = FONT.render("Suggest Move", True, TEXT_COLOR)
    screen.blit(stex, (suggest_rect.centerx - stex.get_width() // 2, suggest_rect.y + 12))

    return None, suggest_rect, None


def check_winner():
    global winner, win_line, game_over

    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != None:
            winner = board[i][0]
            win_line = ((MARGIN_LEFT + 20, i * SQSIZE + SQSIZE // 2), (MARGIN_LEFT + WIDTH - 20, i * SQSIZE + SQSIZE // 2))
            break
        if board[0][i] == board[1][i] == board[2][i] != None:
            winner = board[0][i]
            win_line = ((MARGIN_LEFT + i * SQSIZE + SQSIZE // 2, 20), (MARGIN_LEFT + i * SQSIZE + SQSIZE // 2, WIDTH - 20))
            break

    if board[0][0] == board[1][1] == board[2][2] != None:
        winner = board[0][0]
        win_line = ((MARGIN_LEFT + 20, 20), (MARGIN_LEFT + WIDTH - 20, WIDTH - 20))
    elif board[0][2] == board[1][1] == board[2][0] != None:
        winner = board[0][2]
        win_line = ((MARGIN_LEFT + WIDTH - 20, 20), (MARGIN_LEFT + 20, WIDTH - 20))

    if winner or all(all(cell is not None for cell in row) for row in board):
        game_over = True

def check_winner_simulation(temp_board):
    # Returns 'X', 'O' or None for the winner without affecting game state
    for i in range(3):
        if temp_board[i][0] == temp_board[i][1] == temp_board[i][2] != None:
            return temp_board[i][0]
        if temp_board[0][i] == temp_board[1][i] == temp_board[2][i] != None:
            return temp_board[0][i]

    if temp_board[0][0] == temp_board[1][1] == temp_board[2][2] != None:
        return temp_board[0][0]
    if temp_board[0][2] == temp_board[1][1] == temp_board[2][0] != None:
        return temp_board[0][2]

    return None


def minimax(b, is_maximizing):
    temp_winner = check_winner_simulation(b)
    if temp_winner == "O":
        return 1
    elif temp_winner == "X":
        return -1
    elif all(all(cell is not None for cell in row) for row in b):
        return 0

    if is_maximizing:
        best_score = -float('inf')
        for i in range(3):
            for j in range(3):
                if b[i][j] is None:
                    b[i][j] = "O"
                    score = minimax(b, False)
                    b[i][j] = None
                    best_score = max(score, best_score)
        return best_score
    else:
        best_score = float('inf')
        for i in range(3):
            for j in range(3):
                if b[i][j] is None:
                    b[i][j] = "X"
                    score = minimax(b, True)
                    b[i][j] = None
                    best_score = min(score, best_score)
        return best_score


def best_move(for_player="O"):
    best_score = -float('inf') if for_player == "O" else float('inf')
    move = None
    for i in range(3):
        for j in range(3):
            if board[i][j] is None:
                board[i][j] = for_player
                score = minimax(copy.deepcopy(board), for_player == "X")
                board[i][j] = None
                if (for_player == "O" and score > best_score) or (for_player == "X" and score < best_score):
                    best_score = score
                    move = (i, j)
    return move


def reset():
    global board, player, game_over, winner, win_line, suggested_move, ai_delay_timer
    board = [[None]*3 for _ in range(3)]
    player = "X"
    game_over = False
    winner = None
    win_line = None
    suggested_move = None
    ai_delay_timer = 0

def run():
    global player, game_over, winner, win_line, board, suggested_move, ai_delay_timer
    clock = pygame.time.Clock()
    AI_DELAY_MS = 500
    waiting_for_ai = False
    ai_timer_start = 0

    while True:
        # restart_btn, suggest_btn = draw_board()
        restart_btn, suggest_btn, dashboard_btn = draw_board()

        pygame.display.update()
        clock.tick(60)

        if waiting_for_ai and pygame.time.get_ticks() - ai_timer_start > AI_DELAY_MS:
            move = best_move()
            if move:
                board[move[0]][move[1]] = "O"
            check_winner()
            player = "X"
            waiting_for_ai = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if not game_over and event.type == pygame.MOUSEBUTTONDOWN and player == "X":
                x, y = pygame.mouse.get_pos()
                if x >= MARGIN_LEFT:
                    col = (x - MARGIN_LEFT) // SQSIZE
                    row = y // SQSIZE
                if row < 3 and col < 3 and board[row][col] is None:
                    board[row][col] = "X"
                    suggested_move = None
                    check_winner()
                    player = "O"
                    ai_timer_start = pygame.time.get_ticks()
                    waiting_for_ai = True
            
            if not game_over and event.type == pygame.MOUSEBUTTONDOWN:
                if suggest_btn and suggest_btn.collidepoint(pygame.mouse.get_pos()):
                    suggested_move = best_move(for_player="X")

            if game_over and event.type == pygame.MOUSEBUTTONDOWN:
                if restart_btn and restart_btn.collidepoint(pygame.mouse.get_pos()):
                    reset()
                elif dashboard_btn and dashboard_btn.collidepoint(pygame.mouse.get_pos()):
                    print("Back to dashboard")  # Replace this with actual navigation if integrated
                    dashboard_loop()
                

if __name__ == "__main__":
    run()
