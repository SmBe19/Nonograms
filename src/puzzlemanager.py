import os
import subprocess
import tempfile
from typing import Tuple, Union, List

import time
from PIL import Image

from number_detection import detect_number
from solver import Nonogram, CellState


BORDER_COLOR = (26, 105, 199)
LINE_COLOR = (0, 0, 0)
BACKGROUND_COLOR = (255, 255, 255)
CROSS_COLOR = (216, 14, 12)
MARKED_COLOR = (0, 0, 0)


class PuzzleManager:

    wid: str
    window_name: str
    puzzle: Union[Nonogram, None]
    puzzle_box: Tuple[int, int, int, int]
    col_start: [int]
    col_end: [int]
    row_start: [int]
    row_end: [int]

    def __init__(self, window_name: str):
        self.wid = '0'
        self.window_name = window_name
        self.puzzle = None
        self.puzzle_box = (0, 0, 0, 0)
        self.col_start = []
        self.col_end = []
        self.row_start = []
        self.row_end = []

    def focus_window(self) -> None:
        res = subprocess.run(['xdotool', 'search', '--onlyvisible', '--limit', '1', '--sync', '--name', self.window_name], stdout=subprocess.PIPE)
        self.wid = res.stdout.decode('utf-8').strip()
        subprocess.run(['xdotool', 'windowactivate', '--sync', self.wid])

    def get_screenshot(self, destination: str, delay1: float = 0.2, delay2: float = 0.2) -> None:
        time.sleep(delay1)
        self.focus_window()
        self.move_mouse(0, 0)
        time.sleep(delay2)
        subprocess.run(['import', '-silent', '-window', self.wid, destination])

    def move_mouse(self, x: int, y: int) -> None:
        subprocess.run(['xdotool', 'mousemove', '--window', self.wid, str(x), str(y)])

    def mouse_click(self, x: int, y: int, button: int) -> None:
        subprocess.run(['xdotool', 'mousemove', '--window', self.wid, str(x), str(y), 'click', str(button)])

    def click_cell(self, x: int, y: int, button: int) -> None:
        center = self.get_cell_center_coords(x, y)
        self.mouse_click(center[0] + self.puzzle_box[0], center[1] + self.puzzle_box[1], button)

    def get_puzzle_box(self, im: Image) -> Tuple[int, int, int, int]:
        mid = im.size[0]//2
        top = -1
        bottom = -1
        left = -1
        right = -1
        # Find border
        for y in range(im.size[1]):
            if im.getpixel((mid, y)) == BORDER_COLOR:
                is_border = True
                for x in range(mid-5, mid+5):
                    if im.getpixel((x, y)) != BORDER_COLOR:
                        is_border = False
                if is_border:
                    top = y
                    break
        # Move to top line
        for y in range(top, im.size[1]):
            if im.getpixel((mid, y)) == LINE_COLOR:
                top = y
                break
        # Find right border
        for x in range(mid, im.size[0]):
            if im.getpixel((x, top)) != LINE_COLOR:
                right = x - 1
                break
        # Find bottom border
        for y in range(top, im.size[1]):
            if im.getpixel((right, y)) != LINE_COLOR:
                bottom = y - 1
                break
        # Find left border
        for x in range(mid, 0, -1):
            if im.getpixel((x, bottom)) != LINE_COLOR:
                left = x + 1
                break
        return left, top, right + 1, bottom + 1

    def get_cell_count(self, im: Image, dx: int, dy: int) -> Tuple[int, List[int], List[int]]:
        if dx > 0:
            value_choose = lambda x, y: x
        else:
            value_choose = lambda x, y: y
        starts = []
        ends = []
        cx = im.size[0] - 1
        cy = im.size[1] - 1
        while im.getpixel((cx, cy)) != BACKGROUND_COLOR:
            cx -= 1
            cy -= 1
        ends.append(value_choose(cx, cy))
        count = 0
        while cx > 0 and cy > 0:
            count += 1
            while cx > 0 and cy > 0 and im.getpixel((cx, cy)) == BACKGROUND_COLOR:
                cx -= dx
                cy -= dy
            starts.append(value_choose(cx + dx, cy + dy))
            while cx > 0 and cy > 0 and im.getpixel((cx, cy)) != BACKGROUND_COLOR:
                cx -= dx
                cy -= dy
            ends.append(value_choose(cx, cy))
        ends.pop()
        starts.reverse()
        ends.reverse()
        return count - 1, starts, ends

    def get_cell_center_coords(self, x: int, y: int) -> Tuple[int, int]:
        return ((self.col_start[x+1] + self.col_end[x+1]) // 2,
                (self.row_start[y+1] + self.row_end[y+1]) // 2)

    def get_cell_size(self, x: int, y: int) -> Tuple[int, int]:
        return self.col_end[x+1] - self.col_start[x+1], self.row_end[y+1] - self.row_start[y+1]

    def fill_cells(self, puzzle_region: Image) -> None:
        for y in range(self.puzzle.height):
            for x in range(self.puzzle.width):
                color = puzzle_region.getpixel(self.get_cell_center_coords(x, y))
                if color == MARKED_COLOR:
                    self.puzzle.puzzle[y][x].initial_state = CellState.MARKED
                elif color == CROSS_COLOR:
                    self.puzzle.puzzle[y][x].initial_state = CellState.BLOCKED
                else:
                    self.puzzle.puzzle[y][x].initial_state = CellState.FREE

    def read_hints(self, puzzle_region: Image) -> None:
        horizontal_hints_size = self.get_cell_size(-1, 0)
        vertical_hints_size = self.get_cell_size(0, -1)
        horizontal_hint_count = horizontal_hints_size[0] // self.get_cell_size(0, 0)[0]
        vertical_hint_count = vertical_hints_size[1] // self.get_cell_size(0, 0)[1]
        hint_width = horizontal_hints_size[0] / horizontal_hint_count
        hint_height = vertical_hints_size[1] / vertical_hint_count
        for y in range(self.puzzle.height):
            for x in range(horizontal_hint_count):
                region = puzzle_region.crop((self.col_start[0] + int(x * hint_width), self.row_start[y+1], self.col_start[0] + int((x + 1) * hint_width) + 1, self.row_end[y+1] + 1))
                number = detect_number(region)
                if number > 0:
                    self.puzzle.add_horizontal_hint(y, number)
        for x in range(self.puzzle.width):
            for y in range(vertical_hint_count):
                region = puzzle_region.crop((self.col_start[x+1], self.row_start[0] + int(y * hint_height), self.col_end[x+1] + 1, self.row_start[0] + int((y+1) * hint_height) + 1))
                number = detect_number(region)
                if number > 0:
                    self.puzzle.add_vertical_hint(x, number)

    def read_puzzle(self) -> None:
        with tempfile.TemporaryDirectory(prefix='Nonogram') as tempdir:
            screenshot = os.path.join(tempdir, 'screen.png')
            self.get_screenshot(screenshot)
            im = Image.open(screenshot)
        self.puzzle_box = self.get_puzzle_box(im)
        self.move_mouse(self.puzzle_box[2], self.puzzle_box[3])
        puzzle_region = im.crop(self.puzzle_box)
        width, self.col_start, self.col_end = self.get_cell_count(puzzle_region, 1, 0)
        height, self.row_start, self.row_end = self.get_cell_count(puzzle_region, 0, 1)
        self.puzzle = Nonogram(width, height)
        self.fill_cells(puzzle_region)
        self.read_hints(puzzle_region)

    def apply_puzzle(self) -> None:
        for y in range(self.puzzle.height):
            for x in range(self.puzzle.width):
                initial = self.puzzle.puzzle[y][x].initial_state
                state = self.puzzle.puzzle[y][x].state
                if initial != state:
                    if state == CellState.MARKED:
                        self.click_cell(x, y, 1)
                    elif state == CellState.BLOCKED:
                        self.click_cell(x, y, 3)
                    elif initial == CellState.MARKED:
                        self.click_cell(x, y, 1)
                    elif initial == CellState.BLOCKED:
                        self.click_cell(x, y, 3)
