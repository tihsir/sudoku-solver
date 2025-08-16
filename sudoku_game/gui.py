# sudoku_game/gui.py
import tkinter as tk
from tkinter import ttk, messagebox
from copy import deepcopy

from sudoku_game.board import generate_puzzle
from sudoku_game.solver import solve
from sudoku_game.validator import is_valid
from sudoku_game.hints import get_hint

CELL_SIZE = 50
GRID_SIZE = 9
MARGIN = 20
BOARD_PIXELS = CELL_SIZE * GRID_SIZE
CANVAS_W = BOARD_PIXELS + 2 * MARGIN
CANVAS_H = BOARD_PIXELS + 2 * MARGIN

class SudokuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku")

        # State
        self.difficulty = tk.StringVar(value="medium")
        self.board = None
        self.working = None
        self.givens = set()
        self.selected = None  # (r,c) or None
        self.show_conflicts = tk.BooleanVar(value=True)

        # UI
        self._build_ui()
        self.new_game()

    def _build_ui(self):
        outer = ttk.Frame(self.root, padding=10)
        outer.grid(row=0, column=0, sticky="nsew")

        # Top controls
        top = ttk.Frame(outer)
        top.grid(row=0, column=0, sticky="w", pady=(0, 8))

        ttk.Label(top, text="Difficulty:").grid(row=0, column=0, padx=(0, 6))
        diff = ttk.Combobox(top, textvariable=self.difficulty, values=["easy", "medium", "hard"], width=8, state="readonly")
        diff.grid(row=0, column=1)
        ttk.Button(top, text="New Game", command=self.new_game).grid(row=0, column=2, padx=(8, 0))
        ttk.Button(top, text="Solve", command=self.solve_current).grid(row=0, column=3, padx=6)
        ttk.Button(top, text="Hint", command=self.hint_current).grid(row=0, column=4, padx=6)
        ttk.Button(top, text="Check", command=self.check_conflicts_popup).grid(row=0, column=5, padx=6)
        ttk.Checkbutton(top, text="Highlight conflicts", variable=self.show_conflicts, command=self.redraw).grid(row=0, column=6, padx=(12,0))

        # Canvas
        self.canvas = tk.Canvas(outer, width=CANVAS_W, height=CANVAS_H, bg="white", highlightthickness=0)
        self.canvas.grid(row=1, column=0)
        self.canvas.bind("<Button-1>", self.on_click)
        self.root.bind("<Key>", self.on_key)

        # Number pad
        pad = ttk.Frame(outer)
        pad.grid(row=2, column=0, pady=(8,0))
        for n in range(1, 10):
            b = ttk.Button(pad, text=str(n), width=3, command=lambda x=n: self.place_number(x))
            b.grid(row=0, column=n-1, padx=2)
        ttk.Button(pad, text="Clear", width=6, command=self.clear_cell).grid(row=0, column=9, padx=(10,0))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    def new_game(self):
        self.board = generate_puzzle(self.difficulty.get())
        self.working = deepcopy(self.board)
        self.givens = {(r, c) for r in range(9) for c in range(9) if self.board[r][c] != 0}
        self.selected = None
        self.redraw()

    def solve_current(self):
        temp = deepcopy(self.working)
        if solve(temp):
            self.working = temp
            self.redraw()
        else:
            messagebox.showwarning("Unsolvable", "This board appears unsolvable.")

    def hint_current(self):
        if not self.selected:
            messagebox.showinfo("Hint", "Click a cell first.")
            return
        r, c = self.selected
        hint = get_hint(self.working, r, c)
        if hint is None:
            messagebox.showinfo("Hint", "No hint available for that cell.")
            return
        val, reason = hint
        if (r, c) not in self.givens:
            self.working[r][c] = val
            self.redraw()
        messagebox.showinfo("Hint", f"({r},{c}) → {val}\n{reason}")

    def check_conflicts_popup(self):
        bad = self._collect_conflicts(self.working)
        if not bad:
            messagebox.showinfo("Check", "No rule violations detected.")
        else:
            coords = ", ".join(f"({r},{c})" for r, c in sorted(bad))
            messagebox.showwarning("Check", f"Conflicting cells: {coords}")
        self.redraw()

    def on_click(self, event):
        x, y = event.x - MARGIN, event.y - MARGIN
        if 0 <= x < BOARD_PIXELS and 0 <= y < BOARD_PIXELS:
            c = x // CELL_SIZE
            r = y // CELL_SIZE
            self.selected = (int(r), int(c))
            self.redraw()

    def on_key(self, event):
        if not self.selected:
            return
        if event.keysym in [str(n) for n in range(1,10)]:
            self.place_number(int(event.keysym))
        elif event.keysym in ("BackSpace", "Delete", "0"):
            self.clear_cell()
        elif event.keysym in ("Left", "Right", "Up", "Down"):
            r, c = self.selected
            if event.keysym == "Left":  c = max(0, c-1)
            if event.keysym == "Right": c = min(8, c+1)
            if event.keysym == "Up":    r = max(0, r-1)
            if event.keysym == "Down":  r = min(8, r+1)
            self.selected = (r, c)
            self.redraw()

    def place_number(self, n: int):
        if not self.selected:
            return
        r, c = self.selected
        if (r, c) in self.givens:
            return  
        # strict placement 
        # if not is_valid(self.working, r, c, n):
        #     self.flash_cell(r, c)
        #     return
        self.working[r][c] = n
        self.redraw()
        if self.is_complete(self.working):
            messagebox.showinfo("Solved", "Congratulations! Puzzle solved.")

    def clear_cell(self):
        if not self.selected:
            return
        r, c = self.selected
        if (r, c) in self.givens:
            return
        self.working[r][c] = 0
        self.redraw()

    def redraw(self):
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, CANVAS_W, CANVAS_H, fill="white", outline="")
        if self.selected:
            r, c = self.selected
            x0 = MARGIN + c * CELL_SIZE
            y0 = MARGIN + r * CELL_SIZE
            x1 = x0 + CELL_SIZE
            y1 = y0 + CELL_SIZE
            self.canvas.create_rectangle(x0, y0, x1, y1, fill="#f0f8ff", width=0)

        # Conflicts
        bad = self._collect_conflicts(self.working) if self.show_conflicts.get() else set()

        # Numbers
        for r in range(9):
            for c in range(9):
                v = self.working[r][c]
                if v != 0:
                    x = MARGIN + c * CELL_SIZE + CELL_SIZE / 2
                    y = MARGIN + r * CELL_SIZE + CELL_SIZE / 2
                    color = "#0a6cff" if (r, c) in self.givens else ("#d8000c" if (r, c) in bad else "#222")
                    font = ("Helvetica", 18, "bold" if (r, c) in self.givens else "normal")
                    self.canvas.create_text(x, y, text=str(v), fill=color, font=font)

        # Grid lines
        for i in range(10):
            w = 3 if i % 3 == 0 else 1
            x = MARGIN + i * CELL_SIZE
            y0 = MARGIN
            y1 = MARGIN + 9 * CELL_SIZE
            self.canvas.create_line(x, y0, x, y1, width=w, fill="#000")
            y = MARGIN + i * CELL_SIZE
            x0 = MARGIN
            x1 = MARGIN + 9 * CELL_SIZE
            self.canvas.create_line(x0, y, x1, y, width=w, fill="#000")

    def _collect_conflicts(self, board):
        bad = set()
        # Rows
        for r in range(9):
            seen = {}
            for c in range(9):
                v = board[r][c]
                if v == 0: continue
                if v in seen:
                    bad.add((r,c)); bad.add((r,seen[v]))
                else:
                    seen[v] = c
        # Cols
        for c in range(9):
            seen = {}
            for r in range(9):
                v = board[r][c]
                if v == 0: continue
                if v in seen:
                    bad.add((r,c)); bad.add((seen[v],c))
                else:
                    seen[v] = r
        # Boxes
        for br in range(0,9,3):
            for bc in range(0,9,3):
                seen = {}
                for dr in range(3):
                    for dc in range(3):
                        r, c = br+dr, bc+dc
                        v = board[r][c]
                        if v == 0: continue
                        if v in seen:
                            rr, cc = seen[v]
                            bad.add((r,c)); bad.add((rr,cc))
                        else:
                            seen[v] = (r,c)
        return bad

    def is_complete(self, board):
        return all(all(v != 0 for v in row) for row in board) and len(self._collect_conflicts(board)) == 0

    def flash_cell(self, r, c):
        x0 = MARGIN + c * CELL_SIZE
        y0 = MARGIN + r * CELL_SIZE
        x1 = x0 + CELL_SIZE
        y1 = y0 + CELL_SIZE
        rect = self.canvas.create_rectangle(x0, y0, x1, y1, fill="#ffe5e5", width=0)
        self.root.after(150, lambda: self.canvas.delete(rect))

def launch():
    root = tk.Tk()
    SudokuGUI(root)
    root.mainloop()
