# SPDX-FileCopyrightText: 2024 DJDevon3
# SPDX-License-Identifier: MIT

# RA8875 Screen Saver example

import random
import busio
import digitalio
import board

from adafruit_ra8875 import ra8875

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

square_size = 32
horizontal_squares = 25
vertical_squares = 15

while True:
    for row_index in range(vertical_squares):
        for square_index in range(horizontal_squares):
            x = square_index * square_size
            y = row_index * square_size

            # Generate random RGB values for each square
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)

            # Convert RGB to color565 format
            color565_value = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

            # Draw the square with the random color
            display.fill_rect(x, y, square_size, square_size, color565_value)
