# PySudoku

AA small Sudoku engine written in Python It reads puzzles from text files,
checks them against the rules, solves them with backtracking, tells you whether the
solution is unique, and grades a player's answer cell by cell.

Only the standard library is used (Python 3.10 or newer).

## Running the Project

All commands should be run from the project root.

### Solve a puzzle

python -m pysudoku solve --file data/puzzle.txt

### Solve with search statistics

python -m pysudoku solve --file data/puzzle.txt --stats

### Disable MRV optimization

python -m pysudoku solve --file data/puzzle.txt --stats --no-mrv

### Verify a player's solution

python -m pysudoku verify --puzzle tests/data/sample.txt --submission tests/data/solution_correct.txt

For more information about available commands and options, run:

```bash
python -m pysudoku --help
python -m pysudoku solve --help
python -m pysudoku verify --help

## Running the tests

```bash
python -m unittest discover -s tests -v

## File format

A board is 9 lines of 9 cells.

- Empty cells are `0` or `.`
- Spaces between digits are optional: `530070000` and `5 3 0 0 7 0 0 0 0` are the same row
- `|`, `-` and `+` are ignored wherever they appear, and lines made only of them are skipped

So both of these are the same puzzle:

```
# Sample puzzle (0 = empty)
5 3 0 | 0 7 0 | 0 0 0
6 0 0 | 1 9 5 | 0 0 0
0 9 8 | 0 0 0 | 0 6 0
------+-------+------
8 0 0 | 0 6 0 | 0 0 3
...
```

```
53..7....
6..195...
.98....6.
8...6...3
...
```
Anything else (fewer or more than 9 rows, a row that isn't 9 cells, a letter, `*`,
`10`...) raises `InvalidBoardFormatError` with the row number, for example
`Row 4 has 8 cells, expected 9.`

## How it works

Board: Manages the Sudoku grid, parses puzzle files, tracks original given cells, and detects conflicts in rows, columns, and 3×3 boxes.

Solver: Solves puzzles using recursive Backtracking with optional MRV optimization. It works on a copy of the original grid to keep the input board unchanged.

Verifier: Checks player submissions against the original puzzle, detecting modified given numbers, empty cells, and duplicates.

CLI: Provides commands to solve puzzles, display search statistics, and verify solutions

pysudoku-project/
│
├── pysudoku/
│   ├── __init__.py
│   ├── __main__.py
│   ├── board.py
│   ├── solver.py
│   ├── verifier.py
│   ├── exceptions.py
│   └── cli.py
│
├── data/
│   └── puzzle.txt
│
├── tests/
│   ├── test_board.py
│   ├── test_solver.py
│   ├── test_verifier.py
│   └── data/
│
└── README.md

