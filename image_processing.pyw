import argparse
import inspect
import math
import os
import random
import sys

from PIL import Image
import pygame
from pygame.locals import QUIT


def get_size(data):
    assert len(data) > 0 and len(data[0]) > 0, """
        len(data) > 0 and len(data[0]) > 0 are required.)"""
    width = len(data)
    height = len(data[0])
    return (width, height)


def invert(r, g, b):
    MASK = 0xff
    return (r ^ MASK, g ^ MASK, b ^ MASK)


def negative(surface, data):
    width, height = get_size(data)
    for x in range(width):
        for y in range(height):
            rgb = data[x][y]
            r, g, b, _ = surface.unmap_rgb(rgb)
            r_inv, g_inv, b_inv = invert(r, g, b)
            data[x][y] = (r_inv, g_inv, b_inv)


def to_gray(r, g, b):
    R_WEIGHT = 0.299
    G_WEIGHT = 0.587
    B_WEIGHT = 0.114
    return math.floor(r * R_WEIGHT + g * G_WEIGHT + b * B_WEIGHT)


def grayscale(surface, data):
    width, height = get_size(data)
    for x in range(width):
        for y in range(height):
            rgb = data[x][y]
            r, g, b, _ = surface.unmap_rgb(rgb)
            gray = to_gray(r, g, b)
            data[x][y] = (gray, gray, gray)


def noise(surface, data):
    RGB_MAX = 255
    RGB_NOISE_MIN = -127
    RGB_NOISE_MAX = 127

    width, height = get_size(data)

    for x in range(width):
        for y in range(height):
            rgb = data[x][y]
            rand = random.randint(RGB_NOISE_MIN, RGB_NOISE_MAX)
            r, g, b, _ = surface.unmap_rgb(rgb)
            r = max(0, min(RGB_MAX, r + rand))
            g = max(0, min(RGB_MAX, g + rand))
            b = max(0, min(RGB_MAX, b + rand))
            data[x][y] = (r, g, b)


def brightness(surface, data):
    BRIGHTNESS = 1.5
    RGB_MAX = 255

    width, height = get_size(data)

    for x in range(width):
        for y in range(height):
            rgb = data[x][y]
            r, g, b, _ = surface.unmap_rgb(rgb)
            r = max(0, min(RGB_MAX, int(r * BRIGHTNESS)))
            g = max(0, min(RGB_MAX, int(g * BRIGHTNESS)))
            b = max(0, min(RGB_MAX, int(b * BRIGHTNESS)))
            data[x][y] = (r, g, b)


def sin_curve(surface, data, data_conv):
    WAVES = 4
    RADIUS = 10
    WAVE_FREQ = (WAVES * math.pi * 2) / len(data[0])

    width, height = get_size(data)

    for x in range(width):
        y_offset = math.floor(math.sin(x * WAVE_FREQ) * RADIUS)
        for y in range(height):
            if 0 <= y + y_offset < height:
                rgb = data[x][y + y_offset]

                r, g, b, _ = surface.unmap_rgb(rgb)
                data_conv[x][y] = (r, g, b)


def wave(surface, data, data_conv):
    AMP = 10
    WAVES = 8

    step = (WAVES * math.pi * 2) / len(data)
    radius = 0
    width, height = get_size(data)

    for y in range(height):
        radius += step
        y_offset = max(0, min(height - 1,
                              math.floor(math.cos(radius) * AMP + y)))
        for x in range(width):
            rgb = data[x][y_offset]
            r, g, b, _ = surface.unmap_rgb(rgb)
            data_conv[x][y] = (r, g, b)


def edge(surface, data):
    INTENSITY = 10
    RGB_MAX = 255

    width, height = get_size(data)

    for y in range(1, height):
        for x in range(1, width):
            rgb_left = data[x - 1][y]
            rgb_top = data[x][y - 1]
            rgb = data[x][y]

            r_left, g_left, b_left, _ = surface.unmap_rgb(rgb_left)
            r_top, g_top, b_top, _ = surface.unmap_rgb(rgb_top)
            r, g, b, _ = surface.unmap_rgb(rgb)

            r = min((abs(r_left - r) + abs(r_top - r)) * INTENSITY, RGB_MAX)
            g = min((abs(g_left - g) + abs(g_top - g)) * INTENSITY, RGB_MAX)
            b = min((abs(b_left - b) + abs(b_top - b)) * INTENSITY, RGB_MAX)
            data[x][y] = (r, g, b)


def emboss(surface, data, data_conv):
    RGB_MAX = 255
    R_BG = 128
    G_BG = 128
    B_BG = 128
    POWER = 3

    width, height = get_size(data)

    for y in range(height):
        for x in range(1, width):
            rgb_left = data[x - 1][y]
            rgb = data[x][y]

            r_left, g_left, b_left, _ = surface.unmap_rgb(rgb_left)
            r, g, b, _ = surface.unmap_rgb(rgb)

            r = min(max(R_BG + math.floor((r - r_left) * POWER), 0), RGB_MAX)
            g = min(max(G_BG + math.floor((g - g_left) * POWER), 0), RGB_MAX)
            b = min(max(B_BG + math.floor((b - b_left) * POWER), 0), RGB_MAX)
            data_conv[x][y] = (r, g, b)


def blur(surface, data, data_conv):
    POWER = 5

    width, height = get_size(data)

    for y in range(height):
        for x in range(width):
            r_total, g_total, b_total = 0, 0, 0
            colors = 0

            for y_diff in range(-POWER, POWER + 1):
                for x_diff in range(-POWER, POWER + 1):
                    (x_pos, y_pos) = (x + x_diff, y + y_diff)
                    if 0 <= x_pos < width and 0 <= y_pos < height:
                        rgb = data[x_pos][y_pos]
                        r, g, b, _ = surface.unmap_rgb(rgb)

                        r_total += r
                        g_total += g
                        b_total += b
                        colors += 1
            r = int(r_total / colors)
            g = int(g_total / colors)
            b = int(b_total / colors)
            data_conv[x][y] = (r, g, b)


def fill(surface, data, data_conv, x, y, x_step, y_step):
    r_total, g_total, b_total = 0, 0, 0
    for y_offset in range(y, y + y_step):
        for x_offset in range(x, x + x_step):
            rgb = data[x_offset][y_offset]
            r, g, b, _ = surface.unmap_rgb(rgb)
            r_total += r
            g_total += g
            b_total += b
    r = int(r_total / (x_step * y_step))
    g = int(g_total / (x_step * y_step))
    b = int(b_total / (x_step * y_step))
    for y_offset in range(y, y + y_step):
        for x_offset in range(x, x + x_step):
            data_conv[x_offset][y_offset] = (r, g, b)


def mosaic(surface, data, data_conv):
    width, height = get_size(data)
    step = min(width, height) // 4
    width_div_step = width // step
    height_div_step = height // step
    width_mod_step = width % step
    height_mod_step = height % step

    for y in range(0, height - height_mod_step, step):
        for x in range(0, width - width_mod_step, step):
            fill(surface, data, data_conv, x, y, step, step)
    if width_mod_step:
        for y in range(0, height, step):
            fill(surface, data, data_conv,
                 step * width_div_step, y, width_mod_step, step)
    if height_mod_step:
        for x in range(0, width, step):
            fill(surface, data, data_conv,
                 x, step * height_div_step, step, height_mod_step)
    if width_mod_step and height_mod_step:
        fill(surface, data, data_conv,
             step * width_div_step, step * height_div_step,
             width_div_step, height_div_step)


def ripple(surface, data, data_conv):
    WAVES = 25
    AMP = math.radians(5)

    width, height = get_size(data)
    distance = math.hypot(width, height)
    scale = math.pi * 2 * WAVES / distance

    for y in range(height):
        for x in range(width):
            x_pos = x - width // 2
            y_pos = y - height // 2
            angle = math.sin(math.hypot(x_pos, y_pos) * scale) * AMP
            sin_v, cos_v = math.sin(angle), math.cos(angle)

            x_src = math.floor((x_pos * cos_v - y_pos * sin_v) + width // 2)
            y_src = math.floor((y_pos * cos_v + x_pos * sin_v) + height // 2)

            if 0 <= x_src < width and 0 <= y_src < height:
                rgb = data[x_src][y_src]
                r, g, b, _ = surface.unmap_rgb(rgb)
                data_conv[x][y] = (r, g, b)


def convert(surface, func, path):
    args = inspect.getfullargspec(func)[0]
    src = pygame.image.load(path).convert()
    data = pygame.PixelArray(src)

    if len(args) == 2:
        func(surface, data)
        del data
        return src
    elif len(args) == 3:
        src_conv = pygame.Surface((len(data), len(data[0])), 0, surface)
        data_conv = pygame.PixelArray(src_conv)
        func(surface, data, data_conv)
        del data
        del data_conv
        return src_conv


def get_image_size(path):
    with Image.open(path) as img:
        width = img.size[0]
        height = img.size[1]
    return (width, height)


def draw(surface, src, width, height, row, column):
    for i in range(row):
        y_top = height * i
        for j in range(column):
            x_left = width * j
            surface.blit(src[i * column + j], (x_left, y_top))


def loop(fpsclock, fps):
    pygame.display.update()
    fpsclock.tick(fps)


def quit():
    pygame.quit()
    sys.exit()


def main():
    parser = argparse.ArgumentParser(description="""
                                     Examples about image processing""")
    parser.add_argument("path", type=str, help="path of image file")
    args = parser.parse_args()
    path = os.path.abspath(args.path)
    assert os.path.exists(path), "File not found."

    try:
        width, height = get_image_size(path)
    except OSError:
        print("Can not open this file.")
        return

    CONVERT = [negative, grayscale, noise, brightness,
               sin_curve, wave, edge, emboss, blur,
               mosaic, ripple]
    ROW = 3
    COLUMN = 4
    FPS = 5

    pygame.init()
    surface = pygame.display.set_mode((width * COLUMN, height * ROW))
    fpsclock = pygame.time.Clock()
    src = []
    src.append(pygame.image.load(path).convert())

    for func in CONVERT:
        src.append(convert(surface, func, path))
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                quit()
        draw(surface, src, width, height, ROW, COLUMN)
        loop(fpsclock, FPS)


if __name__ == "__main__":
    main()
