# Quick bitmap test of RA8875 with Feather M4
import time
import busio
import digitalio
import board

import adafruit_ra8875.ra8875 as ra8875
from adafruit_ra8875.ra8875 import color565

WHITE = color565(255, 255, 255)

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
display.fill(WHITE)

class BMP:
    def __init__(self, filename):
        self.filename = filename
        self.colors = 0

    def read_header(self):
        if self.colors:
            return
        with open(self.filename, 'rb') as f:
            f.seek(10)
            self.data = int.from_bytes(f.read(4), 'little')
            f.seek(18)
            self.width = int.from_bytes(f.read(4), 'little')
            self.height = int.from_bytes(f.read(4), 'little')
            f.seek(28)
            self.bpp = int.from_bytes(f.read(2), 'little')
            f.seek(34)
            self.data_size = int.from_bytes(f.read(4), 'little')
            f.seek(46)
            self.colors = int.from_bytes(f.read(4), 'little')

    def draw(self, display, x=0, y=0):
        self.read_header()
        print("{:d}x{:d} image".format(self.width, self.height))
        print("{:d}-bit encoding detected".format(self.bpp))
        line = 0;
        line_size = self.width * (self.bpp//8)
        mod4 = line_size % 4
        if mod4 !=0:
            line_size += (4-mod4)
        self.bmp_data = b''
        self.current_line_data = b''
        with open(self.filename, 'rb') as f:
            f.seek(self.data)
            display.set_window(x, y, self.width, self.height)
            for line in range(self.height):
                self.current_line_data = b''
                line_data = f.read(line_size)
                for i in range(0, line_size, self.bpp//8):
                    if (line_size-i) < self.bpp//8:
                        break
                    b1 = line_data[i]
                    b2 = line_data[i+1]
                    if self.bpp == 16:
                        color = b1 << 8 | b2
                    if self.bpp == 24:
                        b3 = line_data[i+2]
                        color = color565(b1, b2, b3)
                    c = display._encode_pixel(color)
                    self.current_line_data = self.current_line_data + c
                display.setxy(x, self.height - line + y)
                display.push_pixels(self.current_line_data)
            display.set_window(0, 0, display.width, display.height)

BMP("/blinka.bmp").draw(display, 287, 127)