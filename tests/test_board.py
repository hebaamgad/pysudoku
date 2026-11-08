import unittest
from pathlib import Path
from pysudoku.board import Board
from pysudoku.exceptions import InvalidBoardError, InvalidBoardFormatError

DATA = Path(__file__).parent / "data"
SAMPLE_ROW_1 = [5, 3, 0, 0, 7, 0, 0, 0, 0]

class ParsingTests(unittest.TestCase):
    def test_sample_file_parses(self):
        board = Board.from_file(DATA / "puzzle.txt")
        self.assertEqual(board.grid[0], SAMPLE_ROW_1)
        self.assertEqual(board.get(8, 8), 9)
        self.assertEqual(len(board.empty_cells()), 51)

    def test_compact_dotted_version_gives_same_grid(self):
        spaced = Board.from_file(DATA / "puzzle.txt")
        compact = Board.from_file(DATA / "puzzle_compact.txt")
        self.assertEqual(compact.grid, spaced.grid)

    def test_compact_with_dividers(self):
        text = (DATA / "puzzle_compact.txt").read_text()
        lines = [f"{l[:3]}|{l[3:6]}|{l[6:]}" for l in text.split()]
        lines.insert(3, "---+---+---")
        board = Board.from_string("\n".join(lines))
        self.assertEqual(board, Board.from_file(DATA / "puzzle.txt"))

    def test_eight_rows_is_a_format_error(self):
        with self.assertRaises(InvalidBoardFormatError) as error:
            Board.from_file(DATA / "eight_rows.txt")
        self.assertIn("8 rows", str(error.exception))

    def test_ten_rows_is_a_format_error(self):
        with self.assertRaises(InvalidBoardFormatError) as error:
             Board.from_string("\n".join(["000000000"] * 10))
        self.assertIn("10 rows", str(error.exception))
    
    def test_letter_is_a_format_error(self):
        with self.assertRaises(InvalidBoardFormatError) as error:
            Board.from_file(DATA / "letter_x.txt")
        self.assertIn("'x'", str(error.exception))

    def test_short_row_reports_row_number(self):
        lines = ["000000000"] * 9
        lines[3] = "00000000"
        with self.assertRaises(InvalidBoardFormatError) as error:
            Board.from_string("\n".join(lines))
        self.assertEqual(str(error.exception), "Row 4 has 8 cells, expected 9.")


    def test_ten_and_star_are_rejected(self):
        for bad in ("5 3 10 0 7 0 0 0 0", "5 3 * 0 7 0 0 0 0"):
            text = "\n".join([bad] + ["000000000"] * 8)
            with self.assertRaises(InvalidBoardFormatError):
                Board.from_string(text)

    def test_zero_is_not_a_duplicate(self):
        lines = ["000000000"] * 9
        board = Board.from_string("\n".join(lines))
        self.assertEqual(board.find_conflicts(), [])

    def test_missing_file_is_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            Board.from_file(DATA / "does_not_exist.txt")
    

    
class ValidationTests(unittest.TestCase):

    def test_duplicate_given_is_refused(self):
        board = Board.from_file(DATA / "duplicate_given.txt")
        self.assertEqual(board.find_conflicts(), [
            "Row 1: number 5 appears in columns 1 and 4.",
            "Box 2: number 5 appears at (1, 4) and (2, 6).",])

    def test_sample_has_no_conflicts(self):
        board = Board.from_file(DATA / "puzzle.txt")
        self.assertEqual(board.find_conflicts(), [])
    

if __name__ == "__main__":
    unittest.main()
     

    
