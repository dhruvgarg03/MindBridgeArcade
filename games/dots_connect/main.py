import math
import time
import pygame
from dashboard import dashboard_loop

SCREEN = WIDTH, HEIGHT = 800, 600
CELLSIZE = 80
PADDING = 40
ROWS = COLS = (WIDTH - 4 * PADDING) // CELLSIZE
# Position buttons below the grid
button_height = 40
button_width = 240
button_y = HEIGHT - PADDING - 20  # below the grid, using padding

restart_button = pygame.Rect(PADDING, button_y, button_width-70, button_height)
suggest_button = pygame.Rect(WIDTH - button_width - PADDING+20, button_y, button_width-80, button_height)
dashboard_button = pygame.Rect(WIDTH // 2 - button_width // 2, button_y, button_width-40, button_height)

pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
win.fill((30, 30, 47))

WHITE = (255, 255, 255)
RED = (235, 87, 87)
BLUE = (86, 156, 214)
GREEN = (46, 204, 113)
DARK_BG = (30, 30, 47)

font = pygame.font.SysFont('Helvetica', 22)

class Cell:
    def __init__(self, r, c):
        self.r = r
        self.c = c
        self.index = self.r * ROWS + self.c

        self.rect = pygame.Rect((self.c * CELLSIZE + 2 * PADDING, self.r * CELLSIZE +
                                 3 * PADDING, CELLSIZE, CELLSIZE))
        self.left = self.rect.left
        self.top = self.rect.top
        self.right = self.rect.right
        self.bottom = self.rect.bottom
        self.edges = [
            [(self.left, self.top), (self.right, self.top)],
            [(self.right, self.top), (self.right, self.bottom)],
            [(self.right, self.bottom), (self.left, self.bottom)],
            [(self.left, self.bottom), (self.left, self.top)]
        ]
        self.sides = [False, False, False, False]
        self.winner = None

    def checkwin(self, winner):
        if not self.winner:
            if self.sides == [True] * 4:
                self.winner = winner
                if winner == 'X':
                    self.color = GREEN
                else:
                    self.color = RED
                self.text = font.render(self.winner, True, WHITE)

                return 1
        return 0

    def update(self, win):
        if self.winner:
            pygame.draw.rect(win, self.color, self.rect)
            win.blit(self.text, (self.rect.centerx - 5, self.rect.centery - 7))

        for index, side in enumerate(self.sides):
            if side:
                pygame.draw.line(win, WHITE, (self.edges[index][0]),
                                 (self.edges[index][1]), 2)


def create_cells():
    cells = []
    for r in range(ROWS):
        for c in range(COLS):
            cell = Cell(r, c)
            cells.append(cell)
    return cells


def reset_cells():
    pos = None
    ccell = None
    up = False
    right = False
    bottom = False
    left = False
    return pos, ccell, up, right, bottom, left


def reset_score():
    fillcount = 0
    p1_score = 0
    p2_score = 0
    return fillcount, p1_score, p2_score


def reset_player():
    turn = 0
    players = ['X', 'O']
    player = players[turn]
    next_turn = False
    return turn, players, player, next_turn

def suggest_move(cells, player):
    # Check if there's a winning move for the current player
    for cell in cells:
        if cell.winner is None:  # Only check cells that are not already won
            for i, side in enumerate(cell.sides):
                if not side:
                    # Temporarily complete this side to see if it will win
                    cell.sides[i] = True
                    if cell.checkwin(player):
                        # If this side completes the box and wins for the current player
                        return cell, i
                    # Undo the move to check for other possibilities
                    cell.sides[i] = False

    # If no winning move, return a random available move (first available)
    for cell in cells:
        if cell.sides.count(True) < 4 and not cell.winner:
            for i, side in enumerate(cell.sides):
                if not side:
                    return cell, i  # return first available move

    return None, None  # No available moves left



def run():
    global running, gameover, cells, pos, ccell, up, right, bottom, left
    global fillcount, p1_score, p2_score, turn, players, player, next_turn

    gameover = False
    cells = create_cells()
    pos, ccell, up, right, bottom, left = reset_cells()
    fillcount, p1_score, p2_score = reset_score()
    turn, players, player, next_turn = reset_player()

    running = True
    suggested_move = None  # Variable to store suggested move
    suggest_time = None    # Time when the suggestion was made

    while running:
        win.fill(DARK_BG)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos

                if restart_button.collidepoint(pos):
                    gameover = False
                    cells = create_cells()
                    pos, ccell, up, right, bottom, left = reset_cells()
                    fillcount, p1_score, p2_score = reset_score()
                    turn, players, player, next_turn = reset_player()

                elif suggest_button.collidepoint(pos):
                    cell, side = suggest_move(cells, player)
                    if cell is not None and side is not None:
                        suggested_move = (cell, side)  # Store suggested move
                        suggest_time = time.time()  # Store the time when suggestion is made
                        pygame.draw.line(win, GREEN, cell.edges[side][0], cell.edges[side][1], 4)
                        pygame.display.update()
                        print(f"Suggested move: Cell {cell.index}, Side {side}")
                    else:
                        print("No available move found.")
                
                elif dashboard_button.collidepoint(pos):
                    print("Moving to Dashboard...")
                    dashboard_loop()
                    running = False
                    pygame.quit()
                    # return

            if event.type == pygame.MOUSEBUTTONUP:
                pos = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r:
                    gameover = False
                    cells = create_cells()
                    pos, ccell, up, right, bottom, left = reset_cells()
                    fillcount, p1_score, p2_score = reset_score()
                    turn, players, player, next_turn = reset_player()
                if not gameover:
                    if event.key == pygame.K_UP:
                        up = True
                    if event.key == pygame.K_RIGHT:
                        right = True
                    if event.key == pygame.K_DOWN:
                        bottom = True
                    if event.key == pygame.K_LEFT:
                        left = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    up = False
                if event.key == pygame.K_RIGHT:
                    right = False
                if event.key == pygame.K_DOWN:
                    bottom = False
                if event.key == pygame.K_LEFT:
                    left = False

        # Draw grid circles
        for r in range(ROWS + 1):
            for c in range(COLS + 1):
                pygame.draw.circle(win, WHITE, (c * CELLSIZE + 2 * PADDING, r * CELLSIZE + 3 * PADDING), 2)

        # Draw cells
        for cell in cells:
            cell.update(win)
            if pos and cell.rect.collidepoint(pos):
                ccell = cell

        # Draw suggested move (if available)
        if suggested_move:
            # Check if the suggestion time is older than 1 second
            if time.time() - suggest_time < 1:  # 1 second delay for the suggestion
                cell, side = suggested_move
                pygame.draw.line(win, GREEN, cell.edges[side][0], cell.edges[side][1], 4)
            else:
                suggested_move = None  # Clear suggested move after 1 second

        # Process the user's moves
        if ccell:
            index = ccell.index
            if not ccell.winner:
                pygame.draw.circle(win, RED, (ccell.rect.centerx, ccell.rect.centery), 2)

            if up and not ccell.sides[0]:
                ccell.sides[0] = True
                if index - ROWS >= 0:
                    cells[index - ROWS].sides[2] = True
                next_turn = True
                up = right = bottom = left = False
            elif right and not ccell.sides[1]:
                ccell.sides[1] = True
                if (index + 1) % COLS > 0:
                    cells[index + 1].sides[3] = True
                next_turn = True
                up = right = bottom = left = False
            elif bottom and not ccell.sides[2]:
                ccell.sides[2] = True
                if index + ROWS < len(cells):
                    cells[index + ROWS].sides[0] = True
                next_turn = True
                up = right = bottom = left = False
            elif left and not ccell.sides[3]:
                ccell.sides[3] = True
                if (index % COLS) > 0:
                    cells[index - 1].sides[1] = True
                next_turn = True
                up = right = bottom = left = False

            res = ccell.checkwin(player)
            if res:
                fillcount += res
                if player == 'X':
                    p1_score += 1
                else:
                    p2_score += 1
                if fillcount == ROWS * COLS:
                    gameover = True

            if next_turn:
                turn = (turn + 1) % len(players)
                player = players[turn]
                next_turn = False

        # Display scores and game-over message
        p1img = font.render(f'Player 1 : {p1_score}', True, BLUE)
        p1rect = p1img.get_rect()
        p1rect.x, p1rect.y = 2 * PADDING, 15

        p2img = font.render(f'Player 2 : {p2_score}', True, BLUE)
        p2rect = p2img.get_rect()
        p2rect.right, p2rect.y = WIDTH - 2 * PADDING, 15

        win.blit(p1img, p1rect)
        win.blit(p2img, p2rect)
        if player == 'X':
            pygame.draw.line(win, BLUE, (p1rect.x, p1rect.bottom + 2), (p1rect.right, p1rect.bottom + 2), 1)
        else:
            pygame.draw.line(win, BLUE, (p2rect.x, p2rect.bottom + 2), (p2rect.right, p2rect.bottom + 2), 1)

        if gameover:
            rect = pygame.Rect((50, 100, WIDTH - 100, HEIGHT - 200))
            pygame.draw.rect(win, BLACK, rect)
            pygame.draw.rect(win, RED, rect, 2)

            over = font.render('Game Over', True, WHITE)
            win.blit(over, (rect.centerx - over.get_width() / 2, rect.y + 10))

            winner = '1' if p1_score > p2_score else '2'
            winner_img = font.render(f'Player {winner} Won', True, GREEN)
            win.blit(winner_img, (rect.centerx - winner_img.get_width() / 2, rect.centery - 10))

            msg = 'Press r:restart, q:quit'
            msgimg = font.render(msg, True, RED)
            win.blit(msgimg, (rect.centerx - msgimg.get_width() / 2, rect.centery + 20))

        # Draw buttons
        pygame.draw.rect(win, WHITE, (0, 0, WIDTH, HEIGHT), 2, border_radius=0)

        pygame.draw.rect(win, RED, restart_button, border_radius=5)
        restart_text = font.render('Restart', True, WHITE)
        win.blit(restart_text, (restart_button.centerx - restart_text.get_width() // 2,
                                restart_button.centery - restart_text.get_height() // 2))

        pygame.draw.rect(win, BLUE, suggest_button, border_radius=5)
        suggest_text = font.render('Suggest Move', True, WHITE)
        win.blit(suggest_text, (suggest_button.centerx - suggest_text.get_width() // 2,
                                suggest_button.centery - suggest_text.get_height() // 2))

        pygame.draw.rect(win, GREEN, dashboard_button, border_radius=5)
        dashboard_text = font.render('Move to Dashboard', True, WHITE)
        win.blit(dashboard_text, (dashboard_button.centerx - dashboard_text.get_width() // 2,
                                  dashboard_button.centery - dashboard_text.get_height() // 2))

        pygame.display.update()
if __name__ == "__main__":
    run()

# pygame.quit()