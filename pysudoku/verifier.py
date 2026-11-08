"""Grading a player's grid against the original puzzle."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from .board import SIZE, Board

class Status(Enum):
    VALID = "VALID SOLUTION"
    INCOMPLETE = "INCOMPLETE"
    INVALID = "INVALID SOLUTION"

@dataclass
class VerificationReport:
    """Result of a verification, ready for the CLI to print."""
    status: Status
    problems: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """True only for a complete, correct solution."""
        return self.status is Status.VALID

class Verifier:
    """Compares a submission with the puzzle it was meant to solve."""
    def __init__(self, puzzle: Board, submission: Board) -> None:
        self._puzzle = puzzle
        self._submission = submission

    def verify(self) -> VerificationReport:
        """Check the submission and report problems in a fixed order:
        changed givens, then empty cells, then duplicates.
        A grid that keeps every given, has no empty cell and no duplicate is
        correct by definition, so there is no need to compare with a solver.
        """
        changed: list[str] = []
        empty: list[str] = []

        for r in range(SIZE):
            for c in range(SIZE):
                original = self._puzzle.get(r, c)
                value = self._submission.get(r, c)
                where = f"Row {r + 1}, Column {c + 1}"

                if self._puzzle.is_given(r, c):
                    if value == 0:
                        changed.append(f"{where}: the given number {original} was erased.")
                    elif value != original:
                        changed.append(f"{where}: value {value} overwrites the given number {original}.")
                elif value == 0:
                    empty.append(f"{where}: cell is empty.")

        duplicates = self._submission.find_conflicts()

        if changed or duplicates:
            status = Status.INVALID
        elif empty:
            status = Status.INCOMPLETE
        else:
            status = Status.VALID

        return VerificationReport(status, changed + empty + duplicates) 
