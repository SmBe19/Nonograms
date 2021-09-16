import os
import time
import pytesseract

from PIL import Image

ROOT_PATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
OCR_PATH = os.path.join(ROOT_PATH, 'ocr')
DATA_PATH = os.path.join(ROOT_PATH, 'data')
WHITE = (255, 255, 255)
EMPTY_CUTOFF = 0.99


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
    return region.crop((left - 2, top - 2, right + 2, bottom + 2))


def init_tesseract() -> None:
    configs = [
        'load_system_dawg F',
        'load_freq_dawg F',
        'load_unambig_dawg F',
        'load_punc_dawg F',
        'load_bigram_dawg F',
        'load_number_dawg T',
        'user_words_file {}'.format(os.path.join(OCR_PATH, 'eng.user-words')),
    ]
    with open(os.path.join(OCR_PATH, 'eng.user-words'), 'w') as f:
        for i in range(1, 100):
            print(i, file=f)
    with open(os.path.join(OCR_PATH, 'config'), 'w') as f:
        for config in configs:
            print(config, file=f)


tesseract_fixes = {}


def find_number_with_tesseract(region: Image) -> int:
    text = pytesseract.image_to_string(region, config='--psm 8 "{}"'.format(os.path.join(OCR_PATH, 'config'))).strip()
    if text.isdigit():
        return int(text)
    if text in tesseract_fixes:
        return tesseract_fixes[text]
    # TODO teach Tesseract that it should only detect numbers
    print('Could not detect number, got:', text)
    save_region(region, 'not detect')
    region.show()
    value = input()
    if value.isdigit():
        tesseract_fixes[text] = int(value)
        return int(value)
    return 0


def detect_number(region: Image) -> int:
    region = cut_off_border(region)
    if region is None or is_empty(region):
        return 0
    region = crop_content(region)
    number = find_number_with_tesseract(region)
    return number


def save_region(region: Image, message: str) -> None:
    region.save(os.path.join(DATA_PATH, 'region_{}_{}.png'.format(time.time(), message)))
