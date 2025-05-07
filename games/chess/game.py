import os
import pygame
from pygame.locals import *
from games.chess.piece import Piece
from games.chess.chess import Chess
from games.chess.utils import Utils
from ai.aiCall import ai_call
from tooltip.tooltip import Tooltip
import json
import copy
from dashboard import dashboard_loop
SUGGEST_BUTTON_RECT = pygame.Rect(660, 100, 140, 40)  # x, y, width, height
DASHBOARD_BUTTON_RECT = pygame.Rect(660, 160, 180, 50)
tooltip = Tooltip()
# explanation = ""
class Game:
    def __init__(self):
        # Add in __init__ of ChessAI class
        # Add these counters as instance variables in __init__:
        self.highlighted_move = None
        self.highlighted_move_time = None  # Add this line


        self.piece_values = {
            'pawn': 1,
            'knight': 10,
            'bishop': 13.5,
            'rook': 40,
            'queen': 50,
            'king': 100
        }

        self.pst = {
            'pawn': [[0, 0, 0, 0, 0, 0, 0, 0],
                     [5, 5, 5, -5, -5, 5, 5, 5],
                     [1, 1, 2, 3, 3, 2, 1, 1],
                     [0.5, 0.5, 1, 2.5, 2.5, 1, 0.5, 0.5],
                     [0, 0, 0, 2, 2, 0, 0, 0],
                     [0.5, -0.5, -1, 0, 0, -1, -0.5, 0.5],
                     [0.5, 1, 1, -2, -2, 1, 1, 0.5],
                     [0, 0, 0, 0, 0, 0, 0, 0]],
            'knight': [[-5, -4, -3, -3, -3, -3, -4, -5],
                       [-4, -2, 0, 0, 0, 0, -2, -4],
                       [-3, 0, 1, 1.5, 1.5, 1, 0, -3],
                       [-3, 0.5, 1.5, 2, 2, 1.5, 0.5, -3],
                       [-3, 0, 1.5, 2, 2, 1.5, 0, -3],
                       [-3, 0.5, 1, 1.5, 1.5, 1, 0.5, -3],
                       [-4, -2, 0, 0.5, 0.5, 0, -2, -4],
                       [-5, -4, -3, -3, -3, -3, -4, -5]],
            'bishop': [[-2, -1, -1, -1, -1, -1, -1, -2],
                       [-1, 0, 0, 0, 0, 0, 0, -1],
                       [-1, 0, 0.5, 1, 1, 0.5, 0, -1],
                       [-1, 0.5, 0.5, 1, 1, 0.5, 0.5, -1],
                       [-1, 0, 1, 1, 1, 1, 0, -1],
                       [-1, 1, 1, 1, 1, 1, 1, -1],
                       [-1, 0.5, 0, 0, 0, 0, 0.5, -1],
                       [-2, -1, -1, -1, -1, -1, -1, -2]],
            'rook': [[0, 0, 0, 0, 0, 0, 0, 0],
                     [0.5, 1, 1, 1, 1, 1, 1, 0.5],
                     [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
                     [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
                     [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
                     [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
                     [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
                     [0, 0, 0, 0.5, 0.5, 0, 0, 0]],
            'queen': [[-2, -1, -1, -0.5, -0.5, -1, -1, -2],
                      [-1, 0, 0, 0, 0, 0, 0, -1],
                      [-1, 0, 0.5, 0.5, 0.5, 0.5, 0, -1],
                      [-0.5, 0, 0.5, 0.5, 0.5, 0.5, 0, -0.5],
                      [0, 0, 0.5, 0.5, 0.5, 0.5, 0, -0.5],
                      [-1, 0.5, 0.5, 0.5, 0.5, 0.5, 0, -1],
                      [-1, 0, 0.5, 0, 0, 0, 0, -1],
                      [-2, -1, -1, -0.5, -0.5, -1, -1, -2]],
            'king': [[-3, -4, -4, -5, -5, -4, -4, -3],
                     [-3, -4, -4, -5, -5, -4, -4, -3],
                     [-3, -4, -4, -5, -5, -4, -4, -3],
                     [-3, -4, -4, -5, -5, -4, -4, -3],
                     [-2, -3, -3, -4, -4, -3, -3, -2],
                     [-1, -2, -2, -2, -2, -2, -2, -1],
                     [2, 2, 0, 0, 0, 0, 2, 2],
                     [2, 3, 1, 0, 0, 1, 3, 2]]
        }
        self.piece_location = {}
        for file in 'abcdefgh':
            self.piece_location[file] = {}
            for rank in range(1, 9):
                self.piece_location[file][rank] = []
        # Set up starting pieces
        pieces = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook']
        for i, file in enumerate('abcdefgh'):
            self.piece_location[file][1] = [f'white_{pieces[i]}']
            self.piece_location[file][2] = ['white_pawn']
            self.piece_location[file][7] = ['black_pawn']
            self.piece_location[file][8] = [f'black_{pieces[i]}']

        # screen dimensions
        screen_width = 850
        screen_height = 670
        # flag to know if game menu has been showed
        self.menu_showed = False
        # flag to set game loop
        self.running = True
        # base folder for program resources
        self.resources = "res"
 
        # initialize game window
        pygame.display.init()
        # initialize font for text
        pygame.font.init()

        # create game window
        self.screen = pygame.display.set_mode([screen_width, screen_height])

        # title of window
        window_title = "Chess"
        # set window caption
        pygame.display.set_caption(window_title)
        self.board = self.create_starting_board()
        # print(self.board_to_fen(self.board))
        # get location of game icon
        icon_src = os.path.join(self.resources, "chess_icon.png")
        print(icon_src)
        # load game icon
        icon = pygame.image.load(icon_src)
        # set game icon
        pygame.display.set_icon(icon)
        # update display
        pygame.display.flip()
        # set game clock
        self.clock = pygame.time.Clock()

    def create_starting_board(self):
    # Returns a standard 8x8 chess board setup (rank 8 at top, rank 1 at bottom)
        return [
            ["black_rook", "black_knight", "black_bishop", "black_queen", "black_king", "black_bishop", "black_knight", "black_rook"],  # rank 8
            ["black_pawn"] * 8,   # rank 7
            [None] * 8,           # rank 6
            [None] * 8,           # rank 5
            [None] * 8,           # rank 4
            [None] * 8,           # rank 3
            ["white_pawn"] * 8,   # rank 2
            ["white_rook", "white_knight", "white_bishop", "white_queen", "white_king", "white_bishop", "white_knight", "white_rook"]  # rank 1
        ]

    def piece_square_bonus(self, ptype, color, y, x):
        table = self.pst.get(ptype)
        if table:
            return table[y][x] if color == 'white' else table[7 - y][x]
        return 0
    def evaluate_board(self, board):
        score = 0
        for y, row in enumerate(board):
            for x, piece in enumerate(row):
                if piece:
                    color, ptype = piece.split('_')
                    value = self.piece_values.get(ptype, 0)
                    bonus = self.piece_square_bonus(ptype, color, y, x)
                    if color == 'white':
                        score += value + bonus
                    else:
                        score -= value + bonus

        # Mobility bonus
        white_moves = len(self.generate_legal_moves(board, 'white'))
        black_moves = len(self.generate_legal_moves(board, 'black'))
        mobility = 0.1 * (white_moves - black_moves)
        score += mobility

        return score

    def piece_location_to_board(self, piece_location):
        board = [[None for _ in range(8)] for _ in range(8)]
        for file_idx, file_char in enumerate('abcdefgh'):
            for rank in range(1, 9):
                pieces = piece_location[file_char].get(rank, [])
                piece = pieces[0] if pieces else None
                x = file_idx  # a=0, h=7
                y = 8 - rank  # rank 8 → y=0 (top row), rank 1 → y=7 (bottom row)
                board[y][x] = piece
        return board


    def generate_legal_moves(self,board, color):
        moves = []
        direction = -1 if color == 'white' else 1  # White moves up, black down

        for y in range(8):
            for x in range(8):
                piece = board[y][x]
                if piece and piece.startswith(color):
                    ptype = piece.split('_')[1]

                    # PAWN
                    if ptype == 'pawn':
                        ny = y + direction
                        # Move forward
                        if 0 <= ny < 8 and board[ny][x] is None:
                            moves.append(((x, y), (x, ny)))
                            # Double move on first move
                            if (color == 'white' and y == 6) or (color == 'black' and y == 1):
                                ny2 = y + 2 * direction
                                if board[ny2][x] is None:
                                    moves.append(((x, y), (x, ny2)))
                        # Captures
                        for dx in [-1, 1]:
                            nx = x + dx
                            if 0 <= nx < 8 and 0 <= ny < 8:
                                target = board[ny][nx]
                                if target and not target.startswith(color):
                                    moves.append(((x, y), (nx, ny)))

                    # KNIGHT
                    elif ptype == 'knight':
                        knight_moves = [
                            (x + 1, y + 2), (x + 2, y + 1), (x + 2, y - 1), (x + 1, y - 2),
                            (x - 1, y - 2), (x - 2, y - 1), (x - 2, y + 1), (x - 1, y + 2)
                        ]
                        for nx, ny in knight_moves:
                            if 0 <= nx < 8 and 0 <= ny < 8:
                                target = board[ny][nx]
                                if target is None or not target.startswith(color):
                                    moves.append(((x, y), (nx, ny)))

                    # BISHOP
                    elif ptype == 'bishop':
                        for dx, dy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
                            nx, ny = x + dx, y + dy
                            while 0 <= nx < 8 and 0 <= ny < 8:
                                target = board[ny][nx]
                                if target is None:
                                    moves.append(((x, y), (nx, ny)))
                                elif not target.startswith(color):
                                    moves.append(((x, y), (nx, ny)))
                                    break
                                else:
                                    break
                                nx += dx
                                ny += dy

                    # ROOK
                    elif ptype == 'rook':
                        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            nx, ny = x + dx, y + dy
                            while 0 <= nx < 8 and 0 <= ny < 8:
                                target = board[ny][nx]
                                if target is None:
                                    moves.append(((x, y), (nx, ny)))
                                elif not target.startswith(color):
                                    moves.append(((x, y), (nx, ny)))
                                    break
                                else:
                                    break
                                nx += dx
                                ny += dy

                    # QUEEN
                    elif ptype == 'queen':
                        for dx, dy in [(-1, -1), (1, -1), (1, 1), (-1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]:
                            nx, ny = x + dx, y + dy
                            while 0 <= nx < 8 and 0 <= ny < 8:
                                target = board[ny][nx]
                                if target is None:
                                    moves.append(((x, y), (nx, ny)))
                                elif not target.startswith(color):
                                    moves.append(((x, y), (nx, ny)))
                                    break
                                else:
                                    break
                                nx += dx
                                ny += dy

                    # KING
                    elif ptype == 'king':
                        for dx in [-1, 0, 1]:
                            for dy in [-1, 0, 1]:
                                if dx == 0 and dy == 0:
                                    continue
                                nx, ny = x + dx, y + dy
                                if 0 <= nx < 8 and 0 <= ny < 8:
                                    target = board[ny][nx]
                                    if target is None or not target.startswith(color):
                                        moves.append(((x, y), (nx, ny)))
        return moves

    def make_move(self,board, move):
        new_board = copy.deepcopy(board)
        (from_x, from_y), (to_x, to_y) = move
        new_board[to_y][to_x] = new_board[from_y][from_x]
        new_board[from_y][from_x] = None
        return new_board
    def get_piece_value(self, piece):
        if piece is None:
            return 0
        values = {
            'pawn': 1,
            'knight': 10,
            'bishop': 13.5,
            'rook': 40,
            'queen': 50,
            'king': 100
            # add your piece names as needed
        }
        piece_name = piece.lower()
        if '_' in piece_name:
            piece_name = piece_name.split('_')[1]
        return values.get(piece.lower(), 0)

    def move_heuristic(self, board, move, player):
        (from_row, from_col), (to_row, to_col) = move
        piece = board[from_row][from_col]
        target = board[to_row][to_col]

        # High score if capturing a piece
        capture_score = 0
        if target != '.':
            capture_score = self.get_piece_value(target) - self.get_piece_value(piece)

        # Slightly prefer central positions
        center_bonus = 3 if (3 <= to_row <= 4 and 3 <= to_col <= 4) else 0

        # Promotion detection (pawn reaches last rank)
        promotion_bonus = 9 if (piece is not None and piece.lower() == 'p' and (to_row == 0 or to_row == 7)) else 0


        return capture_score + center_bonus + promotion_bonus

    
    def minimax(self,board, depth, alpha, beta, maximizing, color):
        if depth == 0:
            return self.evaluate_board(board), None

        best_move = None
        moves = self.generate_legal_moves(board, color)
        moves.sort(key=lambda m: self.move_heuristic(board, m, color), reverse=True)
        if not moves:
            return self.evaluate_board(board), None

        if maximizing:
            max_eval = float('-inf')
            for move in moves:
                new_board = self.make_move(board, move)
                eval_score, _ = self.minimax(new_board, depth - 1, alpha, beta, False,
                                        'black' if color == 'white' else 'white')
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in moves:
                new_board = self.make_move(board, move)
                eval_score, _ = self.minimax(new_board, depth - 1, alpha, beta, True,
                                        'black' if color == 'white' else 'white')
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval, best_move
    def board_to_fen(self, board, active_color, castling='KQkq', en_passant='-', halfmove='0', fullmove='1'):
            piece_map = {
                'white_pawn': 'P', 'black_pawn': 'p',
                'white_knight': 'N', 'black_knight': 'n',
                'white_bishop': 'B', 'black_bishop': 'b',
                'white_rook': 'R', 'black_rook': 'r',
                'white_queen': 'Q', 'black_queen': 'q',
                'white_king': 'K', 'black_king': 'k'
            }

            fen_rows = []
            for row in board:
                fen_row = []
                empty = 0
                for piece in row:
                    if piece:
                        if empty:
                            fen_row.append(str(empty))
                            empty = 0
                        fen_row.append(piece_map[piece])
                    else:
                        empty += 1
                if empty:
                    fen_row.append(str(empty))
                fen_rows.append(''.join(fen_row))

            return f"{'/'.join(fen_rows)} + f' {active_color} {castling} {en_passant} {halfmove} {fullmove}"
    def move_to_notation(self, move):
        if not move:
            return ""
        (from_x, from_y), (to_x, to_y) = move
        files = 'abcdefgh'
        return f"{files[from_x]}{8-from_y}{files[to_x]}{8-to_y}"


    def save_board_to_file(self,board, filename="board_state.txt"):
        with open(filename, "w") as f:
            for row in board:
                f.write(' '.join([piece if piece else '.' for piece in row]) + "\n")

    def suggest_move(self,board, turn):
        color = 'white' if turn['white'] else 'black'
        _, move = self.minimax(board, depth=5, alpha=float('-inf'), beta=float('inf'), maximizing=True, color=color)
        board_str = "\n".join([" ".join([piece[0] if piece else "." for piece in row]) 
                          for row in board])
    
            # Craft prompt for explanation
        prompt = f"""You are a chess coach. Briefly explain (1 sentence) why this move is strong:
        Board (uppercase=white, lowercase=black):
        {board_str}
        Suggested move: {self.move_to_notation(move)}
        Reason:"""

            # Get AI explanation
        explanation = ai_call(board_str, prompt)

        return move, explanation
        
    def start_game(self):
        """Function containing main game loop""" 
        # chess board offset
        self.board_offset_x = 0
        self.board_offset_y = 35
        self.board_dimensions = (self.board_offset_x, self.board_offset_y)
        
        # get location of chess board image
        board_src = os.path.join(self.resources, "board.png")
        # load the chess board image
        self.board_img = pygame.image.load(board_src).convert()

        # get the width of a chess board square
        square_length = self.board_img.get_rect().width // 8
        print(square_length)

        # initialize list that stores all places to put chess pieces on the board
        self.board_locations = []

        # calculate coordinates of the each square on the board
        for x in range(0, 8):
            self.board_locations.append([])
            for y in range(0, 8):
                self.board_locations[x].append([self.board_offset_x+(x*square_length), 
                                                self.board_offset_y+(y*square_length)])

        # get location of image containing the chess pieces
        pieces_src = os.path.join(self.resources, "pieces.png")
        # create class object that handles the gameplay logic
        self.chess = Chess(self.screen, pieces_src, self.board_locations, square_length)

        # game loop
        while self.running:
            self.clock.tick(5)
            # poll events
            for event in pygame.event.get():
                tooltip.handle_event(event)
                # get keys pressed
                key_pressed = pygame.key.get_pressed()
                # check if the game has been closed by the user
                if event.type == pygame.QUIT or key_pressed[K_ESCAPE]:
                    # set flag to break out of the game loop
                    self.running = False
                elif key_pressed[K_SPACE]:
                    self.chess.reset()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if SUGGEST_BUTTON_RECT.collidepoint(event.pos):
                        board_2d = self.piece_location_to_board(self.chess.piece_location)
                        self.save_board_to_file(board_2d)  # Save the board state to a file
                        move,explanation = self.suggest_move(board_2d, self.chess.turn)
                        if move:
                            self.highlighted_move = move
                            self.highlighted_move_time = pygame.time.get_ticks()
                            print(f"Suggested move: {self.move_to_notation(move)}")
                            tooltip.show(explanation)
                        # print("Current board:")
                        # for row in board_2d:
                        #     print(row)

                        # active_color = 'w' if self.chess.turn['white'] else 'b'
                        # fen = self.board_to_fen(board_2d, active_color=active_color)  # Use FEN conversion
                        # prompt = (
                        #         "You are an expert chess player. Given the current chess board state in FEN notation, "
                        #         "suggest the single best next move in algebraic notation for the current player. "
                        #         "Briefly explain why this move is strong."
                        #     )
                        # print("Turn state:", self.chess.turn)
                        # print("FEN:", fen)
                        # ai_response = ai_call(fen, prompt)  # Pass FEN instead of color sort state
                        # tooltip.show(ai_response)
                        # print("AI Suggestion:", ai_response)

                    if DASHBOARD_BUTTON_RECT.collidepoint(event.pos):
                        self.run = False
                        dashboard_loop()
            winner = self.chess.winner

            if self.menu_showed == False:
                self.menu()
            elif len(winner) > 0:
                self.declare_winner(winner)
            else:
                self.game()
                self.draw_suggest_button()
                self.draw_dashboard_button()
                if hasattr(self, 'highlighted_move') and self.highlighted_move:
                    self.draw_highlighted_move(self.screen, self.highlighted_move)

            # for testing mechanics of the game
            #self.game()
            #self.declare_winner(winner)
            tooltip.draw(self.screen)
            HIGHLIGHT_DURATION = 2000  # milliseconds (2 seconds)
            if self.highlighted_move is not None and self.highlighted_move_time is not None:
                now = pygame.time.get_ticks()
                if now - self.highlighted_move_time > HIGHLIGHT_DURATION:
                    self.highlighted_move = None
                    self.highlighted_move_time = None
            # update display
            pygame.display.flip()
            # update events
            pygame.event.pump()

        # call method to stop pygame
        pygame.quit()
    

    def menu(self):
        """method to show game menu"""
        # background color
        bg_color = (255, 255, 255)
        # set background color
        self.screen.fill(bg_color)
        # black color
        black_color = (0, 0, 0)
        # coordinates for "Play" button
        start_btn = pygame.Rect(360, 300, 100, 50)
        # show play button
        pygame.draw.rect(self.screen, black_color, start_btn)

        # white color
        white_color = (255, 255, 255)
        # create fonts for texts
        big_font = pygame.font.SysFont("comicsansms", 50)
        small_font = pygame.font.SysFont("comicsansms", 20)
        # create text to be shown on the game menu
        welcome_text = big_font.render("Chess", False, black_color)
        created_by = small_font.render(" ", True, black_color)
        start_btn_label = small_font.render("Play", True, white_color)
        
        # show welcome text
        self.screen.blit(welcome_text, 
                      ((self.screen.get_width() - welcome_text.get_width()) // 2, 
                      150))
        # show credit text
        self.screen.blit(created_by, 
                      ((self.screen.get_width() - created_by.get_width()) // 2, 
                      self.screen.get_height() - created_by.get_height() - 100))
        # show text on the Play button
        self.screen.blit(start_btn_label, 
                      ((start_btn.x + (start_btn.width - start_btn_label.get_width()) // 2, 
                      start_btn.y + (start_btn.height - start_btn_label.get_height()) // 2)))

        # get pressed keys
        key_pressed = pygame.key.get_pressed()
        # 
        util = Utils()

        # check if left mouse button was clicked
        if util.left_click_event():
            # call function to get mouse event
            mouse_coords = util.get_mouse_event()

            # check if "Play" button was clicked
            if start_btn.collidepoint(mouse_coords[0], mouse_coords[1]):
                # change button behavior as it is hovered
                pygame.draw.rect(self.screen, white_color, start_btn, 3)
                
                # change menu flag
                self.menu_showed = True
            # check if enter or return key was pressed
            elif key_pressed[K_RETURN]:
                self.menu_showed = True


    def game(self):
        # background color
        color = (0,0,0)
        # set backgound color
        self.screen.fill(color)
        
        # show the chess board
        self.screen.blit(self.board_img, self.board_dimensions)

        # call self.chess. something
        self.chess.play_turn()
        # draw pieces on the chess board
        self.chess.draw_pieces()
    
    def draw_suggest_button(self):
        pygame.draw.rect(self.screen, (50, 50, 50), SUGGEST_BUTTON_RECT) # dark gray
        font = pygame.font.SysFont("comicsansms", 20)
        text = font.render("Suggest Move", True, (255, 255, 255))
        text_rect = text.get_rect(center=SUGGEST_BUTTON_RECT.center)
        self.screen.blit(text, text_rect)
    
    def draw_dashboard_button(self):
        pygame.draw.rect(self.screen, (50, 50, 50), DASHBOARD_BUTTON_RECT)  # dark gray
        font = pygame.font.SysFont("comicsansms", 20)
        text = font.render("Move to Dashboard", True, (255, 255, 255))
        text_rect = text.get_rect(center=DASHBOARD_BUTTON_RECT.center)
        self.screen.blit(text, text_rect)

    def declare_winner(self, winner):
        # background color
        bg_color = (255, 255, 255)
        # set background color
        self.screen.fill(bg_color)
        # black color
        black_color = (0, 0, 0)
        # coordinates for play again button
        reset_btn = pygame.Rect(360, 300, 140, 50)
        # show reset button
        pygame.draw.rect(self.screen, black_color, reset_btn)

        # white color
        white_color = (255, 255, 255)
        # create fonts for texts
        big_font = pygame.font.SysFont("comicsansms", 50)
        small_font = pygame.font.SysFont("comicsansms", 20)

        # text to show winner
        text = winner + " wins!" 
        winner_text = big_font.render(text, False, black_color)

        # create text to be shown on the reset button
        reset_label = "Play Again"
        reset_btn_label = small_font.render(reset_label, True, white_color)

        # show winner text
        self.screen.blit(winner_text, 
                      ((self.screen.get_width() - winner_text.get_width()) // 2, 
                      150))
        
        # show text on the reset button
        self.screen.blit(reset_btn_label, 
                      ((reset_btn.x + (reset_btn.width - reset_btn_label.get_width()) // 2, 
                      reset_btn.y + (reset_btn.height - reset_btn_label.get_height()) // 2)))

        # get pressed keys
        key_pressed = pygame.key.get_pressed()
        # 
        util = Utils()

        # check if left mouse button was clicked
        if util.left_click_event():
            # call function to get mouse event
            mouse_coords = util.get_mouse_event()

            # check if reset button was clicked
            if reset_btn.collidepoint(mouse_coords[0], mouse_coords[1]):
                # change button behavior as it is hovered
                pygame.draw.rect(self.screen, white_color, reset_btn, 3)
                
                # change menu flag
                self.menu_showed = False
            # check if enter or return key was pressed
            elif key_pressed[K_RETURN]:
                self.menu_showed = False
            # reset game
            self.chess.reset()
            # clear winner
            self.chess.winner = ""

    def draw_highlighted_move(self, screen, move):
        if move:
            (from_x, from_y), (to_x, to_y) = move
            square_size = 80  # Use your actual square size variable
            highlight_color = (0, 255, 0, 100)  # semi-transparent green
            s = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
            s.fill(highlight_color)
            # Add board offsets!
            screen.blit(s, (self.board_offset_x + from_x * square_size, self.board_offset_y + from_y * square_size))
            screen.blit(s, (self.board_offset_x + to_x * square_size, self.board_offset_y + to_y * square_size))

