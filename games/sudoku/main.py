import pygame
import random
import copy
from dashboard import dashboard_loop

pygame.init()

# Basic setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku Game")
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 28)
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BLUE = (173, 216, 230)
GRAY = (200, 200, 200)

# Global variables
selected_cell = None
score = 0
message = ""
message_timer = 0
move_history = []
current_level_name = "easy"

# Sample solvable boards
levels = {
    "easy": [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ],
    "medium": [
        [0, 0, 0, 2, 6, 0, 7, 0, 1],
        [6, 8, 0, 0, 7, 0, 0, 9, 0],
        [1, 9, 0, 0, 0, 4, 5, 0, 0],
        [8, 2, 0, 1, 0, 0, 0, 4, 0],
        [0, 0, 4, 6, 0, 2, 9, 0, 0],
        [0, 5, 0, 0, 0, 3, 0, 2, 8],
        [0, 0, 9, 3, 0, 0, 0, 7, 4],
        [0, 4, 0, 0, 5, 0, 0, 3, 6],
        [7, 0, 3, 0, 1, 8, 0, 0, 0],
    ],
}
solutions = {
    "easy": [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ],
"medium": [
    [4, 3, 5, 2, 6, 9, 7, 8, 1],
    [6, 8, 2, 5, 7, 1, 3, 9, 4],
    [1, 9, 7, 8, 3, 4, 5, 6, 2],
    [8, 2, 6, 1, 9, 5, 4, 3, 7],
    [3, 7, 4, 6, 8, 2, 9, 1, 5],
    [9, 5, 1, 7, 4, 3, 6, 2, 8],
    [5, 1, 9, 3, 2, 6, 8, 7, 4],
    [2, 4, 8, 9, 5, 7, 1, 3, 6],
    [7, 6, 3, 4, 1, 8, 2, 5, 9],
]

}

current_level = copy.deepcopy(levels["easy"])
initial_board = copy.deepcopy(current_level)


GRID_ORIGIN_X = (WIDTH - 450) // 2  # 450 = 9 cells * 50px
GRID_ORIGIN_Y = 30
CELL_SIZE = 50

def draw_message_box(message):
    popup_width, popup_height = 500, 100  # Increased width and height
    popup_x = (WIDTH - popup_width) // 2
    popup_y = (HEIGHT - popup_height) // 2
    popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)

    # Draw the box
    pygame.draw.rect(screen, GRAY, popup_rect)
    pygame.draw.rect(screen, BLACK, popup_rect, 2)

    # Word wrap
    words = message.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        if small_font.size(test_line)[0] < popup_width - 40:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)

    # Render each line of text
    for i, line in enumerate(lines):
        text_surface = small_font.render(line.strip(), True, BLACK)
        screen.blit(text_surface, (popup_x + 20, popup_y + 20 + i * 25))

# Draw the Sudoku grid and numbers
def draw_board():
    # Gradient background from top to bottom
    for y in range(HEIGHT):
        r = 173 + (255 - 173) * y // HEIGHT  # From LIGHT_BLUE to WHITE
        g = 216 + (255 - 216) * y // HEIGHT
        b = 230 + (255 - 230) * y // HEIGHT
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

    # Grid top-left origin
    grid_x = GRID_ORIGIN_X
    grid_y = GRID_ORIGIN_Y
    grid_size = CELL_SIZE * 9

    # Draw grid lines
    for i in range(10):
        line_thickness = 4 if i % 3 == 0 else 1
        pygame.draw.line(screen, BLACK, (grid_x + i * CELL_SIZE, grid_y),
                         (grid_x + i * CELL_SIZE, grid_y + grid_size), line_thickness)
        pygame.draw.line(screen, BLACK, (grid_x, grid_y + i * CELL_SIZE),
                         (grid_x + grid_size, grid_y + i * CELL_SIZE), line_thickness)

    # Draw numbers
    for row in range(9):
        for col in range(9):
            num = current_level[row][col]
            if num != 0:
                text = font.render(str(num), True, BLACK)
                screen.blit(text, (grid_x + 15 + col * CELL_SIZE, grid_y + 10 + row * CELL_SIZE))

    # Highlight selected cell
    if selected_cell:
        highlight = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        highlight.fill((173, 216, 230, 70))
        screen.blit(highlight, (grid_x + selected_cell[1] * CELL_SIZE, grid_y + selected_cell[0] * CELL_SIZE))

    # Score text below grid
    score_text = font.render(f"Moves: {score}", True, BLACK)
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, grid_y + grid_size + 10))

    # Buttons
    button_y = grid_y + grid_size + 50
    button_height = 45
    button_widths = [160, 200, 220]
    button_spacing = 40
    total_width = sum(button_widths) + button_spacing * (len(button_widths) - 1)
    start_x = (WIDTH - total_width) // 2

    restart_button = pygame.Rect(start_x, button_y, button_widths[0], button_height)
    suggest_button = pygame.Rect(start_x + button_widths[0] + button_spacing, button_y, button_widths[1], button_height)
    dashboard_button = pygame.Rect(start_x + button_widths[0] + button_widths[1] + 2 * button_spacing, button_y, button_widths[2], button_height)

    for btn in [restart_button, suggest_button, dashboard_button]:
        pygame.draw.rect(screen, GRAY, btn, border_radius=10)
        pygame.draw.rect(screen, BLACK, btn, 2, border_radius=10)

    screen.blit(small_font.render("Restart", True, BLACK), (restart_button.centerx - 35, restart_button.centery - 10))
    screen.blit(small_font.render("Suggest Move", True, BLACK), (suggest_button.centerx - 60, suggest_button.centery - 10))
    screen.blit(small_font.render("Move to Dashboard", True, BLACK), (dashboard_button.centerx - 90, dashboard_button.centery - 10))

    # Undo button at bottom-right of grid
    undo_button = pygame.Rect(grid_x + grid_size - 80, grid_y + grid_size + 10, 100, 35)
    pygame.draw.rect(screen, GRAY, undo_button, border_radius=8)
    pygame.draw.rect(screen, BLACK, undo_button, 2, border_radius=8)
    screen.blit(small_font.render("Undo", True, BLACK), (undo_button.centerx - 20, undo_button.centery - 10))

    # Message popup
    if message:
        draw_message_box(message)

    return restart_button, suggest_button, dashboard_button, undo_button

def is_valid_move(board, row, col, num):
    # Check row
    for c in range(9):
        if board[row][c] == num:
            return False

    # Check column
    for r in range(9):
        if board[r][col] == num:
            return False

    # Check 3x3 subgrid
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for r in range(start_row, start_row + 3):
        for c in range(start_col, start_col + 3):
            if board[r][c] == num:
                return False

    return True

# Suggest move functionality (just saves current state for now)
def suggest_move():
    global message, message_timer, current_level, initial_board, current_level_name, score, selected_cell, move_history # 1. Save current state
    with open("sudoku_state.txt", "w") as file:
        file.write(f"Moves: {score}\n")
        for row in current_level:
            file.write(",".join(str(num) for num in row) + "\n")

    solution_board = solutions[current_level_name]  # Match the current level
    # 2. First, check if the player's moves are correct so far
    for row in range(9):
        for col in range(9):
            if initial_board[row][col] == 0:  # Only check player-modifiable cells
                entered = current_level[row][col]
                correct = solution_board[row][col]
                if entered != 0 and entered != correct:
                    message = (f"Move at ({row + 1}, {col + 1}) is not 100% sure. "
                               f"First try other blocks where you are 100% sure.")
                    message_timer = pygame.time.get_ticks()
                    return

    # 3. If all moves so far are correct, suggest next best move
    for row in range(9):
        for col in range(9):
            if initial_board[row][col] == 0 and current_level[row][col] == 0:
                hint = solution_board[row][col]
                message = f"Next move suggestion: Place {hint} at ({row + 1}, {col + 1})"
                message_timer = pygame.time.get_ticks()
                return

    # 4. If board is complete and all moves are correct
    # 4. If board is complete and all moves are correct
    message = "Board complete and correct!"
    message_timer = pygame.time.get_ticks()

    # Move to next level if available
    if current_level_name == "easy":
        current_level_name = "medium"
        current_level = copy.deepcopy(levels[current_level_name])
        initial_board = copy.deepcopy(current_level)
        message = "Great! Moving to medium level."
        score = 0
        selected_cell = None
        move_history.clear()

    # If no empty cells are found
    # message = "Board already complete!"
    # message_timer = pygame.time.get_ticks()


# Reset the game
def restart_game():
    global current_level, score, selected_cell
    current_level = copy.deepcopy(levels[current_level_name])
    initial_board = copy.deepcopy(current_level)

    score = 0
    selected_cell = None

# Main loop
def run():
    global message, message_timer, running, selected_cell, score
    running = True  # Ensure this is reset each time the game is started

    while running:
        clock.tick(60)
        if message and pygame.time.get_ticks() - message_timer > 3000:
            message = ""

        restart_button, suggest_button, dashboard_button, undo_button = draw_board()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                # if 50 <= x < 500 and 50 <= y < 500:
                if (GRID_ORIGIN_X <= x < GRID_ORIGIN_X + 9 * CELL_SIZE and GRID_ORIGIN_Y <= y < GRID_ORIGIN_Y + 9 * CELL_SIZE):
                    col = (x - GRID_ORIGIN_X) // CELL_SIZE
                    row = (y - GRID_ORIGIN_Y) // CELL_SIZE
                    selected_cell = (row, col)
                elif restart_button.collidepoint(event.pos):
                    restart_game()
                elif suggest_button.collidepoint(event.pos):
                    suggest_move()
                elif dashboard_button.collidepoint(event.pos):
                    print("Returning to Dashboard...")
                    return  # Exit the loop and return to dashboard
                elif undo_button.collidepoint(event.pos):
                    if move_history:
                        last_row, last_col, prev_val = move_history.pop()
                        current_level[last_row][last_col] = prev_val
                        score = max(0, score - 1)

            if event.type == pygame.KEYDOWN:
                if selected_cell:
                    row, col = selected_cell
                    if initial_board[row][col] == 0:
                        if event.key in range(pygame.K_1, pygame.K_9 + 1):
                            num = event.key - pygame.K_0
                            if is_valid_move(current_level, row, col, num):
                                move_history.append((row, col, current_level[row][col]))
                                current_level[row][col] = num
                                score += 1
                            else:
                                message = f"Invalid move: {num} at ({row + 1}, {col + 1})"
                                message_timer = pygame.time.get_ticks()

        pygame.display.update()

    pygame.quit()  # Optional if you're fully closing the app
