import tkinter as tk
from tkinter import messagebox, ttk
import random
import time

# ---------------- Sudoku Solver ----------------
def is_valid(board, row, col, num):
    size = len(board)
    for i in range(size):
        if board[row][i] == num or board[i][col] == num:
            return False
    n = int(size ** 0.5)
    start_row, start_col = n * (row // n), n * (col // n)
    for i in range(n):
        for j in range(n):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def solve_sudoku(board):
    size = len(board)
    for row in range(size):
        for col in range(size):
            if board[row][col] == 0:
                for num in range(1, size + 1):
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        if solve_sudoku(board):
                            return True
                        board[row][col] = 0
                return False
    return True

# ---------------- Puzzle Generator ----------------
def generate_puzzle(size=9, difficulty='easy'):
    board = [[0 for _ in range(size)] for _ in range(size)]
    n = int(size ** 0.5)
    for k in range(0, size, n):
        fill_block(board, k, k, n)
    solve_sudoku(board)
    remove_cells(board, difficulty)
    return board

def fill_block(board, row, col, n):
    nums = list(range(1, n*n + 1))
    random.shuffle(nums)
    for i in range(n):
        for j in range(n):
            board[row+i][col+j] = nums.pop()

def remove_cells(board, difficulty):
    size = len(board)
    if difficulty == 'easy':
        remove_count = size * size // 4
    elif difficulty == 'medium':
        remove_count = size * size // 3
    else:
        remove_count = size * size // 2
    while remove_count > 0:
        i, j = random.randint(0, size-1), random.randint(0, size-1)
        if board[i][j] != 0:
            board[i][j] = 0
            remove_count -= 1

# ---------------- GUI ----------------
class SudokuGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Solver & Game")
        self.size = 9
        self.entries = []
        self.start_time = None
        self.timer_running = False
        self.timer_label = tk.Label(root, text="Time: 00:00", font=('Arial', 14))
        self.timer_label.grid(row=0, column=0, columnspan=9)
        self.create_grid()
        self.create_controls()
        self.update_timer()
        self.colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(0,255,255),(255,0,255)]

    def create_grid(self):
        self.entries = []
        for i in range(self.size):
            row_entries = []
            for j in range(self.size):
                e = tk.Entry(self.root, width=3, font=('Arial', 18), justify='center')
                e.grid(row=i+1, column=j, padx=1, pady=1)
                e.bind("<FocusOut>", lambda event, x=i, y=j: self.check_cell(x, y))
                row_entries.append(e)
            self.entries.append(row_entries)

    def create_controls(self):
        self.solve_btn = tk.Button(self.root, text="Solve", command=self.solve)
        self.solve_btn.grid(row=self.size+1, column=0, columnspan=3, sticky="we")

        self.clear_btn = tk.Button(self.root, text="Clear", command=self.clear_board)
        self.clear_btn.grid(row=self.size+1, column=3, columnspan=3, sticky="we")

        self.generate_btn = tk.Button(self.root, text="Generate Puzzle", command=self.generate)
        self.generate_btn.grid(row=self.size+1, column=6, columnspan=3, sticky="we")

        tk.Label(self.root, text="Difficulty:").grid(row=self.size+2, column=0, columnspan=2)
        self.diff_var = tk.StringVar(value="easy")
        self.diff_menu = ttk.Combobox(self.root, textvariable=self.diff_var, values=["easy","medium","hard"], width=8)
        self.diff_menu.grid(row=self.size+2, column=2, columnspan=2)

    def get_board(self):
        board = []
        for i in range(self.size):
            row = []
            for j in range(self.size):
                val = self.entries[i][j].get()
                if val.isdigit():
                    row.append(int(val))
                else:
                    row.append(0)
            board.append(row)
        return board

    def set_board(self, board):
        for i in range(self.size):
            for j in range(self.size):
                self.entries[i][j].delete(0, tk.END)
                if board[i][j] != 0:
                    self.entries[i][j].insert(0, str(board[i][j]))

    # ---------------- Features ----------------
    def check_cell(self, row, col):
        val = self.entries[row][col].get()
        if val.isdigit():
            num = int(val)
            board = self.get_board()
            board[row][col] = 0  # Temporarily remove for validation
            if not is_valid(board, row, col, num):
                self.flash_red(self.entries[row][col])

        self.check_solved()

    def flash_red(self, cell, count=0):
        if count >= 6:
            cell.config(bg='white')
            return
        cell.config(bg='red' if count %2 ==0 else 'white')
        self.root.after(100, lambda: self.flash_red(cell, count+1))

    def check_solved(self):
        board = self.get_board()
        if all(all(cell != 0 for cell in row) for row in board):
            if solve_sudoku([row[:] for row in board]):
                self.timer_running = False
                self.celebrate()

    def celebrate(self, count=0):
        if count > 50:
            return
        for i in range(self.size):
            for j in range(self.size):
                color = random.choice(self.colors)
                hex_color = "#%02x%02x%02x" % color
                self.entries[i][j].config(bg=hex_color)
        self.root.after(100, lambda: self.celebrate(count+1))

    def solve(self):
        board = self.get_board()
        if solve_sudoku(board):
            self.set_board(board)
            self.timer_running = False
            self.celebrate()
        else:
            messagebox.showinfo("Sudoku Solver", "No solution exists")

    def clear_board(self):
        for i in range(self.size):
            for j in range(self.size):
                self.entries[i][j].delete(0, tk.END)
                self.entries[i][j].config(bg='white')
        self.start_time = time.time()
        self.timer_running = True

    def generate(self):
        difficulty = self.diff_var.get()
        board = generate_puzzle(self.size, difficulty)
        self.set_board(board)
        self.start_time = time.time()
        self.timer_running = True

    def update_timer(self):
        if self.timer_running:
            elapsed = int(time.time() - self.start_time)
            minutes, seconds = divmod(elapsed, 60)
            self.timer_label.config(text=f"Time: {minutes:02}:{seconds:02}")
        self.root.after(1000, self.update_timer)

if __name__ == "__main__":
    root = tk.Tk()
    gui = SudokuGUI(root)
    root.mainloop()
