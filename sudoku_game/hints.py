# sudoku_game/hints.py
from copy import deepcopy
from typing import Optional, Tuple, List
from sudoku_game.validator import is_valid
from sudoku_game.solver import solve

def candidates_for_cell(board: List[List[int]], row: int, col: int) -> List[int]:
    if board[row][col] != 0:
        return []
    cands = []
    for n in range(1, 10):
        if is_valid(board, row, col, n):
            cands.append(n)
    return cands

def get_hint(board: List[List[int]], row: int, col: int) -> Optional[Tuple[int, str]]:
    if not (0 <= row < 9 and 0 <= col < 9):
        return None
    if board[row][col] != 0:
        return None

    cands = candidates_for_cell(board, row, col)
    if len(cands) == 1:
        return cands[0], f"Only candidate for ({row},{col}) is {cands[0]} (naked single)."

    b = deepcopy(board)
    if solve(b):
        return b[row][col], "From solved board (solver hint)."
    return None
