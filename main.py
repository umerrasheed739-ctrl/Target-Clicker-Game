git # Target Clicker Game
# A simple game built with Tkinter for a student assignment.
# The player clicks a moving target as many times as possible in 30 seconds.

import tkinter as tk
from tkinter import messagebox
import random


# ----- Game Settings -----
GAME_TIME = 30          # total seconds for one game
TARGET_COLORS = ["red", "orange", "green", "blue", "purple"]

# Target sizes (radius in pixels) for each difficulty level
DIFFICULTY_SIZES = {
    "Easy": 45,
    "Medium": 30,
    "Hard": 18,
}


class TargetClickerGame:
    """Main game class that builds the window and holds the game logic."""

    def __init__(self, root):
        self.root = root
        self.root.title("Target Clicker")
        # Allow the window to be resized and maximized
        self.root.resizable(True, True)

        # Game state variables
        self.score = 0
        self.time_left = GAME_TIME
        self.target_radius = DIFFICULTY_SIZES["Easy"]
        self.target_id = None          # canvas item id of the current target
        self.game_running = False      # True only while a game is active
        self.timer_job = None          # id of the scheduled timer event
        self.is_fullscreen = False     # tracks fullscreen on/off state

        self._build_gui()

        # Press Escape to exit fullscreen
        self.root.bind("<Escape>", self._exit_fullscreen)

    # ----- Build the GUI -----
    def _build_gui(self):
        # Title label
        tk.Label(
            self.root,
            text="Target Clicker",
            font=("Helvetica", 20, "bold"),
        ).pack(pady=(10, 5))

        # Top bar: score (left) and timer (right)
        top_bar = tk.Frame(self.root)
        top_bar.pack(fill="x", padx=20)

        self.score_label = tk.Label(
            top_bar, text="Score: 0", font=("Helvetica", 14)
        )
        self.score_label.pack(side="left")

        self.timer_label = tk.Label(
            top_bar, text=f"Time: {GAME_TIME}", font=("Helvetica", 14)
        )
        self.timer_label.pack(side="right")

        # Difficulty selection row
        diff_frame = tk.Frame(self.root)
        diff_frame.pack(pady=(5, 0))

        tk.Label(diff_frame, text="Difficulty:", font=("Helvetica", 11)).pack(side="left")

        self.difficulty = tk.StringVar(value="Easy")
        for level in DIFFICULTY_SIZES:
            tk.Radiobutton(
                diff_frame,
                text=level,
                variable=self.difficulty,
                value=level,
                font=("Helvetica", 11),
            ).pack(side="left", padx=5)

        # Game canvas (the play area) - grows with the window
        self.canvas = tk.Canvas(
            self.root,
            width=500,
            height=400,
            bg="white",
            highlightthickness=1,
            highlightbackground="black",
        )
        # fill="both" + expand=True lets the canvas use all available space
        self.canvas.pack(fill="both", expand=True, padx=20, pady=10)
        # Bind a click on the canvas to the target-click handler
        self.canvas.bind("<Button-1>", self._on_canvas_click)

        # Buttons row
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=(0, 10))

        tk.Button(
            btn_frame, text="Start Game", width=12,
            command=self.start_game,
        ).pack(side="left", padx=10)

        tk.Button(
            btn_frame, text="Restart Game", width=12,
            command=self.restart_game,
        ).pack(side="left", padx=10)

        # Fullscreen toggle button
        tk.Button(
            btn_frame, text="Fullscreen", width=12,
            command=self.toggle_fullscreen,
        ).pack(side="left", padx=10)

    # ----- Fullscreen -----
    def toggle_fullscreen(self):
        """Switch between fullscreen and normal window mode."""
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)

    def _exit_fullscreen(self, event):
        """Exit fullscreen when the Escape key is pressed."""
        if self.is_fullscreen:
            self.is_fullscreen = False
            self.root.attributes("-fullscreen", False)

    # ----- Target Drawing -----
    def _draw_target(self):
        """Draw a circular target at a random position on the canvas."""
        self._clear_target()

        radius = self.target_radius
        # Use the actual canvas size (so it works when resized/maximized)
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        # Fallback to default size if the canvas has not been drawn yet
        if canvas_width <= 1:
            canvas_width = 500
        if canvas_height <= 1:
            canvas_height = 400

        # Pick a random center that keeps the whole circle inside the canvas
        x = random.randint(radius, canvas_width - radius)
        y = random.randint(radius, canvas_height - radius)

        color = random.choice(TARGET_COLORS)

        self.target_id = self.canvas.create_oval(
            x - radius, y - radius,
            x + radius, y + radius,
            fill=color, outline="black",
        )

    def _clear_target(self):
        """Remove the current target from the canvas (if any)."""
        if self.target_id is not None:
            self.canvas.delete(self.target_id)
            self.target_id = None

    # ----- Click Handling -----
    def _on_canvas_click(self, event):
        # Ignore clicks if the game is not running
        if not self.game_running or self.target_id is None:
            return

        # Find the closest canvas item to the click point
        closest = self.canvas.find_closest(event.x, event.y)

        # If the closest item is the target, it counts as a hit
        if closest and closest[0] == self.target_id:
            self.score += 1
            self.score_label.config(text=f"Score: {self.score}")
            self._draw_target()  # move target to a new random spot

    # ----- Timer -----
    def _tick(self):
        """Decrease the timer by one second; end the game at zero."""
        if not self.game_running:
            return

        self.time_left -= 1
        self.timer_label.config(text=f"Time: {self.time_left}")

        if self.time_left <= 0:
            self._end_game()
        else:
            # Schedule the next tick one second later
            self.timer_job = self.root.after(1000, self._tick)

    # ----- Game Control -----
    def start_game(self):
        """Start a brand new 30-second game."""
        if self.game_running:
            return  # a game is already running

        # Apply the chosen difficulty
        self.target_radius = DIFFICULTY_SIZES[self.difficulty.get()]

        # Reset state
        self.score = 0
        self.time_left = GAME_TIME
        self.score_label.config(text=f"Score: {self.score}")
        self.timer_label.config(text=f"Time: {self.time_left}")

        # Begin
        self.game_running = True
        self._draw_target()
        self.timer_job = self.root.after(1000, self._tick)

    def restart_game(self):
        """Stop the current game (if any) and reset to the starting state."""
        self._stop_timer()
        self.game_running = False
        self._clear_target()

        self.score = 0
        self.time_left = GAME_TIME
        self.score_label.config(text=f"Score: {self.score}")
        self.timer_label.config(text=f"Time: {self.time_left}")

    def _end_game(self):
        """End the game, disable the target, and show the final score."""
        self.game_running = False
        self._clear_target()
        messagebox.showinfo("Game Over", f"Game Over!\nYour final score is {self.score}.")

    def _stop_timer(self):
        """Cancel any pending timer event."""
        if self.timer_job is not None:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None


# ----- Run the program -----
if __name__ == "__main__":
    root = tk.Tk()
    app = TargetClickerGame(root)
    root.mainloop()