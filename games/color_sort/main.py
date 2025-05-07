# import critical modules - random for board generation, copy for being able to restart, pygame for framework
import copy
import random
import pygame
import os
from dashboard import dashboard_loop
from ai.aiCall import ai_call
from tooltip.tooltip import Tooltip
import json
# initialize pygame
pygame.init()

# initialize game variables
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('Water Sort PyGame')
font = pygame.font.Font('freesansbold.ttf', 24)
tooltip = Tooltip()

fps = 60
timer = pygame.time.Clock()
RED = 0
ORANGE = 1
LIGHT_BLUE = 2
DARK_BLUE = 3
DARK_GREEN = 4
PINK = 5
PURPLE = 6
DARK_GRAY = 7
BROWN = 8
LIGHT_GREEN = 9
YELLOW = 10
WHITE = 11
color_choices = ['red', 'orange', 'light blue', 'dark blue', 'dark green', 'pink', 'purple', 'dark gray',
                 'brown', 'light green', 'yellow', 'white']
tube_colors = []
initial_colors = []
# 10 - 14 tubes, always start with two empty
tubes = 10
new_game = True
selected = False
tube_rects = []
select_rect = 100
win = False
moves=0

# select a number of tubes and pick random colors upon new game setup
def generate_start():
    num_colors = 4  # or however many colors you want to use (max 11 for now)
    num_tubes = num_colors + 2
    tube_colorss = [[] for _ in range(num_tubes)]

    # Create a pool with 4 entries of each color (fixed indices from 0 to num_colors-1)
    color_pool = []
    for color_index in range(num_colors):
        color_pool.extend([color_index] * 4)  # 4 of each color

    random.shuffle(color_pool)  # Shuffle the pool, not the color index mapping

    # Fill the tubes (except last two empty tubes)
    tube_index = 0
    while color_pool:
        if len(tube_colorss[tube_index]) < 4:
            tube_colorss[tube_index].append(color_pool.pop())
        tube_index = (tube_index + 1) % (num_tubes - 2)  # Only fill first (num_tubes - 2) tubes
    # for tube in tube_colorss:
    #     tube.reverse()
    return tube_colorss

# draw all tubes and colors on screen, as well as indicating what tube was selected
def draw_tubes(tubes_num, tube_cols):
    tube_boxes = []

    if tubes_num % 2 == 0:
        tubes_per_row = tubes_num // 2
        offset = False
    else:
        tubes_per_row = tubes_num // 2 + 1
        offset = True

    spacing = WIDTH / tubes_per_row

    # Draw top row
    for i in range(tubes_per_row):
        for j in range(len(tube_cols[i])):
            pygame.draw.rect(
                screen,
                color_choices[tube_cols[i][j]],
                [5 + spacing * i, 200 - (50 * j), 65, 50],
                0,
                3
            )
        box = pygame.draw.rect(screen, 'blue', [5 + spacing * i, 50, 65, 200], 5, 5)
        if select_rect == i:
            pygame.draw.rect(screen, 'green', [5 + spacing * i, 50, 65, 200], 3, 5)
        tube_boxes.append(box)

    # Draw bottom row
    if offset:
        for i in range(tubes_per_row - 1):
            if i + tubes_per_row < len(tube_cols):
                for j in range(len(tube_cols[i + tubes_per_row])):
                    pygame.draw.rect(
                        screen,
                        color_choices[tube_cols[i + tubes_per_row][j]],
                        [(spacing * 0.5) + 5 + spacing * i, 450 - (50 * j), 65, 50],
                        0,
                        3
                    )
                box = pygame.draw.rect(
                    screen,
                    'blue',
                    [(spacing * 0.5) + 5 + spacing * i, 300, 65, 200],
                    5,
                    5
                )
                if select_rect == i + tubes_per_row:
                    pygame.draw.rect(
                        screen,
                        'green',
                        [(spacing * 0.5) + 5 + spacing * i, 300, 65, 200],
                        3,
                        5
                    )
                tube_boxes.append(box)
    else:
        for i in range(tubes_per_row):
            if i + tubes_per_row < len(tube_cols):
                for j in range(len(tube_cols[i + tubes_per_row])):
                    pygame.draw.rect(
                        screen,
                        color_choices[tube_cols[i + tubes_per_row][j]],
                        [5 + spacing * i, 450 - (50 * j), 65, 50],
                        0,
                        3
                    )
                box = pygame.draw.rect(screen, 'blue', [5 + spacing * i, 300, 65, 200], 5, 5)
                if select_rect == i + tubes_per_row:
                    pygame.draw.rect(screen, 'green', [5 + spacing * i, 300, 65, 200], 3, 5)
                tube_boxes.append(box)

    return tube_boxes



# determine the top color of the selected tube and destination tube,
# as well as how long a chain of that color to move
def calc_move(colors, selected_rect, destination):
    chain = True
    color_on_top = 100
    length = 1
    color_to_move = 100
    if len(colors[selected_rect]) > 0:
        color_to_move = colors[selected_rect][-1]
        for i in range(1, len(colors[selected_rect])):
            if chain:
                if colors[selected_rect][-1 - i] == color_to_move:
                    length += 1
                else:
                    chain = False
    if 4 > len(colors[destination]):
        if len(colors[destination]) == 0:
            color_on_top = color_to_move
        else:
            color_on_top = colors[destination][-1]
    if color_on_top == color_to_move:
        for i in range(length):
            if len(colors[destination]) < 4:
                if len(colors[selected_rect]) > 0:
                    colors[destination].append(color_on_top)
                    colors[selected_rect].pop(-1)
    print(colors, length)
    previous_tubes_colors = copy.deepcopy(colors)
    return colors


# check if every tube with colors is 4 long and all the same color. That's how we win
def check_victory(colors):
    won = True
    for i in range(len(colors)):
        if len(colors[i]) > 0:
            if len(colors[i]) != 4:
                won = False
            else:
                main_color = colors[i][-1]
                for j in range(len(colors[i])):
                    if colors[i][j] != main_color:
                        won = False
    return won


# main game loop
import os

def save_current_state(tube_colors, moves):
    file_path = os.path.abspath("current_state.txt")
    with open(file_path, "w") as f:
        f.write(f"Moves: {moves}\n")
        for tube in tube_colors:
            f.write(",".join(str(color) for color in tube) + "\n")
    print(f"State saved at: {file_path}")

def run():
    global tube_colors, initial_colors, new_game, selected, select_rect, win, moves, previous_tubes_colors
    running = True
    while running:
        screen.fill((30, 30, 30))
        timer.tick(fps)
        
        # Button dimensions
        button_width, button_height = 210, 50
        button_padding = 20
        bottom_margin = 20
        button_y = HEIGHT - button_height - bottom_margin
    
        # Suggest Move button
        suggest_button_rect = pygame.Rect(10, button_y, button_width, button_height)
        pygame.draw.rect(screen, (0, 170, 255), suggest_button_rect, border_radius=10)
        suggest_text = font.render("Suggest Move", True, (255, 255, 255))
        screen.blit(suggest_text, (suggest_button_rect.x + 25, suggest_button_rect.y + 12))
    
        # Back to Dashboard button
        dashboard_button_rect = pygame.Rect(
            suggest_button_rect.right + button_padding, button_y, button_width+40, button_height)
        pygame.draw.rect(screen, (255, 100, 100), dashboard_button_rect, border_radius=10)
        dashboard_text = font.render("Back to Dashboard", True, (255, 255, 255))
        screen.blit(dashboard_text, (dashboard_button_rect.x + 10, dashboard_button_rect.y + 12))
    
        # Restart button above the other two
        restart_button_rect = pygame.Rect(
            dashboard_button_rect.right + button_padding, button_y, button_width, button_height)
        pygame.draw.rect(screen, (100, 200, 100), restart_button_rect, border_radius=10)
        restart_text_btn = font.render("Restart", True, (255, 255, 255))
        screen.blit(restart_text_btn, (restart_button_rect.x + 55, restart_button_rect.y + 12))
    
        # generate game board on new game, make a copy of the colors in case of restart
        if new_game:
            tube_colors = generate_start()
            tube = len(tube_colors)
            initial_colors = copy.deepcopy(tube_colors)
            new_game = False
        # draw tubes every cycle
        else:
            tube_rects = draw_tubes(tubes, tube_colors)
        # check for victory every cycle
        win = check_victory(tube_colors)
        # event handling - Quit button exits, clicks select tubes, enter and space for restart and new board
        for event in pygame.event.get():
            tooltip.handle_event(event)
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    tube_colors = copy.deepcopy(initial_colors)
                elif event.key == pygame.K_RETURN:
                    new_game = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if suggest_button_rect.collidepoint(event.pos):
                    # save_current_state(tube_colors, moves)
                    current_state_str = json.dumps(previous_tubes_colors)
                    current_state_str = [list(reversed(tube)) for tube in tubes]
                    prompt = (
        "You are a color sort game expert. Analyze this TOP-FIRST tube state and suggest the optimal move.\n"
        "Rules:\n"
        "1. Tubes are lists where FIRST element = TOP color\n"
        "2. Moves must either:\n"
        "   a) Pour into an EMPTY tube, or\n"
        "   b) Match the TOP color of destination tube\n"
        "3. Strategic priorities:\n"
        "   - Create empty tubes for critical moves\n"
        "   - Group same colors together\n"
        "   - Avoid blocking colors under dissimilar tops\n\n"
        f"Current state (top-first):\n{current_state_str}\n"
        "Response format:\n"
        "Move [COLOR] from Tube [X] to Tube [Y]: [1-sentence strategic reason]\n"
        "Example:\n"
        "Move 2 from Tube 0 to Tube 3: This groups purple colors while freeing Tube 0 for future organization."
    )
    
                 # Call AI
                    ai_response = ai_call(current_state_str, prompt)
    
                    tooltip.show(ai_response)
    
                    print("AI Suggestion:", ai_response)
                    print("Suggest Move button clicked : ", previous_tubes_colors)
                # elif not selected:
                #     for item in range(len(tube_rects)):
                #         if tube_rects[item].collidepoint(event.pos):
                #             selected = True
                #             select_rect = item
                elif restart_button_rect.collidepoint(event.pos):
                    tube_colors = copy.deepcopy(initial_colors)
                    moves = 0  # reset move counter on restart
                    selected = False
                    select_rect = 100
                    previous_tubes_colors = copy.deepcopy(tube_colors)
                elif dashboard_button_rect.collidepoint(event.pos):
                    running = False  # Exit the game loop to go back to the dashboard
                    # dashboard_loop()
                    
                elif not selected:
                    for item in range(len(tube_rects)):
                        if tube_rects[item].collidepoint(event.pos):
                            selected = True
                            select_rect = item
                else:
                    for item in range(len(tube_rects)):
                        if tube_rects[item].collidepoint(event.pos):
                            dest_rect = item
                            tube_colors = calc_move(tube_colors, select_rect, dest_rect)
                            moves += 1  # increment move count here!
                            selected = False
                            select_rect = 100
                            previous_tubes_colors = copy.deepcopy(tube_colors)
    
        # draw 'victory' text when winning in middle, always show restart and new board text at top
        if win:
            victory_text = font.render('You Won! Press Enter for a new board!', True, 'white')
            screen.blit(victory_text, (30, 265))
        restart_text = font.render('Stuck? Space-Restart, Enter-New Board!', True, 'white')
        moves_text = font.render(f'Moves: {moves}', True, 'white')
        screen.blit(moves_text, (10, 40))
        # Draw 'Suggest Move' button at bottom
    
        screen.blit(restart_text, (10, 10))
    
        tooltip.draw(screen)
    
        # display all drawn items on screen, exit pygame if running == False
        pygame.display.flip()
