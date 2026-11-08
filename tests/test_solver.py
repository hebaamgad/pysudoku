import time
import unittest
from pathlib import Path
from pysudoku import Board, Solver
DATA = Path(__file__).parent / "data"

class SolverTests(unittest.TestCase):
    
    def test_sample_has_unique_solution(self):
        puzzle = Board.from_file(DATA / "puzzle.txt")
        solver = Solver(puzzle)
        self.assertEqual(solver.solve(), Board.from_file(DATA / "solution_correct.txt"))
        self.assertEqual(solver.count_solutions(), 1)
    def test_plain_backtracking_gives_same_answer(self):
        puzzle = Board.from_file(DATA / "puzzle.txt")
        with_mrv = Solver(puzzle).solve()
        without = Solver(puzzle, use_mrv=False).solve()
        self.assertEqual(with_mrv, without)

    def test_removing_two_givens_makes_it_ambiguous(self):
        board = Board.from_file(DATA / "multiple_solutions.txt")
        self.assertEqual(Solver(board).count_solutions(limit=2), 2)

    def test_valid_board_without_solution(self):
        board = Board.from_file(DATA / "no_solution.txt")
        self.assertEqual(board.find_conflicts(), [])
        solver = Solver(board)
        self.assertIsNone(solver.solve())
        self.assertEqual(solver.count_solutions(), 0)

    def test_empty_board_is_fast(self):
        board = Board.from_file(DATA / "empty_board.txt")
        start = time.perf_counter()
        count = Solver(board).count_solutions(limit=2)
        self.assertEqual(count, 2)
        self.assertLess(time.perf_counter() - start, 1.0)

    def test_solve_does_not_touch_the_original(self):
        board = Board.from_file(DATA / "puzzle.txt")
        before = board.grid
        solved = Solver(board).solve()
        self.assertTrue(solved.is_full())
        self.assertEqual(board.grid, before)
        self.assertEqual(len(board.empty_cells()), 51)

    def test_count_respects_the_limit(self):
        board = Board.empty()
        self.assertEqual(Solver(board).count_solutions(limit=5), 5)
        with self.assertRaises(ValueError):
            Solver(board).count_solutions(limit=0)

    def test_solution_keeps_the_givens(self):
        puzzle = Board.from_file(DATA / "puzzle.txt")
        solved = Solver(puzzle).solve()
        for r, c in puzzle.givens:
            self.assertEqual(solved.get(r, c), puzzle.get(r, c))
        self.assertEqual(solved.givens, puzzle.givens)



if __name__ == "__main__":
    unittest.main()
