import unittest
from pathlib import Path
from pysudoku.board import Board
from pysudoku.verifier import Status, Verifier

DATA = Path(__file__).parent / "data"

def verify(submission_file):
    puzzle = Board.from_file(DATA / "puzzle.txt")
    submission = Board.from_file(DATA / submission_file)
    return Verifier(puzzle, submission).verify()

class VerifierTests(unittest.TestCase):
    
    def test_sample_submission(self):
        report = verify("submission_sample.txt")
        self.assertEqual(report.status, Status.INVALID)
        self.assertEqual(report.problems, [
            "Row 9, Column 1: cell is empty.",
            "Row 2: number 8 appears in columns 3 and 9.",
            "Column 3: number 8 appears in rows 2 and 3.",
            "Box 1: number 8 appears at (2, 3) and (3, 3).",])
        
    def test_correct_solution(self):
        report = verify("solution_correct.txt")
        self.assertEqual(report.status, Status.VALID)
        self.assertEqual(report.problems, [])
        self.assertTrue(report.is_valid)

    def test_one_empty_cell_is_incomplete(self):
        report = verify("solution_incomplete.txt")
        self.assertEqual(report.status, Status.INCOMPLETE)
        self.assertEqual(report.problems, ["Row 1, Column 3: cell is empty."])

    def test_changed_given_comes_first(self):
        report = verify("solution_changed_given.txt")
        self.assertEqual(report.status, Status.INVALID)
        self.assertEqual(report.problems[0], "Row 1, Column 1: value 3 overwrites the given number 5.")
        # the 3 is now also a duplicate in row 1, column 1 and box 1
        self.assertEqual(len(report.problems), 4)

if __name__ == "__main__":
    unittest.main()