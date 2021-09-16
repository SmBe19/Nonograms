from solver import Nonogram, CellState


def _print_puzzle(puzzle: Nonogram, col_width: int, hint_value, cell_value) -> None:
    horizontal_hint_count = max(map(len, puzzle.horizontal))
    vertical_hint_count = max(map(len, puzzle.vertical))
    horizontal_line = '+' + ('-' * col_width * horizontal_hint_count) + '+' + (('-' * col_width + '+') * puzzle.width)
    print(horizontal_line)
    for i in range(vertical_hint_count):
        line = '|' + (' ' * col_width * horizontal_hint_count) + '|'
        for x in range(puzzle.width):
            if i < len(puzzle.vertical[x]):
                value = ' {: 2} '.format(puzzle.vertical[x][i].value)
                if hint_value:
                    value += hint_value(puzzle.vertical[x][i])
                value += ' ' * (col_width - len(value))
                line += value + '|'
            else:
                line += ' ' * col_width + '|'
        print(line)
    print(horizontal_line)
    for y in range(puzzle.height):
        line = '|'
        for i in range(horizontal_hint_count):
            if i < len(puzzle.horizontal[y]):
                value = ' {: 2} '.format(puzzle.horizontal[y][i].value)
                if hint_value:
                    value += hint_value(puzzle.horizontal[y][i])
                value += ' ' * (col_width - len(value))
                line += value
            else:
                line += ' ' * col_width
        line += '|'
        for x in range(puzzle.width):
            value = ''
            if puzzle.puzzle[y][x].cell.state == CellState.MARKED:
                value = ' ## '
            elif puzzle.puzzle[y][x].cell.state == CellState.BLOCKED:
                value = ' __ '
            else:
                value = '    '
            if cell_value:
                value += cell_value(x, y, puzzle.puzzle[y][x].cell)
            value += ' ' * (col_width - len(value))
            line += value + '|'
        print(line)
    print(horizontal_line)


def print_puzzle_debug(puzzle: Nonogram) -> None:
    _print_puzzle(puzzle, 12, lambda hint: '{}-{}'.format(hint.leftmost, hint.rightmost), lambda x, y, cell: '{}-{}'.format(x, y))


def print_puzzle(puzzle: Nonogram) -> None:
    _print_puzzle(puzzle, 4, None, None)
