import tkinter as tk
from tkinter import messagebox
import random
import os
from PIL import Image, ImageTk
from PIL import ImageFilter, ImageEnhance
# === Setup path for assets ===
try:
    ASSET_PATH = os.path.dirname(os.path.abspath(__file__))
except NameError:
    ASSET_PATH = os.getcwd()

# Loads, resizes, and returns a candy image or a colored block as a fallback.
def load_image(index):
    TARGET_SIZE = (58, 58)
    path = os.path.join(ASSET_PATH, f"candy{index}.png")
    try:
        img = Image.open(path)
        img = img.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception:
        img = tk.PhotoImage(width=60, height=60)
        color = ["red", "blue", "green", "yellow", "purple", "orange", "cyan", "pink"]
        img.put(color[index % len(color)], to=(0, 0, 60, 60))
        return img

class Candy:
    def __init__(self, image_index, image_list):
        self.image_index = image_index
        self.image_list = image_list

    @property
    def image(self):
        return self.image_list[self.image_index]

class Board:
    def __init__(self, rows, cols, num_types, image_list):
        self.rows = rows
        self.cols = cols
        self.num_types = num_types
        self.image_list = image_list
        self.grid = [[Candy(random.randint(0, num_types - 1), self.image_list) for _ in range(cols)] for _ in range(rows)]
        self.matches = set()
        self.remove_matches()

    def swap(self, r1, c1, r2, c2):
        # Swaps two adjacent candies if the swap results in a match.
        if not self.valid_indices(r1, c1) or not self.valid_indices(r2, c2):
            return False
        if not ((abs(r1 - r2) == 1 and c1 == c2) or (abs(c1 - c2) == 1 and r1 == r2)):
            return False

        self.grid[r1][c1], self.grid[r2][c2] = self.grid[r2][c2], self.grid[r1][c1]

        if not (self._check_local_matches(r1, c1) or self._check_local_matches(r2, c2)):
            self.grid[r1][c1], self.grid[r2][c2] = self.grid[r2][c2], self.grid[r1][c1]
            return False

        return True

    def valid_indices(self, r, c):
        # Checks if the given row and column are within the board's bounds.
        return 0 <= r < self.rows and 0 <= c < self.cols

    def _check_local_matches(self, r, c):
        # Efficiently checks for a match only around a specific candy's location.
        candy_type = self.grid[r][c].image_index

        h_count = 1
        for i in range(1, 3):
            if self.valid_indices(r, c - i) and self.grid[r][c - i].image_index == candy_type:
                h_count += 1
            else:
                break
        for i in range(1, 3):
            if self.valid_indices(r, c + i) and self.grid[r][c + i].image_index == candy_type:
                h_count += 1
            else:
                break
        if h_count >= 3: return True

        v_count = 1
        for i in range(1, 3):
            if self.valid_indices(r - i, c) and self.grid[r - i][c].image_index == candy_type:
                v_count += 1
            else:
                break
        for i in range(1, 3):
            if self.valid_indices(r + i, c) and self.grid[r + i][c].image_index == candy_type:
                v_count += 1
            else:
                break
        if v_count >= 3: return True
        return False

    def check_matches(self):
        # Scans the entire board for all horizontal and vertical matches.
        matches = set()
        for r in range(self.rows):
            start_c = 0
            for c in range(1, self.cols + 1):
                if c == self.cols or self.grid[r][c].image_index != self.grid[r][start_c].image_index:
                    if c - start_c >= 3:
                        matches.update([(r, i) for i in range(start_c, c)])
                    start_c = c

        for c in range(self.cols):
            start_r = 0
            for r in range(1, self.rows + 1):
                if r == self.rows or self.grid[r][c].image_index != self.grid[start_r][c].image_index:
                    if r - start_r >= 3:
                        matches.update([(i, c) for i in range(start_r, r)])
                    start_r = r

        self.matches = matches
        return len(matches) > 0

    def get_match_positions(self):
        # Finds and returns the positions of all matched candies.
        self.check_matches()
        return list(self.matches)

    def remove_matches(self):
        # Removes all matched candies and refills the board with new ones from the top.
        total_removed = 0
        while self.check_matches():
            for r, c in self.matches:
                self.grid[r][c] = None
            total_removed += len(self.matches)

            for c in range(self.cols):
                stack = []
                for r in range(self.rows):
                    if self.grid[r][c] is not None:
                        stack.append(self.grid[r][c])
                for r in range(self.rows):
                    if len(stack) > 0:
                        self.grid[self.rows - 1 - r][c] = stack.pop()
                    else:
                        self.grid[self.rows - 1 - r][c] = Candy(random.randint(0, self.num_types - 1), self.image_list)
        return total_removed

    def refill(self):
        # Updates the board model after a match and returns data for falling animations.
        if not self.matches:
            return {}

        fall_info = [[(None, r) for c in range(self.cols)] for r in range(self.rows)]

        for r, c in self.matches:
            self.grid[r][c] = None

        for c in range(self.cols):
            empty_count = 0
            for r in range(self.rows - 1, -1, -1):
                if self.grid[r][c] is None:
                    empty_count += 1
                elif empty_count > 0:
                    new_r = r + empty_count
                    self.grid[new_r][c] = self.grid[r][c]
                    self.grid[r][c] = None
                    fall_info[new_r][c] = (r, new_r)

            for r in range(empty_count):
                self.grid[r][c] = Candy(random.randint(0, self.num_types - 1), self.image_list)
                fall_info[r][c] = (None, r) # New candy

        return fall_info

LEVELS = [
    {"score_goal": 550, "moves": 15, "board_size": (5, 5), "num_types": 4, "difficulty": "Easy"},
    {"score_goal": 700, "moves": 13, "board_size": (5, 5), "num_types": 5, "difficulty": "Easy"},
    {"score_goal": 800, "moves": 15, "board_size": (6, 6), "num_types": 5, "difficulty": "Medium"},
    {"score_goal": 900, "moves": 20, "board_size": (6, 6), "num_types": 6, "difficulty": "Medium"},
    {"score_goal": 1000, "moves": 20, "board_size": (7, 7), "num_types": 6, "difficulty": "Hard"},
    {"score_goal": 1100, "moves": 20, "board_size": (7, 7), "num_types": 7, "difficulty": "Hard"},
    {"score_goal": 1200, "moves": 20, "board_size": (8, 8), "num_types": 7, "difficulty": "Very Hard"},
    {"score_goal": 1300, "moves": 20, "board_size": (8, 8), "num_types": 8, "difficulty": "Very Hard"},
    {"score_goal": 1400, "moves": 20, "board_size": (8, 8), "num_types": 8, "difficulty": "Expert"},
    {"score_goal": 1500, "moves": 20, "board_size": (8, 8), "num_types": 9, "difficulty": "Expert"}
]

class CandyCrushGUI:
    # Initializes the main game window, layout, and starts the first level.
    def __init__(self, root: tk.Tk):
        self.root = root
        self.level = 0
        self.score = 0
        self.selected = None
        self.is_auto_playing = False
        self.is_animating = False
        self.failed_attempts = 0
        self.score_goal = 0
        self.moves_left = 0
        self.root.title("Candy Crush")
        self.idle_timer_id = None

        self.root.geometry("800x700")
        self.root.resizable(True, True)

        try:
            img_path = os.path.join(ASSET_PATH, "background.png")
            self.bg_img_pil = Image.open(img_path).resize((800, 700), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(self.bg_img_pil)
            self.bg_label = tk.Label(root, image=self.bg_photo)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Could not load main background image: {e}")
            root.config(bg="#fde0e0")

        self.header = tk.Label(root, text="\U0001f36c Candy Crush \U0001f36d", font=("Poppins", 26, "bold"), fg="#d12c8b")
        self.header.place(relx=0.5, rely=0.05, anchor="n")

        self.frame = tk.Frame(root, bg="#ffffff", bd=5, relief="groove")
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        self.info_container = tk.Frame(self.root, bg=self.root.cget('bg'))
        self.info_container.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        self.info_frame = tk.Frame(self.info_container, bg="#f5c8ff")
        self.info_frame.pack()
        self._create_info_widgets()

        self.init_level()

    def init_level(self):
        # Sets up the game state and UI for the current level.
        self.score = 0
        self.is_animating = False
        self.is_auto_playing = False
        self.selected = None

        config = LEVELS[self.level]
        self.rows, self.cols = config["board_size"]
        self.num_types = config["num_types"]

        self.moves_left = config["moves"] + (self.failed_attempts * 5)
        self.score_goal = config["score_goal"]

        self.candy_images = [load_image(i) for i in range(self.num_types)]
        self.board = Board(self.rows, self.cols, self.num_types, self.candy_images)
        self.buttons = [[None for _ in range(self.cols)] for _ in range(self.rows)]

        for widget in self.frame.winfo_children():
            widget.destroy()

        self.create_widgets()

        self.header.config(bg=self.bg_label.cget('bg'))
        self.info_container.config(bg=self.bg_label.cget('bg'))

        self.update_gui()
        self.start_idle_timer()

    # Creates the statistics and control buttons in the bottom info panel.
    def _create_info_widgets(self):
        stats_frame = tk.Frame(self.info_frame, bg="#f5c8ff")
        stats_frame.grid(row=0, column=0, columnspan=3)

        self.score_label = tk.Label(self.info_frame, text=f"Score: {self.score}", font=("Arial", 14), bg="#f5c8ff", fg="black")
        self.score_label.grid(row=0, column=0, padx=10)

        self.goal_label = tk.Label(self.info_frame, text=f"Goal: {self.score_goal}", font=("Arial", 14), bg="#f5c8ff", fg="black")
        self.goal_label.grid(row=0, column=1, padx=10)

        self.moves_label = tk.Label(self.info_frame, text=f"Moves: {self.moves_left}", font=("Arial", 14), bg="#f5c8ff", fg="black")
        self.moves_label.grid(row=0, column=2, padx=10)

        self.level_label = tk.Label(self.info_frame, text=f"Level: {self.level + 1} ({LEVELS[self.level]['difficulty']})", font=("Arial", 14), bg="#f5c8ff", fg="black")
        self.level_label.grid(row=0, column=3, padx=10)

        button_frame = tk.Frame(self.info_frame, bg="#f5c8ff")
        button_frame.grid(row=1, column=0, columnspan=4, pady=5)

        restart_btn = tk.Button(self.info_frame, text="\U0001f501 Restart", font=("Arial", 12, "bold"),
                                command=self.restart_game, bg="#ffdddd", fg="#770000", relief="raised", bd=2)
        restart_btn.grid(row=1, column=0, padx=10)

        hint_btn = tk.Button(self.info_frame, text="\U0001f4a1 Hint", font=("Arial", 12, "bold"),
                             command=self.show_hint, bg="#fffbdd", fg="#777700", relief="raised", bd=2)
        hint_btn.grid(row=1, column=1, padx=10)

        self.autoplay_btn = tk.Button(self.info_frame, text="\U000025b6 Auto-Play", font=("Arial", 12, "bold"),
                                      command=self.toggle_autoplay, bg="#ddffdd", fg="#005500", relief="raised", bd=2)
        self.autoplay_btn.grid(row=1, column=2, columnspan=2, padx=10)

    def create_widgets(self):
        # Creates the grid of candy buttons for the current level.
        for r in range(self.rows):
            for c in range(self.cols):
                btn = tk.Button(self.frame, width=60, height=60, image=None, borderwidth=2, bg="white",
                                relief="raised", command=lambda r=r, c=c: self.select_candy(r, c))
                btn.grid(row=r, column=c, padx=1, pady=1)
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#ffe6f0"))
                btn.bind("<Leave>", lambda e, b=btn: b.config(bg="white"))
                self.buttons[r][c] = btn

    def update_gui(self):
        # Refreshes the entire game grid and stat labels with the current game state.
        for r in range(self.rows):
            for c in range(self.cols):
                candy = self.board.grid[r][c]
                self.buttons[r][c].image = candy.image
                self.buttons[r][c].config(image=candy.image, bg="white")
        self.score_label.config(text=f"Score: {self.score}")
        self.goal_label.config(text=f"Goal: {self.score_goal}")
        self.moves_label.config(text=f"Moves: {self.moves_left}")
        self.level_label.config(text=f"Level: {self.level + 1} ({LEVELS[self.level]['difficulty']})")

    # Animates the visual swapping of two candies.
    def animate_swap(self, r1, c1, r2, c2, callback=None):
        x1, y1 = self.buttons[r1][c1].winfo_x(), self.buttons[r1][c1].winfo_y()
        x2, y2 = self.buttons[r2][c2].winfo_x(), self.buttons[r2][c2].winfo_y()
        dx = (x2 - x1) / 10.0
        dy = (y2 - y1) / 10.0

        temp_label1 = tk.Label(self.frame, image=self.board.grid[r1][c1].image, bg="white")
        temp_label2 = tk.Label(self.frame, image=self.board.grid[r2][c2].image, bg="white")
        temp_label1.place(x=x1, y=y1)
        temp_label2.place(x=x2, y=y2)

        def move_step(step):
            nonlocal x1, y1, x2, y2
            x1 += dx
            y1 += dy
            x2 -= dx
            y2 -= dy
            temp_label1.place(x=x1, y=y1)
            temp_label2.place(x=x2, y=y2)

            if step < 10:
                self.root.after(20, lambda s=step + 1: move_step(s))
            else:
                temp_label1.destroy()
                temp_label2.destroy()
                if callback:
                    callback()
        move_step(1)

    # Animates a single candy falling to a new position.
    def animate_fall(self, r, c, end_r, callback=None):
        x, y = self.buttons[r][c].winfo_x(), self.buttons[r][c].winfo_y()
        dy = (self.buttons[end_r][c].winfo_y() - y) / 10.0

        def fall_step(step):
            nonlocal y
            y += dy
            self.buttons[r][c].place(x=x, y=y)

            if step < 10:
                self.root.after(20, lambda s=step + 1: fall_step(s))
            else:
                if callback:
                    callback()
        fall_step(1)

    def animate_and_remove_matches(self):
        # Starts the animation sequence for matched candies.
        if not self.board.check_matches():
            return

        for r, c in self.board.matches:
            self.buttons[r][c].config(image='', bg="#fff5f5")
        self.root.after(200, self._refill_and_animate_fall)

    def _refill_and_animate_fall(self):
        # Refills the board model and triggers falling animations.
        fall_info = self.board.refill()
        removed = len(self.board.matches)
        self.score += removed * 10

        animated_candies = set()
        for c in range(self.board.cols):
            for r in range(self.board.rows -1, -1, -1):
                if (r, c) not in animated_candies:
                    start_r, end_r = fall_info[r][c]
                    if start_r is not None:
                        img = self.board.grid[end_r][c].image
                        self.buttons[end_r][c].config(image=img)
                        self.buttons[start_r][c].config(image='') # Hide original
                        animated_candies.add((end_r, c))

        self.update_gui()

        self.root.after(250, self._check_game_state)

    def _check_game_state(self):
        # Checks for cascades, win/loss conditions, or continues auto-play after a turn.
        if self.board.check_matches():
            self.root.after(300, self.animate_and_remove_matches)
        elif self.score >= self.score_goal:
            self.failed_attempts = 0
            messagebox.showinfo("Level Complete \U0001f389", f"You've completed Level {self.level + 1}!")
            self.next_level()
        elif self.moves_left <= 0:
            self.failed_attempts += 1
            if messagebox.askretrycancel("Game Over", f"You've run out of moves! Score: {self.score}/{self.score_goal}\n\nTry this level again?"):
                self.init_level()
            else:
                self.root.quit()
        elif self.is_auto_playing:
            self.root.after(500, self.perform_auto_play)
        else:
            self.is_animating = False
            self.reset_idle_timer()

    def select_candy(self, r, c):
            # Handles player clicks for selecting and swapping candies.
            if self.is_auto_playing or self.is_animating:
                return
    
            if self.selected is None:
                self.selected = (r, c)
                self.buttons[r][c].config(relief="sunken", bg="#e0e0e0")
            else:
                r1, c1 = self.selected
    
                if (r, c) == (r1, c1):
                    self.buttons[r1][c1].config(relief="flat", bg="white")
                    self.selected = None
                    return
    
                self.reset_idle_timer()

                if self.board.swap(r1, c1, r, c):
                    self.is_animating = True
                    self.moves_left -= 1
                    self.moves_label.config(text=f"Moves: {self.moves_left}")
                    self.animate_swap(r1, c1, r, c, callback=self.animate_and_remove_matches)
                else:
                    self.root.bell()
    
                self.buttons[r1][c1].config(relief="flat", bg="white")
                self.selected = None
    
    def next_level(self):
            # Advances the game to the next level or ends the game if all levels are complete.
            if self.level + 1 < len(LEVELS):
                self.level += 1
                self.failed_attempts = 0
                self.score = 0
                self.init_level()
            else:
                messagebox.showinfo("Victory \U0001f389", "You've completed all levels!")
                self.root.quit()
    
    def restart_game(self):
            # Resets the game to Level 1.
            self.level = 0
            self.score = 0
            self.failed_attempts = 0
            self.reset_idle_timer()
            self.init_level()
    
    def start_idle_timer(self):
            # Starts a timer that shows a hint after a period of inactivity.
            self.idle_timer_id = self.root.after(5000, self.show_hint)
    
    def reset_idle_timer(self):
            # Cancels the current idle timer and starts a new one.
            if self.idle_timer_id:
                self.root.after_cancel(self.idle_timer_id)
            self.start_idle_timer()
    
    def find_hint_fast(self):
            # Finds the first available valid move on the board using a greedy search.
            for r in range(self.rows):
                for c in range(self.cols):
                    if c + 1 < self.cols:
                        self.board.grid[r][c], self.board.grid[r][c + 1] = self.board.grid[r][c + 1], self.board.grid[r][c]
                        if self.board._check_local_matches(r, c) or self.board._check_local_matches(r, c + 1):
                            self.board.grid[r][c], self.board.grid[r][c + 1] = self.board.grid[r][c + 1], self.board.grid[r][c] # Swap back
                            return (r, c), (r, c + 1)
                        self.board.grid[r][c], self.board.grid[r][c + 1] = self.board.grid[r][c + 1], self.board.grid[r][c] # Swap back
                    if r + 1 < self.rows:
                        self.board.grid[r][c], self.board.grid[r + 1][c] = self.board.grid[r + 1][c], self.board.grid[r][c]
                        if self.board._check_local_matches(r, c) or self.board._check_local_matches(r + 1, c):
                            self.board.grid[r][c], self.board.grid[r + 1][c] = self.board.grid[r + 1][c], self.board.grid[r][c] # Swap back
                            return (r, c), (r + 1, c)
                        self.board.grid[r][c], self.board.grid[r + 1][c] = self.board.grid[r + 1][c], self.board.grid[r][c] # Swap back
            return None
    
    def show_hint(self):
            # Visually highlights a suggested move for the player.
            if self.is_auto_playing: return
            hint_move = self.find_hint_fast()
            if hint_move:
                (r1, c1), (r2, c2) = hint_move
                btn1, btn2 = self.buttons[r1][c1], self.buttons[r2][c2]
    
                btn1.unbind("<Enter>")
                btn1.unbind("<Leave>")
                btn2.unbind("<Enter>")
                btn2.unbind("<Leave>")
    
                btn1.config(bg="yellow")
                btn2.config(bg="yellow")
    
                def restore_hint_buttons():
                    if btn1.winfo_exists():
                        btn1.config(bg="white")
                        btn1.bind("<Enter>", lambda e, b=btn1: b.config(bg="#ffe6f0"))
                        btn1.bind("<Leave>", lambda e, b=btn1: b.config(bg="white"))
                    if btn2.winfo_exists():
                        btn2.config(bg="white")
                        btn2.bind("<Enter>", lambda e, b=btn2: b.config(bg="#ffe6f0"))
                        btn2.bind("<Leave>", lambda e, b=btn2: b.config(bg="white"))
    
                self.root.after(700, restore_hint_buttons)
            else:
                messagebox.showinfo("No Moves", "No possible moves found. Consider reshuffling the board.")
    
    def toggle_autoplay(self):
            # Starts or stops the automatic playing mode.
            self.is_auto_playing = not self.is_auto_playing
            if self.is_auto_playing:
                self.autoplay_btn.config(text="\U000023f8 Stop Auto", relief="sunken", bg="#ffaaaa")
                self.perform_auto_play()
            else:
                self.autoplay_btn.config(text="\U000025b6 Auto-Play", relief="raised", bg="#ddffdd")
    
    def perform_auto_play(self):
            # Executes a single move found by the hint system.
            if not self.is_auto_playing:
                return
    
            hint_move = self.find_hint_fast()
            if hint_move:
                (r1, c1), (r2, c2) = hint_move
                self.board.swap(r1, c1, r2, c2)
                self.is_animating = True
                self.moves_left -= 1
                self.moves_label.config(text=f"Moves: {self.moves_left}")
                self.animate_and_remove_matches()
            else:
                self.toggle_autoplay()

if __name__ == "__main__":
    root = tk.Tk()
    game = CandyCrushGUI(root)
    root.mainloop()