class SudokuError(Exception):
    """Base class for all Sudoku errors"""

class InvalidBoardFormatError(SudokuError):
    """The file content is not a 9x9 grid of valid cells"""

class InvalidBoardError(SudokuError):
    """The starting board repeats a digit in a row, column or box"""

    def __init__(self, conflicts: list[str]) -> None:
        super().__init__("Board has conflicts")
        self.conflicts = conflicts