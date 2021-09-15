import os
import time
import pytesseract

from PIL import Image

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
WHITE = (255, 255, 255)
EMPTY_CUTOFF = 0.99

LOOKUP_100_PERCENT_ZOOM = [
    0,  # 0
    0.457,  # 1
    0.261,  # 2
    0.285,  # 3
    0.309,  # 4
    0.357,  # 5
    0.166,  # 6
    0.428,  # 7
    0.114,  # 8
    0,  # 9
]


def white_ratio(region: Image) -> float:
    white_pixels = 0
    for y in range(region.size[1]):
        for x in range(region.size[0]):
            if region.getpixel((x, y)) == WHITE:
                white_pixels += 1
    return white_pixels / (region.size[0] * region.size[1])


def is_empty(region: Image) -> bool:
    return white_ratio(region) >= EMPTY_CUTOFF


def cut_off_border(region: Image) -> Image:
    top = 0
    bottom = region.size[1]
    left = 0
    right = region.size[0]
    mid_x = right // 2
    mid_y = bottom // 2
    while top < bottom and region.getpixel((mid_x, top)) != WHITE:
        top += 1
    if top == bottom:
        return None
    while region.getpixel((mid_x, bottom - 1)) != WHITE:
        bottom -= 1
    while left < right and region.getpixel((left, mid_y)) != WHITE:
        left += 1
    if left == right:
        return None
    while region.getpixel((right - 1, mid_y)) != WHITE:
        right -= 1
    return region.crop((left, top, right, bottom))


def crop_content(region: Image) -> Image:
    top = 0
    bottom = region.size[1]
    left = 0
    right = region.size[0]

    def white_line(x: int, y: int, dx: int, dy: int):
        while x < region.size[0] and y < region.size[1]:
            if region.getpixel((x, y)) != WHITE:
                return False
            x += dx
            y += dy
        return True

    while white_line(0, top, 1, 0):
        top += 1
    while white_line(0, bottom - 1, 1, 0):
        bottom -= 1
    while white_line(left, 0, 0, 1):
        left += 1
    while white_line(right - 1, 0, 0, 1):
        right -= 1
    return region.crop((left, top, right, bottom))


def find_number_for_100_percent(region: Image) -> int:
    ratio = white_ratio(region)
    miv = 0
    for i, v in enumerate(LOOKUP_100_PERCENT_ZOOM):
        if abs(ratio - v) < abs(ratio - LOOKUP_100_PERCENT_ZOOM[miv]):
            miv = i
    return miv


def find_number_with_tesseract(region: Image) -> int:
    text = pytesseract.image_to_string(region, config='--psm 8').strip()
    if text.isdigit():
        return int(text)
    return 0


def detect_number(region: Image) -> int:
    # TODO try not to use tesseract
    region = cut_off_border(region)
    if region is None or is_empty(region):
        return 0
    # region = crop_content(region)
    # number = find_number_for_100_percent(region)
    number = find_number_with_tesseract(region)
    # region.save(os.path.join(DATA_PATH, 'region_{}_{}_{}.png'.format(number, white_ratio(region), time.time())))
    return number
