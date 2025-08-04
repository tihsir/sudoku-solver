import random
from copy import deepcopy
from sudoku.solver import solve

def generate_empty_board():
    return [[0 for _ in range(9)] for _ in range(9)]

def is_valid(board, row, col, num):
    for i in range(9):
        if board[row][i] == num or board[i][col] == num:
            return False

    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[start_row+i][start_col+j] == num:
                return False

    return True

def fill_board(board):
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                nums = list(range(1, 10))
                random.shuffle(nums)
                for num in nums:
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        if fill_board(board):
                            return True
                        board[row][col] = 0
                return False
    return True

def generate_full_board():
    board = generate_empty_board()
    fill_board(board)
    return board

def remove_cells(board, num_clues):
    puzzle = deepcopy(board)
    cells_to_remove = 81 - num_clues
    attempts = 0

    while cells_to_remove > 0 and attempts < 100:
        row, col = random.randint(0, 8), random.randint(0, 8)
        if puzzle[row][col] != 0:
            backup = puzzle[row][col]
            puzzle[row][col] = 0

            temp = deepcopy(puzzle)
            if not has_unique_solution(temp):
                puzzle[row][col] = backup
                attempts += 1
            else:
                cells_to_remove -= 1
    return puzzle

def has_unique_solution(board):
    solutions = []

    def solve_with_count(b):
        for r in range(9):
            for c in range(9):
                if b[r][c] == 0:
                    for n in range(1, 10):
                        if is_valid(b, r, c, n):
                            b[r][c] = n
                            solve_with_count(b)
                            b[r][c] = 0
                    return
        solutions.append(deepcopy(b))

    solve_with_count(deepcopy(board))
    return len(solutions) == 1

def generate_puzzle(difficulty='medium'):
    full = generate_full_board()
    clues = {'easy': 40, 'medium': 30, 'hard': 22}
    return remove_cells(full, clues.get(difficulty, 30))
