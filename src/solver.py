from enum import Enum
from typing import List, Any


class CellState(Enum):
    FREE = 1
    MARKED = 2
    BLOCKED = 3


class Cell:

    initial_state: CellState
    state: CellState
    width: int
    height: int

    def __init__(self):
        self.initial_state = CellState.FREE
        self.state = CellState.FREE
        self.width = 0
        self.height = 0

    def __str__(self):
        if self.state == CellState.MARKED:
            return 'X'
        if self.state == CellState.BLOCKED:
            return '#'
        return '.'


class Hint:

    value: int
    done: bool
    leftmost: int
    rightmost: int

    def __init__(self, value: int):
        self.value = value
        self.done = False
        self.leftmost = 0
        self.rightmost = 0

    def __repr__(self):
        return 'Hint <{} ({}-{})>'.format(self.value, self.leftmost, self.rightmost)


class Nonogram:

    width: int
    height: int
    puzzle: List[List[Cell]]
    horizontal: List[List[Hint]]
    vertical: List[List[Hint]]

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.puzzle = [[Cell() for _ in range(width)] for _ in range(height)]
        self.horizontal = [[] for _ in range(height)]
        self.vertical = [[] for _ in range(width)]

    def add_horizontal_hint(self, y: int, value: int) -> None:
        self.horizontal[y].append(Hint(value))

    def add_vertical_hint(self, x: int, value: int) -> None:
        self.vertical[x].append(Hint(value))

    def _init_solve(self) -> None:
        for y in range(self.height):
            for x in range(self.width):
                self.puzzle[y][x].state = self.puzzle[y][x].initial_state
        for row in self.horizontal:
            for hint in row:
                hint.leftmost = 0
                hint.rightmost = self.width - hint.value
        for col in self.vertical:
            for hint in col:
                hint.leftmost = 0
                hint.rightmost = self.height - hint.value

    def _update_one_mostness(self, hint_list_list: [[Hint]]) -> None:
        for row in hint_list_list:
            last_end = -1
            for hint in row:
                hint.leftmost = max(hint.leftmost, last_end + 1)
                last_end = hint.leftmost + hint.value
            last_end = self.width
            for hint in reversed(row):
                hint.rightmost = min(hint.rightmost, last_end - hint.value)
                last_end = hint.rightmost - 1

    def _update_mostness(self) -> None:
        self._update_one_mostness(self.horizontal)
        self._update_one_mostness(self.vertical)

    def _apply_mostness_overlap(self) -> None:
        for y, row in enumerate(self.horizontal):
            for hint in row:
                for x in range(hint.rightmost, hint.leftmost + hint.value):
                    self.puzzle[y][x].state = CellState.MARKED
        for x, col in enumerate(self.vertical):
            for hint in col:
                for y in range(hint.rightmost, hint.leftmost + hint.value):
                    self.puzzle[y][x].state = CellState.MARKED

    def _update_sizes(self) -> None:
        marked = []

        def finish():
            for mark in marked:
                mark.width = len(marked)
            marked.clear()
        for y in range(self.height):
            for x in range(self.width):
                if self.puzzle[y][x].state == CellState.MARKED:
                    marked.append(self.puzzle[y][x])
                else:
                    finish()
        finish()
        for x in range(self.width):
            for y in range(self.height):
                if self.puzzle[y][x].state == CellState.MARKED:
                    marked.append(self.puzzle[y][x])
                else:
                    finish()
        finish()

    def solve(self) -> None:
        self._init_solve()
        self._update_mostness()
        print(self.horizontal)
        print(self.vertical)
        self._apply_mostness_overlap()
        self._update_sizes()
