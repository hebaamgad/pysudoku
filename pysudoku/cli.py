"""Command-line interface. This is the only module that prints.
Exit codes: 0 success, 1 invalid/unsolvable board or failed verification,
2 bad arguments or missing file.
"""
from __future__ import annotations
import argparse
import sys
from .board import Board
from .exceptions import InvalidBoardFormatError
from .solver import Solver
from .verifier import Verifier

ANALYSIS = {
    0: "NO SOLUTION (the clues contradict each other).",
    1: "UNIQUE SOLUTION (exactly 1 solution exists).",
    2: "MULTIPLE SOLUTIONS (at least 2 solutions exist; one is shown above).",
}

def cmd_solve(args: argparse.Namespace) -> int:
    """Validate, solve and classify a puzzle."""
    print(f"[+] Loading puzzle from: {args.file}")
    board = Board.from_file(args.file)

    conflicts = board.find_conflicts()
    if conflicts:
        print("[+] Validating board configuration... FAILED")
        for message in conflicts:
            print(f"[!] {message}")
        return 1
    print("[+] Validating board configuration... OK")
    print("[+] Running Sudoku solver...")
    print()

    solver = Solver(board, use_mrv=not args.no_mrv)
    count = solver.count_solutions(limit=2)
    calls, elapsed = solver.calls, solver.elapsed  # saved before solve() runs a new search
    if count == 0:
        print(f"[+] Solution analysis: {ANALYSIS[0]}")
        return 1
    print("=== SOLUTION FOUND ===")
    print(solver.solve())
    print()
    print(f"[+] Solution analysis: {ANALYSIS[count]}")
    if args.stats:
        mode = "off" if args.no_mrv else "on"
        print(f"[+] Search stats: {calls} recursive calls in {elapsed * 1000:.2f} ms (MRV {mode}).")
    return 0

def cmd_verify(args: argparse.Namespace) -> int:
    """Grade a player's grid against the puzzle."""
    print(f"[+] Verifying submission: {args.submission} against puzzle: {args.puzzle}")
    print()
    puzzle = Board.from_file(args.puzzle)
    submission = Board.from_file(args.submission)
    report = Verifier(puzzle, submission).verify()

    print("=== VERIFICATION RESULT ===")
    print(f"Status: {report.status.value}")
    if report.problems:
        print(f"Problems found ({len(report.problems)}):")
        for problem in report.problems:
            print(f"  - {problem}")
    return 0 if report.is_valid else 1

def build_parser() -> argparse.ArgumentParser:
    """Create the argument parser with the solve and verify subcommands."""
    parser = argparse.ArgumentParser(
        prog="python -m pysudoku",
        description="Validate, solve and verify Sudoku puzzles.",)
    
    sub = parser.add_subparsers(dest="command", required=True, metavar="<command>")

    solve = sub.add_parser("solve", help="solve a puzzle and report if the solution is unique")
    solve.add_argument("--file", required=True, metavar="PATH", help="puzzle file to solve")
    solve.add_argument("--stats", action="store_true", help="print recursive calls and time taken")
    solve.add_argument("--no-mrv", action="store_true",
                       help="take empty cells in reading order instead of the most constrained one first")
    solve.set_defaults(handler=cmd_solve)

    verify = sub.add_parser("verify", help="grade a player's grid against the puzzle")
    verify.add_argument("--puzzle", required=True, metavar="PATH", help="the original puzzle")
    verify.add_argument("--submission", required=True, metavar="PATH", help="the player's grid")
    verify.set_defaults(handler=cmd_verify)

    return parser

def main(argv: list[str] | None = None) -> int:
    """Parse arguments, run the command and return the exit code."""
    args = build_parser().parse_args(argv)  # argparse exits with 2 on bad arguments
    try:
        return args.handler(args)
    except FileNotFoundError as error:
        print(f"[!] File not found: {error.filename}", file=sys.stderr)
        return 2
    except InvalidBoardFormatError as error:
        print(f"[!] Invalid board format: {error}", file=sys.stderr)
        return 1