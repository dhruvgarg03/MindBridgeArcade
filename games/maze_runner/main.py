import tkinter as tk
from tkinter import messagebox
import os
import random

CELL_SIZE = 50

class MazeRunner:

    def go_to_dashboard(self):
        import subprocess
        import sys
        python_exe = sys.executable
        subprocess.Popen([python_exe, os.path.abspath("main.py")])
        self.root.destroy()

    def __init__(self, root):
        self.root = root
        self.root.title("Maze Runner")

        window_width = 800
        window_height = 600
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_pos = int((screen_width - window_width) / 2)
        y_pos = int((screen_height - window_height) / 2)
        self.root.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")
        self.root.resizable(False, False)

        self.root.configure(bg="#1e1e2f")  # Dark background

        self.score = 0
        self.level_files = [f"levels/level{i}.txt" for i in range(1, 9)]
        self.level_index = 0

        # Title label
        self.title_label = tk.Label(root, text="", bg="#1e1e2f")  # Empty label for padding
        self.title_label.pack(pady=7)

        # Frame for game area
        self.canvas_frame = tk.Frame(root, bg="#1e1e2f")
        self.canvas_frame.pack()

        self.canvas = tk.Canvas(self.canvas_frame, width=500, height=500, bg="white", highlightthickness=2, highlightbackground="#444")
        self.canvas.pack()

        # Bottom Controls Frame
        self.bottom_frame = tk.Frame(root, bg="#1e1e2f")
        self.bottom_frame.pack(pady=15)

        # Common button style
        btn_style = {"font": ("Helvetica", 12), "bg": "#4a90e2", "fg": "white", "activebackground": "#357ABD",
                     "activeforeground": "white", "relief": "flat", "bd": 0, "padx": 10, "pady": 5}

        self.dashboard_btn = tk.Button(self.bottom_frame, text="Move To Dashboard", command=self.go_to_dashboard, **btn_style)
        self.dashboard_btn.pack(side="left", padx=10)

        self.restart_btn = tk.Button(self.bottom_frame, text="Restart", command=self.restart_game, **btn_style)
        self.restart_btn.pack(side="left", padx=10)

        self.suggest_btn = tk.Button(self.bottom_frame, text="Suggest Move", command=self.suggest_move, **btn_style)
        self.suggest_btn.pack(side="left", padx=10)

        self.score_label = tk.Label(self.bottom_frame, text="Score: 0", font=("Helvetica", 12, "bold"),
                                    fg="#ffffff", bg="#1e1e2f")
        self.score_label.pack(side="left", padx=20)

        self.load_level()
        self.root.bind("<Key>", self.move_player)

    def load_level(self):
        self.canvas.delete("all")
        self.maze = []
        with open(self.level_files[self.level_index]) as f:
            for line in f:
                self.maze.append(list(line.strip()))

        self.rows = len(self.maze)
        self.cols = len(self.maze[0])

        self.start_x, self.start_y = 1, 1
        self.end_x, self.end_y = self.cols - 2, self.rows - 2
        self.player_x, self.player_y = self.start_x, self.start_y

        self.draw_maze()

    def draw_maze(self):
        for y in range(self.rows):
            for x in range(self.cols):
                color = "white"
                if self.maze[y][x] == '1':
                    color = "#2c3e50"  # Dark wall color
                elif (x, y) == (self.start_x, self.start_y):
                    color = "#27ae60"  # Start: green
                elif (x, y) == (self.end_x, self.end_y):
                    color = "#e74c3c"  # End: red

                self.canvas.create_rectangle(
                    x * CELL_SIZE, y * CELL_SIZE, (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE,
                    fill=color, outline="gray"
                )

        self.player = self.canvas.create_oval(
            self.player_x * CELL_SIZE + 5, self.player_y * CELL_SIZE + 5,
            (self.player_x + 1) * CELL_SIZE - 5, (self.player_y + 1) * CELL_SIZE - 5,
            fill="#3498db"  # Blue player
        )

    def move_player(self, event):
        dx, dy = 0, 0
        if event.keysym == "Up":
            dy = -1
        elif event.keysym == "Down":
            dy = 1
        elif event.keysym == "Left":
            dx = -1
        elif event.keysym == "Right":
            dx = 1

        new_x = self.player_x + dx
        new_y = self.player_y + dy

        if self.maze[new_y][new_x] != '1':
            self.player_x = new_x
            self.player_y = new_y
            self.score += 1
            self.update_display()

            if (self.player_x, self.player_y) == (self.end_x, self.end_y):
                self.score += 50
                messagebox.showinfo("Level Complete!", f"You completed the level with score {self.score}!")
                self.next_level()

    def update_display(self):
        self.canvas.delete("suggestion")
        self.canvas.coords(self.player,
                           self.player_x * CELL_SIZE + 5, self.player_y * CELL_SIZE + 5,
                           (self.player_x + 1) * CELL_SIZE - 5, (self.player_y + 1) * CELL_SIZE - 5)
        self.score_label.config(text=f"Score: {self.score}")

    def restart_game(self):
        self.score = 0
        self.load_level()
        self.update_display()

    def next_level(self):
        if self.level_index == len(self.level_files) - 1:
            messagebox.showinfo("You Win!", f"You completed all levels with a final score of {self.score}!")
            self.root.destroy()
        else:
            self.level_index += 1
            self.load_level()
            self.update_display()

    def get_next_best_move(self):
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        best_move = None
        min_distance = float("inf")

        for dx, dy in directions:
            nx, ny = self.player_x + dx, self.player_y + dy
            if 0 <= ny < self.rows and 0 <= nx < self.cols and self.maze[ny][nx] != '1':
                distance = abs(self.end_x - nx) + abs(self.end_y - ny)
                if distance < min_distance:
                    min_distance = distance
                    best_move = (nx, ny)

        return best_move

    def suggest_move(self):
        move_file = "current_state.txt"
        with open(move_file, "w") as f:
            f.write(f"Level: {self.level_index + 1}\n")
            f.write(f"Position: ({self.player_x}, {self.player_y})\n")
            f.write(f"Score: {self.score}\n")

        suggested = self.get_next_best_move()
        if suggested:
            x, y = suggested
            self.canvas.create_rectangle(
                x * CELL_SIZE, y * CELL_SIZE, (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE,
                fill="#f1c40f", outline="#f39c12", width=3, tags="suggestion"
            )


def create_levels():
 
    # Updated and more difficult level definitions
    levels = {
        "level1.txt": [
            "111111111",
            "100000001",
            "101111101",
            "101000101",
            "101011101",
            "100010001",
            "111111111"
        ],
        "level2.txt": [
            "111111111",
            "100000001",
            "101111101",
            "100100001",
            "111101111",
            "100000001",
            "111111111"
        ],
        "level3.txt": [
            "111111111",
            "100010001",
            "101110101",
            "100000001",
            "101111101",
            "100000001",
            "111111111"
        ],
        "level4.txt": [
            "111111111",
            "100000001",
            "101111101",
            "101000101",
            "101110101",
            "100000001",
            "111111111"
        ],
        "level5.txt": [
            "1111111111",
            "1000000001",
            "1011111101",
            "1000000101",
            "1111110101",
            "1000000001",
            "1111111111"
        ],
        "level6.txt": [
            "1111111111",
            "1000100001",
            "1010101111",
            "1010000001",
            "1110111101",
            "1000000001",
            "1111111111"
        ],
        "level7.txt": [
            "1111111111",
            "1000000001",
            "1110111101",
            "1000100001",
            "1011111011",
            "1000000001",
            "1111111111"
        ],
        "level8.txt": [
            "1111111111",
            "1000001001",
            "1011101111",
            "1000100001",
            "1111111101",
            "1000000001",
            "1111111111"
        ]
    }

    # Create levels directory if it doesn't exist
    os.makedirs("levels", exist_ok=True)

    # Write each level to its corresponding file
    for filename, lines in levels.items():
        with open(f"levels/{filename}", "w") as f:
            f.write("\n".join(lines))

def run():
    create_levels()
    root = tk.Tk()
    MazeRunner(root)
    root.mainloop()

