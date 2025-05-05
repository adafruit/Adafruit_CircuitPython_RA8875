# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT
# 2024 Optimized with ChatGPT by DJDevon3
# https://chat.openai.com/share/57ee2bb5-33ba-4538-a4b7-ec3dea8ea5c7
""" Raw Bitmap Helper Class (not hardware accelerated)"""

import struct


class BMP:
    """
    Raw Bitmap Helper Class (not hardware accelerated)

    :param str: filename BMP filename
    :param int colors: BMP color data
    :param int data: BMP data
    :param int data_size: BMP data size
    :param int bpp: BMP bit depth data
    :param int width: BMP width
    :param int height: BMP height
    :param int read_header: BMP read header function

    """

    def __init__(self, filename, debug: bool = False):
        self.filename = filename
        self.colors = None
        self.data = None
        self.data_size = 0
        self.bpp = 0
        self.width = 0
        self.height = 0
        self.debug = debug  # Store debug mode
        self.read_header()

    def read_header(self):
        """Read file header data"""
        if self.colors:
            return
        with open(self.filename, "rb") as bmp_file:
            header_data = bmp_file.read(
                54
            )  # Read the entire BMP header (assuming it's 54 bytes)
            self.data = int.from_bytes(header_data[10:14], "little")
            self.width = int.from_bytes(header_data[18:22], "little")
            self.height = int.from_bytes(header_data[22:26], "little")
            self.bpp = int.from_bytes(header_data[28:30], "little")
            self.data_size = int.from_bytes(header_data[34:38], "little")
            self.colors = int.from_bytes(header_data[46:50], "little")
            if self.debug:  # Check debug mode
                print(f"Header Hex Dump: {header_data}")
                print(f"Header Data: {self.data}")
                print(f"Header Width: {self.width}")
                print(f"Header Height: {self.height}")
                print(f"Header BPP: {self.bpp}")
                print(f"Header Size: {self.data_size}")
                print(f"Header Colors: {self.colors}")

    def draw_bmp(self, disp, x: int = 0, y: int = 0, chunk_size: int = 1):
        """Draw BMP"""
        if self.debug:  # Check debug mode
            print(f"{self.width}x{self.height} image")
            print(f"{self.bpp}-bit encoding detected")

        with open(self.filename, "rb") as bmp_file:
            bmp_file.seek(self.data)
            line_data = bmp_file.read()

        for start_line in range(0, self.height, chunk_size):
            end_line = min(start_line + chunk_size, self.height)
            current_line_data = b""
            for line in range(start_line, end_line):
                line_start = line * self.width * (self.bpp // 8)
                line_end = line_start + self.width * (self.bpp // 8)
                for i in range(line_start, line_end, self.bpp // 8):
                    if (line_end - i) < self.bpp // 8:
                        break
                    if self.bpp == 16:
                        color = self.convert_555_to_565(
                            line_data[i] | line_data[i + 1] << 8
                        )
                    elif self.bpp in (24, 32):
                        color = self.color565(
                            line_data[i + 2], line_data[i + 1], line_data[i]
                        )
                    current_line_data += struct.pack(">H", color)
            disp.setxy(x, self.height - end_line + y)
            disp.push_pixels(current_line_data)

    @staticmethod
    def convert_555_to_565(color_555):
        """Convert 16-bit color from 5-5-5 to 5-6-5 format"""
        r = (color_555 & 0x1F) << 3
        g = ((color_555 >> 5) & 0x1F) << 2
        b = ((color_555 >> 10) & 0x1F) << 3
        return (r << 11) | (g << 5) | b

    @staticmethod
    def color565(r, g, b):
        """Convert 24-bit RGB color to 16-bit color (5-6-5 format)"""
        return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
