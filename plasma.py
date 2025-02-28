
#!/opt/homebrew/bin/python3

import math
import random
import colorsys

# Constants
UPDATE_PIXEL_COUNT = 12
WIDTH, HEIGHT = 16, 16  
SCALE = 30              
FPS = 30
UPDATE_DELAY = math.floor(1000 / FPS)

# Data structures
plasma_pixels = [[[0, 0, 0] for _ in range(WIDTH)] for _ in range(HEIGHT)]
error_values = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
top_error_positions = [i for i in range(256)]
display_pixels = [[[0, 0, 0] for _ in range(WIDTH)] for _ in range(HEIGHT)]

# ============================== #
#     PURE FUNCTIONS (IMPORTABLE)
# ============================== #
from datetime import datetime

# 3x5 pixel representations of digits 0-9
DIGIT_MAP = {
    '0': [
        "###",
        "# #",
        "# #",
        "# #",
        "###"
    ],
    '1': [
        " # ",
        "## ",
        " # ",
        " # ",
        "###"
    ],
    '2': [
        "###",
        "  #",
        "###",
        "#  ",
        "###"
    ],
    '3': [
        "###",
        "  #",
        "###",
        "  #",
        "###"
    ],
    '4': [
        "# #",
        "# #",
        "###",
        "  #",
        "  #"
    ],
    '5': [
        "###",
        "#  ",
        "###",
        "  #",
        "###"
    ],
    '6': [
        "###",
        "#  ",
        "###",
        "# #",
        "###"
    ],
    '7': [
        "###",
        "  #",
        "  #",
        "  #",
        "  #"
    ],
    '8': [
        "###",
        "# #",
        "###",
        "# #",
        "###"
    ],
    '9': [
        "###",
        "# #",
        "###",
        "  #",
        "###"
    ]
}

def draw_alpha_pixel(x, y, color, alpha):
    plasma_pixels[y][x] = [
        (1 - alpha) * plasma_pixels[y][x][j] + alpha * color[j] for j in range(3)
    ]

def update_clock():
    now = datetime.now()
    time_string = now.strftime("%H%M")
    start_x, start_y = 0, 2  # Position of the clock on the grid
    color = [0, 0, 0]
    alpha = 0.75
    
    for i, digit in enumerate(time_string):
        digit_pattern = DIGIT_MAP[digit]
        x_offset = start_x + (i * 4) + (0 if i>1 else 1)  # Space between digits
        y_offset = start_y + (6 if i>1 else 0)  # Space between digits
        
        for dy, row in enumerate(digit_pattern):
            for dx, pixel in enumerate(row):
                if pixel == "#":
                    #plasma_pixels[y_offset + dy][x_offset + dx] = [0, 0, 0]  
                    draw_alpha_pixel(x_offset + dx, y_offset + dy, color, alpha)

    progress_x = start_x + int((WIDTH-1)*(now.second / 59.0))
    progress_y = HEIGHT - 1
    draw_alpha_pixel(progress_x, progress_y, color, alpha)


def hsv_to_hex(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return '#%02x%02x%02x' % (int(r * 255), int(g * 255), int(b * 255))

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))

def update_plasma(t):
    for y in range(HEIGHT):
        for x in range(WIDTH):
            color_value = (
                math.sin(0.04*(-x + t)) +
                math.sin(0.05*(y - t)) +
                math.sin(0.06*(-(x + 0.5*y) + t)) +
                math.sin(0.07*((0.5*x + y) - t)) 
            )
            normalized = (color_value + 4) / 8
            hue = (normalized + t * 0.05) % 1.0
            r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
            pixel = plasma_pixels[y][x]
            pixel[0] = r
            pixel[1] = g
            pixel[2] = b

def partial_sort_error_positions():
    for i in range(len(top_error_positions) - 1):
        idx_a = top_error_positions[i]
        idx_b = top_error_positions[i + 1]
        y_a, x_a = divmod(idx_a, WIDTH)
        y_b, x_b = divmod(idx_b, WIDTH)
        if error_values[y_a][x_a] < error_values[y_b][x_b]:
            top_error_positions[i], top_error_positions[i + 1] = top_error_positions[i + 1], top_error_positions[i]

def update_error():
    for y in range(HEIGHT):
        for x in range(WIDTH):
            plasma_pixel = plasma_pixels[y][x]
            display_pixel = display_pixels[y][x]
            error_values[y][x] += sum(abs(plasma_pixel[i] - display_pixel[i]) for i in range(3)) + random.randint(0,10)
    partial_sort_error_positions()
    partial_sort_error_positions()

def update_display():
    for i in range(UPDATE_PIXEL_COUNT):
        p = top_error_positions[i]
        y, x = divmod(p, WIDTH)
        display_pixels[y][x][:] = plasma_pixels[y][x]
        error_values[y][x] = 0
    top_error_positions[:] = top_error_positions[UPDATE_PIXEL_COUNT:] + top_error_positions[:UPDATE_PIXEL_COUNT]

def max_error_value():
    return max(max(row) for row in error_values) + 1

# ===================================== #
#    TKINTER-DEPENDENT (NOT IMPORTABLE)
# ===================================== #

def main():
    import tkinter as tk

    root = tk.Tk()
    root.title("Plasmaeffekt med Tkinter")

    canvas = tk.Canvas(root, width=WIDTH * SCALE * 3, height=HEIGHT * SCALE, bg='black')
    canvas.pack()

    canvas_pixels = [[None for _ in range(WIDTH * 3)] for _ in range(HEIGHT)]
    for y in range(HEIGHT):
        for x in range(WIDTH * 3):
            rect = canvas.create_rectangle(
                x * SCALE, y * SCALE, (x + 1) * SCALE - 1, (y + 1) * SCALE - 1,
                outline='', fill='#000000'
            )
            canvas_pixels[y][x] = rect

    def show_plasma():
        for y in range(HEIGHT):
            for x in range(WIDTH):
                pixel = plasma_pixels[y][x]
                canvas.itemconfig(canvas_pixels[y][x], fill=rgb_to_hex(pixel))

    def show_display():
        for y in range(HEIGHT):
            for x in range(WIDTH):
                pixel = display_pixels[y][x]
                canvas.itemconfig(canvas_pixels[y][x + 2 * WIDTH], fill=rgb_to_hex(pixel))

    def show_error():
        max_error = max_error_value()
        for y in range(HEIGHT):
            for x in range(WIDTH):
                error = error_values[y][x] / max_error
                canvas.itemconfig(canvas_pixels[y][x + WIDTH], fill=hsv_to_hex(1, error, 1))

    def update(t):
        update_plasma(t)
        update_clock()
        update_error()
        update_display()
        show_plasma()
        show_error()
        show_display()
        root.after(UPDATE_DELAY, lambda: update(t + 0.01))

    update(random.randrange(0, 1000000))
    root.mainloop()

if __name__ == "__main__":
    main()
