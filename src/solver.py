from enum import Enum
from typing import List, Any, Set, Tuple


class CellState(Enum):
    FREE = 1
    MARKED = 2
    BLOCKED = 3


class Hint:

    value: int
    leftmost: int
    rightmost: int

    def __init__(self, value: int):
        self.value = value
        self.leftmost = 0
        self.rightmost = 0

    def __repr__(self):
        return 'Hint <{} ({}-{})>'.format(self.value, self.leftmost, self.rightmost)


class Cell:

    initial_state: CellState
    state: CellState

    def __init__(self):
        self.initial_state = CellState.FREE
        self.state = CellState.FREE


class RowCell:

    cell: Cell
    left: int
    right: int
    possible_hints: Set[Hint]

    def __init__(self, cell: Cell):
        self.cell = cell
        self.left = 0
        self.right = 0
        self.possible_hints = set()


class Nonogram:

    width: int
    height: int
    puzzle: List[List[RowCell]]
    horizontal: List[List[Hint]]
    vertical: List[List[Hint]]
    solve_order: List[Tuple[int, int]]

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.puzzle = [[RowCell(Cell()) for _ in range(width)] for _ in range(height)]
        self.puzzle_flipped = [[RowCell(self.puzzle[y][x].cell) for y in range(height)] for x in range(width)]
        self.horizontal = [[] for _ in range(height)]
        self.vertical = [[] for _ in range(width)]
        self.solve_order = []

    def add_horizontal_hint(self, y: int, value: int) -> None:
        self.horizontal[y].append(Hint(value))

    def add_vertical_hint(self, x: int, value: int) -> None:
        self.vertical[x].append(Hint(value))

    def _add_solve_order(self, x: int, y: int):
        if (x, y) not in self.solve_order:
            self.solve_order.append((x, y))

    def _init_solve(self) -> None:
        for y in range(self.height):
            for x in range(self.width):
                self.puzzle[y][x].cell.state = self.puzzle[y][x].cell.initial_state
        for row in self.horizontal:
            for hint in row:
                hint.leftmost = 0
                hint.rightmost = self.width - hint.value
        for col in self.vertical:
            for hint in col:
                hint.leftmost = 0
                hint.rightmost = self.height - hint.value

    def _calc_mostness(self) -> None:
        def _calc_one_mostness(hint_list_list: [[Hint]]) -> None:
            for row in hint_list_list:
                last_end = -1
                for hint in row:
                    hint.leftmost = max(hint.leftmost, last_end + 1)
                    last_end = hint.leftmost + hint.value
                last_end = self.width
                for hint in reversed(row):
                    hint.rightmost = min(hint.rightmost, last_end - hint.value)
                    last_end = hint.rightmost - 1
        _calc_one_mostness(self.horizontal)
        _calc_one_mostness(self.vertical)

    def _apply_mostness_overlap(self) -> None:
        def _apply_one_mostness_overlap(hint_list_list: [[Hint]], puzzle: [[RowCell]]) -> None:
            for y, row in enumerate(hint_list_list):
                for hint in row:
                    for x in range(hint.rightmost, hint.leftmost + hint.value):
                        puzzle[y][x].cell.state = CellState.MARKED
                        self._add_solve_order(x, y)
        _apply_one_mostness_overlap(self.horizontal, self.puzzle)
        _apply_one_mostness_overlap(self.vertical, self.puzzle_flipped)

    def _update_sizes(self) -> None:
        marked = []

        def _finish():
            for i, mark in enumerate(marked):
                mark.left = i
                mark.right = len(marked) - i - 1
            marked.clear()

        def _update_one_sizes(puzzle: [[RowCell]]) -> None:
            last = None
            for row in puzzle:
                for cell in row:
                    if cell.cell.state == last:
                        marked.append(cell)
                    else:
                        _finish()
                        last = cell.cell.state
                        marked.append(cell)
                _finish()

        _update_one_sizes(self.puzzle)
        _update_one_sizes(self.puzzle_flipped)

    def _calc_possible_hints(self):
        def _calc_one_possible_hints(hint_list_list: [[Hint]], puzzle: [[RowCell]]) -> None:
            for y, row in enumerate(hint_list_list):
                for hint in row:
                    for x in range(hint.leftmost, hint.rightmost + hint.value):
                        puzzle[y][x].possible_hints.add(hint)
                first = True
                for x, cell in enumerate(puzzle[y]):
                    if cell.cell.state != CellState.MARKED:
                        first = True
                    if first and cell.cell.state == CellState.MARKED:
                        first = False
                        hints = cell.possible_hints
                        for xx in range(x - cell.left, x + cell.right + 1):
                            hints = hints & puzzle[y][xx].possible_hints
                        for xx in range(x - cell.left, x + cell.right + 1):
                            puzzle[y][xx].possible_hints.clear()
                            puzzle[y][xx].possible_hints.update(hints)
                for x, cell in enumerate(puzzle[y]):
                    if not cell.possible_hints:
                        cell.cell.state = CellState.BLOCKED
                        self._add_solve_order(x, y)
        for row in self.puzzle:
            for cell in row:
                cell.possible_hints.clear()
        for row in self.puzzle_flipped:
            for cell in row:
                cell.possible_hints.clear()
        _calc_one_possible_hints(self.horizontal, self.puzzle)
        _calc_one_possible_hints(self.vertical, self.puzzle_flipped)

    def _deduce_mostness(self) -> None:
        def _deduce_one_mostness(hint_list_list: [[Hint]], puzzle: [[RowCell]]) -> None:
            for y, row in enumerate(hint_list_list):
                def fits_ltr(x: int, value: int) -> bool:
                    if value <= 0:
                        return True
                    if x >= len(puzzle[y]):
                        return False
                    row_cell: RowCell = puzzle[y][x]
                    if row_cell.cell.state == CellState.BLOCKED:
                        return False
                    if row_cell.cell.state == CellState.MARKED:
                        if row_cell.right >= value:
                            return False
                        return fits_ltr(x + row_cell.right + 1, value - row_cell.right - 1)
                    if value <= row_cell.right + 1:
                        return True
                    return fits_ltr(x + row_cell.right + 1, value - row_cell.right - 1)
                for hint in row:
                    for x in range(hint.leftmost, hint.rightmost + hint.value):
                        if puzzle[y][x].cell.state == CellState.MARKED and len(puzzle[y][x].possible_hints) == 1 and hint in puzzle[y][x].possible_hints:
                            hint.leftmost = max(hint.leftmost, x - hint.value + 1)
                            hint.rightmost = min(hint.rightmost, x)
                    while hint.leftmost < len(puzzle[y]) and not fits_ltr(hint.leftmost, hint.value):
                        hint.leftmost += 1
                    while hint.rightmost > 0 and not fits_ltr(hint.rightmost, hint.value):
                        hint.rightmost -= 1

        _deduce_one_mostness(self.horizontal, self.puzzle)
        _deduce_one_mostness(self.vertical, self.puzzle_flipped)

    def _find_finished_cells(self) -> None:
        def _find_one_finished_cells(hint_hint_list: [[Hint]], puzzle: [[RowCell]]) -> None:
            for y, row in enumerate(hint_hint_list):
                for hint in row:
                    if hint.leftmost == hint.rightmost:
                        if hint.leftmost - 1 >= 0:
                            assert puzzle[y][hint.leftmost - 1].cell.state != CellState.MARKED
                            puzzle[y][hint.leftmost - 1].cell.state = CellState.BLOCKED
                            self._add_solve_order(hint.leftmost - 1, y)
                        if hint.rightmost + hint.value < len(puzzle[y]):
                            assert puzzle[y][hint.rightmost + hint.value].cell.state != CellState.MARKED
                            puzzle[y][hint.rightmost + hint.value].cell.state = CellState.BLOCKED
                            self._add_solve_order(hint.rightmost + hint.value, y)
                all_done = True
                for hint in row:
                    if hint.leftmost != hint.rightmost:
                        all_done = False
                        break
                if all_done:
                    for x, cell in enumerate(puzzle[y]):
                        if cell.cell.state != CellState.MARKED:
                            cell.cell.state = CellState.BLOCKED
                            self._add_solve_order(x, y)
        _find_one_finished_cells(self.horizontal, self.puzzle)
        _find_one_finished_cells(self.vertical, self.puzzle_flipped)

    def count_known_cells(self) -> int:
        return sum(1 for row in self.puzzle for c in row if c.cell.state != CellState.FREE)

    def solve(self) -> None:
        self._init_solve()
        self._calc_mostness()
        known = self.count_known_cells()
        counter = 3
        while True:
            self._update_sizes()
            self._calc_possible_hints()
            self._deduce_mostness()
            self._calc_mostness()
            self._apply_mostness_overlap()
            self._find_finished_cells()

            new_known = self.count_known_cells()
            if new_known == self.width * self.height:
                print('Solved completely!')
                break
            if new_known == known:
                counter -= 1
                if counter <= 0:
                    break
            else:
                counter = 3
            known = new_known

