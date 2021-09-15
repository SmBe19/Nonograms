#!/usr/bin/env python3

import argparse

from puzzlemanager import PuzzleManager


def main():
    parser = argparse.ArgumentParser(description='Solve Nonograms')
    parser.add_argument('--window-name', default='Nonograms - online puzzle game - Chromium')
    args = parser.parse_args()
    manager = PuzzleManager(args.window_name)
    manager.read_puzzle()
    manager.puzzle.solve()
    manager.apply_puzzle()


if __name__ == '__main__':
    main()
