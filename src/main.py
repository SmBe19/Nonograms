#!/usr/bin/env python3

import argparse

from printer import print_puzzle, print_puzzle_debug
from puzzlemanager import PuzzleManager


def main():
    parser = argparse.ArgumentParser(description='Solve Nonograms')
    parser.add_argument('--window-name', default='Nonograms - online puzzle game - Chromium')
    parser.add_argument('--skip-crosses', '-c', action='store_true', help='do not add crosses in the solution')
    parser.add_argument('--solve-order', '-s', action='store_true', help='apply the solution in the order in which it was found')
    parser.add_argument('--print-read', '-r', action='store_true', help='print the puzzle before solving')
    parser.add_argument('--print', '-p', action='store_true', help='print the solved puzzle')
    parser.add_argument('--print-debug', '-d', action='store_true', help='print debug information')
    args = parser.parse_args()
    manager = PuzzleManager(args.window_name)
    manager.read_puzzle()
    if args.print_read:
        print_puzzle(manager.puzzle)
    try:
        manager.puzzle.solve()
        if args.print:
            print_puzzle(manager.puzzle)
        if args.print_debug:
            print_puzzle_debug(manager.puzzle)
        if args.solve_order:
            manager.apply_puzzle_in_solve_order(not args.skip_crosses)
        else:
            manager.apply_puzzle(not args.skip_crosses)
    finally:
        manager.move_mouse(manager.puzzle_box[0], manager.puzzle_box[1])


if __name__ == '__main__':
    main()
