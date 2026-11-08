"""Backtracking search for Sudoku."""

from __future__ import annotations

import random
import time
from .board import SIZE, Board, box_index
DIGITS = range(1, 10)

class Solver:
    """Solves a board with recursive backtracking.
    Three lists of sets (rows, cols, boxes) remember which digits are already
    used, so checking a candidate is a set lookup instead of a scan. With
    `use_mrv` on, the search always branches on the empty cell that has the
    fewest legal candidates left.
    The board passed in is never modified: every run starts from a fresh copy."""

    def __init__(self, board: Board, use_mrv: bool = True, rng: random.Random | None = None) -> None:
        board.validate()  # raises InvalidBoardError on duplicates
        self._board = board.copy()
        self._use_mrv = use_mrv
        self._rng = rng

        # filled by the last solve()/count_solutions() call
        self.calls = 0
        self.elapsed = 0.0 


    def solve(self) -> Board | None:
        """Return a solved copy of the board, or None if there is no solution."""
        found = self._run(limit=1)
        if not found:
            return None
        return Board(found[0], self._board.givens)

    def count_solutions(self, limit: int = 2) -> int:
        """Count solutions, but stop as soon as `limit` of them are found.

        With the default limit of 2 the answer means: 0 = no solution,
        1 = unique, 2 = more than one.
        """
        if limit < 1:
            raise ValueError("limit must be at least 1")
        return len(self._run(limit))

    def _run(self, limit: int) -> list[list[list[int]]]:
        self._load()
        self.calls = 0
        found: list[list[list[int]]] = []
        start = time.perf_counter()
        self._search(limit, found)
        self.elapsed = time.perf_counter() - start
        return found

    def _load(self) -> None:
        self._grid = self._board.grid
        self._rows: list[set[int]] = [set() for _ in range(SIZE)]
        self._cols: list[set[int]] = [set() for _ in range(SIZE)]
        self._boxes: list[set[int]] = [set() for _ in range(SIZE)]
        self._empty: list[tuple[int, int]] = []
        for r in range(SIZE):
            for c in range(SIZE):
                value = self._grid[r][c]
                if value:
                    self._rows[r].add(value)
                    self._cols[c].add(value)
                    self._boxes[box_index(r, c)].add(value)
                else:
                    self._empty.append((r, c))

    def _candidates(self, r: int, c: int) -> list[int]:
        used = self._rows[r] | self._cols[c] | self._boxes[box_index(r, c)]
        return [d for d in DIGITS if d not in used]

    def _next_cell(self) -> tuple[int, int, list[int]] | None:
        best = None
        for r, c in self._empty:
            if self._grid[r][c]:
                continue
            options = self._candidates(r, c)
            if not self._use_mrv:
                return r, c, options
            if best is None or len(options) < len(best[2]):
                best = (r, c, options)
                if len(options) <= 1:  # can't do better than this
                    break
        return best

    def _place(self, r: int, c: int, d: int) -> None:
        self._grid[r][c] = d
        self._rows[r].add(d)
        self._cols[c].add(d)
        self._boxes[box_index(r, c)].add(d)

    def _unplace(self, r: int, c: int, d: int) -> None:
        self._grid[r][c] = 0
        self._rows[r].discard(d)
        self._cols[c].discard(d)
        self._boxes[box_index(r, c)].discard(d)

    def _search(self, limit: int, found: list[list[list[int]]]) -> None:
        self.calls += 1
        cell = self._next_cell()
        if cell is None:
            # nothing left to fill: this is a full solution
            found.append([row[:] for row in self._grid])
            return 
        r, c, options = cell

        if self._rng is not None:
            self._rng.shuffle(options)

        for d in options:
            self._place(r, c, d)
            self._search(limit, found)
            self._unplace(r, c, d)  # backtrack
            if len(found) >= limit:
                return

    