from copy import deepcopy
from sudoku_game.validator import is_valid

def find_empty(board):
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                return r, c
    return None

def solve(board):
    empty = find_empty(board)
    if not empty:
        return True
    r, c = empty
    for i in range(1,10):
        if is_valid(board, r, c, i):
            board[r][c] = i
            if solve(board):
                return True
            board[r][c] = 0
    return False

def count_solutions(board, limit=2):
    """
    Return how many solutions exist, up to `limit`.
    Early-cuts as soon as count reaches `limit` (default 2).
    """
    b = deepcopy(board)
    count = 0

    def dfs():
        nonlocal count
        if count >= limit:
            return
        empty = find_empty(b)
        if not empty:
            count += 1
            return
        r, c = empty
        for n in range(1, 10):
            if is_valid(b, r, c, n):
                b[r][c] = n
                dfs()
                if count >= limit:
                    return
                b[r][c] = 0

    dfs()
    return count

def has_unique_solution(board):
    """Boolean convenience wrapper."""
    return count_solutions(board, limit=2) == 1