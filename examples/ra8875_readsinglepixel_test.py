# SPDX-FileCopyrightText: 2024 DJDevon3
# SPDX-License-Identifier: MIT
"""RA8875 Read Single Pixel example"""

import time
import busio
import digitalio
import board

from adafruit_ra8875 import ra8875
from adafruit_ra8875.bmp import BMP
from adafruit_ra8875.ra8875 import color565

# Configuration for CS and RST pins:
cs_pin = digitalio.DigitalInOut(board.D9)
rst_pin = digitalio.DigitalInOut(board.D10)

# Config for display baudrate (default max is 6mhz):
BAUDRATE = 6000000

# Setup SPI bus using hardware SPI:
spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Create and setup the RA8875 display:
display = ra8875.RA8875(spi, cs=cs_pin, rst=rst_pin, baudrate=BAUDRATE)
display.init()

BLACK = color565(0, 0, 0)
RED = color565(255, 0, 0)
GREEN = color565(0, 255, 0)
BLUE = color565(0, 0, 255)
YELLOW = color565(255, 255, 0)
CYAN = color565(0, 255, 255)
MAGENTA = color565(255, 0, 255)
WHITE = color565(255, 255, 255)

# Load the bitmap image
bitmap = BMP("/ra8875_color_chart.bmp")

# Center BMP image on the display
x_position = (display.width // 2) - (bitmap.width // 2)
y_position = (display.height // 2) - (bitmap.height // 2)

# Fill entire display background with white
display.fill(WHITE)
print("Filled display layer0 with white\n")

# Draw BMP (bottom to top)
bitmap.draw_bmp(display, x_position, y_position)

# Coordinates inside of a 53x53 red square in the bmp
X1 = 320
Y1 = 190
# Coordinates inside of a 53x53 blue square in the bmp
X2 = 370
Y2 = 190
# Coordinates inside of a 53x53 purple square in the bmp
X3 = 425
Y3 = 190
# Coordinates inside of a 53x53 yellow square in the bmp
X4 = 485
Y4 = 190
# Coordinates inside of a 53x53 green square in the bmp
X5 = 320
Y5 = 240
# Coordinates inside of a 53x53 cyan square in the bmp
X6 = 370
Y6 = 240
# Coordinates inside of a 53x53 white square in the bmp
X7 = 425
Y7 = 240
# Coordinates inside of a 53x53 black square in the bmp
X8 = 485
Y8 = 240
# Coordinates inside of a 53x53 yellow square in the bmp
X9 = 320
Y9 = 290
# Coordinates inside of a 53x53 red square in the bmp
X10 = 370
Y10 = 290
# Coordinates inside of a 53x53 green square in the bmp
X11 = 425
Y11 = 290
# Coordinates inside of a 53x53 blue square in the bmp
X12 = 485
Y12 = 290

# List of color sampling coordinates
coordinates = [
    (X1, Y1),
    (X2, Y2),
    (X3, Y3),
    (X4, Y4),
    (X5, Y5),
    (X6, Y6),
    (X7, Y7),
    (X8, Y8),
    (X9, Y9),
    (X10, Y10),
    (X11, Y11),
    (X12, Y12),
]

# Giving them names makes it easier to spot errors
color_names = [
    "Red",
    "Blue",
    "Purple",
    "Yellow",
    "Green",
    "Cyan",
    "White",
    "Black",
    "Yellow",
    "Red",
    "Green",
    "Blue",
]

# Starting x,y for color rectangles to create
rect_coordinates = [
    (0, 0),
    (53, 0),
    (106, 0),
    (159, 0),
    (0, 53),
    (53, 53),
    (106, 53),
    (159, 53),
    (0, 106),
    (53, 106),
    (106, 106),
    (159, 106),
]

# Read every pixel at listed coordinates
# Returns colors as r,g,b
# Creates filled rectangles using r,g,b to confirm color sample
for i, (x, y) in enumerate(coordinates):
    color = display.read_single_pixel(x, y)
    print(f"color{i+1} at ({x},{y}): {color_names[i]} - {color}")
    time.sleep(0.1)
    rect_x, rect_y = rect_coordinates[i]
    display.fill_rect(rect_x, rect_y, 53, 53, color565(color))

# Draws cross-hair to confirm sampled coordinates
# This can only happen after the sample is taken
display.draw_cursor(X1, Y1, RED, BLACK)
display.draw_cursor(X2, Y2, RED, BLACK)
display.draw_cursor(X3, Y3, RED, BLACK)
display.draw_cursor(X4, Y4, RED, BLACK)
display.draw_cursor(X5, Y5, RED, BLACK)
display.draw_cursor(X6, Y6, RED, BLACK)
display.draw_cursor(X7, Y7, RED, BLACK)
display.draw_cursor(X8, Y8, RED, BLACK)
display.draw_cursor(X9, Y9, RED, BLACK)
display.draw_cursor(X10, Y10, RED, BLACK)
display.draw_cursor(X11, Y11, RED, BLACK)
display.draw_cursor(X12, Y12, RED, BLACK)
