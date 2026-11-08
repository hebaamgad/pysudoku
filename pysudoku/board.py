"""The Board class: reading a grid from text, checking it and printing it."""

from __future__ import annotations
from pathlib import Path
from .exceptions import InvalidBoardError, InvalidBoardFormatError, SudokuError

SIZE = 9
DIVIDERS = "|-+"
DIVIDER_LINE = "------+-------+------"
Cell = tuple[int, int]

def box_index(row:int, col:int) ->int:
    """Return the 0-based box number of a cell (boxes go left to right, top to bottom)."""
    return (row//3)*3 + col//3

def box_cells(box:int) ->list[Cell]:
    """Return the nine cells of a box, row by row."""
    top, left = box // 3 * 3, box % 3 * 3
    return [(r,c) for r in range(top,top+3) for c in range(left,left+3)]

def _join(items:list[str]) -> str:
    if len(items)==1:
        return items[0]
    return ", ".join(items[:-1]) + " and " + items[-1]

class Board:
    """A 9x9 Sudoku grid stored as list[list[int]], with 0 for an empty cell.
    The board also remembers which cells were *given* (part of the original
    puzzle), so the game and the verifier can tell them apart from the
    player's own numbers."""

    def __init__(self,grid: list[list[int]],givens: set[Cell] |frozenset[Cell] | None=None) -> None:
        if len(grid) != SIZE or any(len(row)!= SIZE for row in grid):
            raise InvalidBoardFormatError("A board needs exactly 9 rows of 9 cells.")
        for row in grid:
            for value in row:
                if not isinstance(value,int) or not 0<= value <=9:
                    raise InvalidBoardFormatError(f"Invalid cell value: {value!r}.") 

        self._grid =[list(row) for row in grid]
        if givens is None:
            givens={(r,c) for r in range(SIZE) for c in range(SIZE) if self._grid[r][c]}
        self._givens = frozenset(givens)
    @classmethod
    def from_string(cls, text: str) -> Board:
        """Parse a board from text.
        Accepted: digits with or without spaces, 0 or '.' for empty cells,
        the divider characters | - + anywhere, blank lines and '#' comments."""
        rows: list[list[int]] = []
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            for ch in DIVIDERS:
                line = line.replace(ch, " ")
            if not line.strip():
                # a line made only of dividers,  ------+-------+------
                continue
            row_no = len(rows) + 1
            cells = []
            for ch in "".join(line.split()):
                if ch == ".":
                    cells.append(0)
                elif ch.isdigit() and ch.isascii():
                    cells.append(int(ch))
                else:
                    raise InvalidBoardFormatError(f"Row {row_no} contains an invalid character {ch!r}.")
            if len(cells) != SIZE:
                raise InvalidBoardFormatError(f"Row {row_no} has {len(cells)} cells, expected 9.")
            rows.append(cells)
        if len(rows) != SIZE:
            raise InvalidBoardFormatError(f"Found {len(rows)} rows, expected 9.")
        return cls(rows)

    @classmethod
    def from_file(cls,path: str | Path) -> Board:
        """Read and parse a board file. A missing file raises FileNotFoundError."""
        text=Path(path).read_text(encoding="utf-8")
        return cls.from_string(text)

    @classmethod
    def empty(cls) -> Board:
        """Return a board with every cell empty."""
        return cls([[0] * SIZE for _ in range(SIZE)])
    @property
    def grid(self) -> list[list[int]]:
        """A copy of the grid. Changing it does not change the board."""
        return [row[:] for row in self._grid]
    @property
    def givens(self) ->frozenset[Cell]:
        """The cells that belong to the original puzzle."""
        return self._givens
    def get(self,row:int,col:int) -> int:
        """Value at (row, col), 0-based. 0 means empty."""
        return self._grid[row][col]
    def is_given(self,row:int,col:int) -> bool:
        """True if the cell was filled in the original puzzle."""
        return (row, col) in self._givens
    def empty_cells(self) -> list[Cell]:
        """All (row, col) pairs that are still 0, in reading order."""
        return [(r, c) for r in range(SIZE) for c in range(SIZE) if self._grid[r][c] == 0]
    def is_full(self) -> bool:
        """True when no cell is empty."""
        return not self.empty_cells()

    def _repeats(self, cells: list[Cell]) -> list[tuple[int, list[Cell]]]:
        seen: dict[int, list[Cell]] = {}
        for r, c in cells:
            value = self._grid[r][c]
            if value:
                seen.setdefault(value, []).append((r, c))
        return [(d, spots) for d, spots in sorted(seen.items()) if len(spots) > 1]

    def find_conflicts(self) -> list[str]:
        """List every repeated digit in a row, column or box.
        Messages use 1-based positions. An empty list means the board is valid.
        Rows come first, then columns, then boxes."""
        problems: list[str] = []

        for r in range(SIZE):
            for digit, cells in self._repeats([(r, c) for c in range(SIZE)]):
                cols = _join([str(c + 1) for _, c in cells])
                problems.append(f"Row {r + 1}: number {digit} appears in columns {cols}.")

        for c in range(SIZE):
            for digit, cells in self._repeats([(r, c) for r in range(SIZE)]):
                rows = _join([str(r + 1) for r, _ in cells])
                problems.append(f"Column {c + 1}: number {digit} appears in rows {rows}.")

        for b in range(SIZE):
            for digit, cells in self._repeats(box_cells(b)):
                spots = _join([f"({r + 1}, {c + 1})" for r, c in cells])
                problems.append(f"Box {b + 1}: number {digit} appears at {spots}.")

        return problems

    def validate(self) -> None:
        """Raise InvalidBoardError if the board breaks a Sudoku rule."""
        conflicts = self.find_conflicts()
        if conflicts:
            raise InvalidBoardError(conflicts)

    def set(self, row: int, col: int, value: int) -> None:
        """Write a value (0 clears) into a non-given cell."""
        if self.is_given(row, col):
            raise SudokuError(f"Row {row + 1}, Column {col + 1} is part of the puzzle and can't be changed.")
        if not 0 <= value <= 9:
            raise SudokuError(f"{value} is not a valid Sudoku value.")
        self._grid[row][col] = value

    def copy(self) -> Board:
        """An independent copy, givens included."""
        return Board(self._grid, self._givens)

    def __str__(self) -> str:
        """Return the board as text with dividers."""
        lines = []
        for r in range(SIZE):
            if r in (3, 6):
                lines.append(DIVIDER_LINE)
            blocks = []
            for start in (0, 3, 6):
                blocks.append(" ".join(str(v) if v else "." for v in self._grid[r][start:start + 3]))
            lines.append(" | ".join(blocks))
        return "\n".join(lines)
    def __repr__(self) -> str:
        """Short description, handy when debugging."""
        filled = SIZE * SIZE - len(self.empty_cells())
        return f"<Board {filled}/81 filled>"

    def __eq__(self, other: object) -> bool:
        """Two boards are equal when their grids are equal (givens are ignored)."""
        if not isinstance(other, Board):
            return NotImplemented
        return self._grid == other._grid



    
        
        

    




      
        







    
        
    
