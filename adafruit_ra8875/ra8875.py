# The MIT License (MIT)
#
# Copyright (c) 2019 Melissa LeBlanc-Williams for Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`Adafruit_RA8875`
====================================================

A Driver Library for the RA8875

* Author(s): Melissa LeBlanc-Williams

Implementation Notes
--------------------

**Hardware:**

* `RA8875 Driver Board for 40-pin TFT Touch Displays - 800x480 Max <https://www.adafruit.com/product/1590>`_

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases
* Adafruit's Bus Device library:
  https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
# * Adafruit's Register library: https://github.com/adafruit/Adafruit_CircuitPython_Register
"""

# imports
import time
import adafruit_bus_device.spi_device as spi_device
import adafruit_ra8875.registers as reg

try:
    import struct
except ImportError:
    import ustruct as struct

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_RA8875.git"

def color565(r, g=0, b=0):
    """Convert red, green and blue values (0-255) into a 16-bit 565 encoding."""
    try:
        r, g, b = r  # see if the first var is a tuple/list
    except TypeError:
        pass
    return (r & 0xf8) << 8 | (g & 0xfc) << 3 | b >> 3

class RA8875:
    """Set Variables and Send Init Commands"""
    def __init__(self, spi, cs, rst=None, width=800, height=480, baudrate=12000000, polarity=0, phase=0):
        self.spi_device = spi_device.SPIDevice(spi, cs, baudrate=baudrate, polarity=polarity, phase=phase)
        self.width = width
        self.height = height
        self.rst = rst
        if self.rst:
            self.rst.switch_to_output(value=0)
            self.reset()
        if self.read_reg(0) == 0x75:
            return False
        self._txt_scale = 0
        self._mode = None
        self._tpin = None

    def init(self, start_on=True):
        if self.width == 800 and self.height == 480:
            pixclk = reg.PCSR_PDATL | reg.PCSR_2CLK
            hsync_nondisp = 26
            hsync_start = 32
            hsync_pw = 96
            vsync_nondisp = 32
            vsync_start = 23
            vsync_pw = 2
            self.adc_clk = reg.TPCR0_ADCCLK_DIV16
        elif self.width == 480 and self.height == 272:
            pixclk = reg.PCSR_PDATL | reg.PCSR_4CLK
            hsync_nondisp = 10
            hsync_start = 8
            hsync_pw = 48
            vsync_nondisp = 3
            vsync_start = 8
            vsync_pw = 10
            self.adc_clk = reg.TPCR0_ADCCLK_DIV4
        else:
            raise ValueError('An invalid display size was specified.')

        self.pllinit()

        self.write_reg(reg.SYSR, reg.SYSR_16BPP | reg.SYSR_MCU8)
        self.write_reg(reg.PCSR, pixclk)
        time.sleep(0.001)   # 1 millisecond

        # Horizontal settings registers
        self.write_reg(reg.HDWR, self.width // 8 - 1)
        self.write_reg(reg.HNDFTR, reg.HNDFTR_DE_HIGH)
        self.write_reg(reg.HNDR, (hsync_nondisp - 2) // 8)
        self.write_reg(reg.HSTR, hsync_start // 8 - 1)
        self.write_reg(reg.HPWR, reg.HPWR_LOW + hsync_pw // 8 - 1)

        # Vertical settings registers
        self.write_reg(reg.VDHR0, (self.height - 1) & 0xFF)
        self.write_reg(reg.VDHR1, (self.height - 1) >> 8)
        self.write_reg(reg.VNDR0, vsync_nondisp - 1)
        self.write_reg(reg.VNDR1, vsync_nondisp >> 8)
        self.write_reg(reg.VSTR0, vsync_start - 1)
        self.write_reg(reg.VSTR1, vsync_start >> 8)
        self.write_reg(reg.VPWR, reg.VPWR_LOW + vsync_pw - 1)

        # Set active window X
        self.write_reg(reg.HSAW0, 0)
        self.write_reg(reg.HSAW1, 0)
        self.write_reg(reg.HEAW0, (self.width - 1) & 0xFF)
        self.write_reg(reg.HEAW1, (self.width - 1) >> 8)

        # Set active window Y
        self.write_reg(reg.VSAW0, 0)
        self.write_reg(reg.VSAW1, 0)
        self.write_reg(reg.VEAW0, (self.height - 1) & 0xFF)
        self.write_reg(reg.VEAW1, (self.height - 1) >> 8)

        # Clear the entire window
        self.write_reg(reg.MCLR, reg.MCLR_START | reg.MCLR_FULL)
        time.sleep(0.500)   # 500 milliseconds

        self.on(start_on)
        self.gpiox(True)
        self.pwm1_config(True, reg.PWM_CLK_DIV1024)
        self.pwm1_out(255)

    def pllinit(self):
        self.write_reg(reg.PLLC1, reg.PLLC1_PLLDIV1 + 10)
        time.sleep(0.001)   # 1 millisecond
        self.write_reg(reg.PLLC2, reg.PLLC2_DIV4)
        time.sleep(0.001)   # 1 millisecond

    def write_reg(self, cmd, data):
        self.write_cmd(cmd)
        self.write_data(data)

    def write_cmd(self, cmd):
        with self.spi_device as spi:
            spi.write(reg.CMDWR)
            spi.write(bytearray([cmd]))

    def write_data(self, data, raw=False):
        with self.spi_device as spi:
            spi.write(reg.DATWR)
            spi.write(data if raw else bytearray([data]))

    def read_reg(self, cmd):
        self.write_cmd(cmd)
        return self.read_data()

    def read_status(self):
        cmd = bytearray(1)
        with self.spi_device as spi:
            spi.write(reg.CMDRD)
            spi.readinto(cmd)
            return struct.unpack(">B", cmd)[0]

    def read_data(self):
        data = bytearray(1)
        with self.spi_device as spi:
            spi.write(reg.DATRD)
            spi.readinto(data)
            return struct.unpack(">B", data)[0]

    def wait_poll(self, register, mask):
        start = int(round(time.time() * 1000))
        while True:
            time.sleep(0.001)
            regval = self.read_reg(register)
            if regval & mask == 0:
                return True
            millis = int(round(time.time() * 1000))
            if millis - start >= 20: return False

    def reset(self):
        self.rst.value = 0
        time.sleep(0.100)  # 100 milliseconds
        self.rst.value = 1
        time.sleep(0.100)  # 100 milliseconds

    def rect(self, x, y, width, height, color):
        self.rect_helper(x, y, width, height, color, False)

    def fill_rect(self, x, y, width, height, color):
        self.rect_helper(x, y, width, height, color, True)

    def fill(self, color): # Fill The Screen
        self.rect_helper(0, 0, self.width, self.height, color, True)

    def circle(self, x, y, radius, color):
        self.circle_helper(x, y, radius, color, False)

    def fill_circle(self, x, y, radius, color):
        self.circle_helper(x, y, radius, color, True)

    def ellipse(self, x_center, y_center, long_axis, short_axis, color):
        self.ellipse_helper(x_center, y_center, long_axis, short_axis, color, False)

    def fill_ellipse(self, x_center, y_center, long_axis, short_axis, color):
        self.ellipse_helper(x_center, y_center, long_axis, short_axis, color, True)

    def curve(self, x_center, y_center, long_axis, short_axis, curve_part, color):
        self.curve_helper(x_center, y_center, long_axis, short_axis, curve_part, color, False)

    def fill_curve(self, x_center, y_center, long_axis, short_axis, curve_part, color):
        self.curve_helper(x_center, y_center, long_axis, short_axis, curve_part, color, True)

    def triangle(self, x1, y1, x2, y2, x3, y3, color):
        self.triangle_helper(x1, y1, x2, y2, x3, y3, color, False)

    def fill_triangle(self, x1, y1, x2, y2, x3, y3, color):
        self.triangle_helper(x1, y1, x2, y2, x3, y3, color, True)

    def _encode_pos(self, x, y):
        """Encode a postion into bytes."""
        return struct.pack(">HH", x, y)

    def _encode_pixel(self, color):
        """Encode a pixel color into bytes."""
        return struct.pack(">H", color)

    def _decode_pixel(self, data):
        """Decode bytes into a pixel color."""
        return color565(*struct.unpack(">BBB", data))

    def setxy(self, x, y):
        self.gfx_mode()
        self.write_reg(reg.CURH0, x)
        self.write_reg(reg.CURH1, x >> 8)
        self.write_reg(reg.CURV0, y)
        self.write_reg(reg.CURV1, y >> 8)

    def pixel(self, x, y, color):
        self.setxy(x, y)
        self.write_cmd(reg.MRWC)
        self.write_data(self._encode_pixel(color), True)

    def push_pixels(self, pixel_data):
        self.gfx_mode()
        self.write_cmd(reg.MRWC)
        self.write_data(pixel_data, True)

    def set_window(self, x, y, width, height):
        """Set an Active Drawing Area, which can be used in conjuntion with push_pixels
        for faster drawing"""
        if x + width >= self.width: width = self.width - x
        if y + height >= self.height: height = self.height - y
        # X
        self.write_reg(reg.HSAW0,x & 0xFF)
        self.write_reg(reg.HSAW0+1,x >> 8)
        self.write_reg(reg.HEAW0,(x + width) & 0xFF)
        self.write_reg(reg.HEAW0+1,(x + width) >> 8)
        # Y
        self.write_reg(reg.VSAW0,y & 0xFF)
        self.write_reg(reg.VSAW0+1,y >> 8)
        self.write_reg(reg.VEAW0,(y + height) & 0xFF)
        self.write_reg(reg.VEAW0+1,(y + height) >> 8)

    def hline(self, x, y, width, color):
        self.line(x, y, x + width, y, color)

    def vline(self, x, y, height, color):
        self.line(x, y, x, y + height, color)

    def line(self, x1, y1, x2, y2, color):
        self.gfx_mode()

        # Set Start Point
        self.write_reg(0x91, x1)
        self.write_reg(0x92, x1 >> 8)
        self.write_reg(0x93, y1)
        self.write_reg(0x94, y1 >> 8)

        # Set End Point
        self.write_reg(0x95, x2)
        self.write_reg(0x96, x2 >> 8)
        self.write_reg(0x97, y2)
        self.write_reg(0x98, y2 >> 8)

        self._set_color(color)

        # Draw it
        self.write_reg(reg.DCR, 0x80)
        self.wait_poll(reg.DCR, reg.DCR_LNSQTR_STATUS)

    def circle_helper(self, x, y, radius, color, filled):
        self.gfx_mode()

        # Set X, Y, and Radius
        self.write_reg(0x99, x)
        self.write_reg(0x9A, x >> 8)
        self.write_reg(0x9B, y)
        self.write_reg(0x9C, y >> 8)
        self.write_reg(0x9D, radius)

        self._set_color(color)

        # Draw it
        self.write_reg(reg.DCR, reg.DCR_CIRC_START | (reg.DCR_FILL if filled else reg.DCR_NOFILL))
        print(self.wait_poll(reg.DCR, reg.DCR_CIRC_STATUS))

    def rect_helper(self, x, y, width, height, color, filled):
        self.gfx_mode()

        # Set X and Y
        self.write_reg(0x91, x)
        self.write_reg(0x92, x >> 8)
        self.write_reg(0x93, y)
        self.write_reg(0x94, y >> 8)

        # Set Width and Height
        self.write_reg(0x95, width)
        self.write_reg(0x96, width >> 8)
        self.write_reg(0x97, height)
        self.write_reg(0x98, height >> 8)

        self._set_color(color)

        # Draw it
        self.write_reg(reg.DCR, 0xB0 if filled else 0x90)
        self.wait_poll(reg.DCR, reg.DCR_LNSQTR_STATUS)

    def fill_round_rect(self, x, y, width, height, radius, color):
        self.gfx_mode()

        self.curve_helper(x + radius, y + radius, radius, radius, 1, color, True)
        self.curve_helper(x + width - radius, y + radius, radius, radius, 2, color, True)
        self.curve_helper(x + radius, y + height - radius, radius, radius, 0, color, True)
        self.curve_helper(x + width - radius, y + height - radius, radius, radius, 3, color, True)
        self.rect_helper(x + radius, y, x + width - radius, y + height, color, True)
        self.rect_helper(x, y + radius, x + width, y + height - radius, color, True)

    def round_rect(self, x, y, width, height, radius, color):
        self.gfx_mode()

        self.curve_helper(x + radius, y + radius, radius, radius, 1, color, False)
        self.curve_helper(x + width - radius, y + radius, radius, radius, 2, color, False)
        self.curve_helper(x + radius, y + height - radius, radius, radius, 0, color, False)
        self.curve_helper(x + width - radius, y + height - radius, radius, radius, 3, color, False)
        self.hline(x + radius, y, width - (radius * 2), color)
        self.hline(x + radius, y + height, width - (radius * 2), color)
        self.vline(x, y + radius, height - (radius * 2), color)
        self.vline(x + width, y + radius, height - (radius * 2), color)

    def triangle_helper(self, x1, y1, x2, y2, x3, y3, color, filled):
        self.gfx_mode()

        # Set Point Coordinates
        self.write_reg(0x91, x1)
        self.write_reg(0x92, x1 >> 8)
        self.write_reg(0x93, y1)
        self.write_reg(0x94, y1 >> 8)
        self.write_reg(0x95, x2)
        self.write_reg(0x96, x2 >> 8)
        self.write_reg(0x97, y2)
        self.write_reg(0x98, y2 >> 8)
        self.write_reg(0xA9, x3)
        self.write_reg(0xAA, x3 >> 8)
        self.write_reg(0xAB, y3)
        self.write_reg(0xAC, y3 >> 8)

        self._set_color(color)

        # Draw it
        self.write_reg(reg.DCR, 0xA1 if filled else 0x81)
        self.wait_poll(reg.DCR, reg.DCR_LNSQTR_STATUS)

    def curve_helper(self, x_center, y_center, long_axis, short_axis, curve_part, color, filled):
        self.gfx_mode()

        # Set X and Y Center
        self.write_reg(0xA5, x_center)
        self.write_reg(0xA6, x_center >> 8)
        self.write_reg(0xA7, y_center)
        self.write_reg(0xA8, y_center >> 8)

        # Set Long and Short Axis
        self.write_reg(0xA1, long_axis)
        self.write_reg(0xA2, long_axis >> 8)
        self.write_reg(0xA3, short_axis)
        self.write_reg(0xA4, short_axis >> 8)

        self._set_color(color)

        # Draw it
        self.write_reg(reg.ELLIPSE, (0xD0 if filled else 0x90) | (curve_part & 0x03))
        self.wait_poll(reg.ELLIPSE, reg.ELLIPSE_STATUS)

    def ellipse_helper(self, x_center, y_center, long_axis, short_axis, color, filled):
        self.gfx_mode()

        # Set X and Y  Center
        self.write_reg(0xA5, x_center)
        self.write_reg(0xA6, x_center >> 8)
        self.write_reg(0xA7, y_center)
        self.write_reg(0xA8, y_center >> 8)

        # Set Long and Short Axis
        self.write_reg(0xA1, long_axis)
        self.write_reg(0xA2, long_axis >> 8)
        self.write_reg(0xA3, short_axis)
        self.write_reg(0xA4, short_axis >> 8)

        self._set_color(color)

        # Draw it
        self.write_reg(reg.ELLIPSE, 0xC0 if filled else 0x80)
        self.wait_poll(reg.ELLIPSE, reg.ELLIPSE_STATUS)

    def _set_bg_color(self, color):
        self.write_reg(0x60, (color & 0xf800) >> 11)
        self.write_reg(0x61, (color & 0x07e0) >> 5)
        self.write_reg(0x62, (color & 0x001f))

    def _set_color(self, color):
        self.write_reg(0x63, (color & 0xf800) >> 11)
        self.write_reg(0x64, (color & 0x07e0) >> 5)
        self.write_reg(0x65, (color & 0x001f))

    def on(self, on):
        self.write_reg(reg.PWRR, reg.PWRR_NORMAL | (reg.PWRR_DISPON if on else reg.PWRR_DISPOFF))

    def gpiox(self, on):
        self.write_reg(reg.GPIOX, 1 if on else 0)

    def pwm1_config(self, on, clock):
        self.write_reg(reg.P1CR, (reg.P1CR_ENABLE if on else reg.P1CR_DISABLE) | (clock & 0xF))

    def pwm2_config(self, on, clock):
        self.write_reg(reg.P2CR, (reg.P2R_ENABLE if on else reg.P2CR_DISABLE) | (clock & 0xF))

    def pwm1_out(self, p):
        self.write_reg(reg.P1DCR, p)

    def pwm2_out(self, p):
        self.write_reg(reg.P2DCR, p)

    def touch_init(self, tpin):
        self._tpin = tpin
        self._tpin.direction.INPUT
        self.write_reg(reg.INTC2, reg.INTC2_TP)
        self.touch_enable(True)

    def touch_enable(self, on):
        if self._tpin is not None:
            self.gfx_mode()
            if on:
                self.write_reg(reg.TPCR0, reg.TPCR0_ENABLE | reg.TPCR0_WAIT_4096CLK | reg.TPCR0_WAKEENABLE | self.adc_clk)
                self.write_reg(reg.TPCR1, reg.TPCR1_AUTO | reg.TPCR1_DEBOUNCE)
                self.write_data(self.read_reg(reg.INTC1) | reg.INTC1_TP)
            else:
                self.write_data(self.read_reg(reg.INTC1) & ~reg.INTC1_TP)
                self.write_reg(reg.TPCR0, reg.TPCR0_DISABLE)

    def touched(self):
        if self._tpin is None: return False
        self.gfx_mode()
        if self._tpin.value: return False
        istouched = True if self.read_reg(reg.INTC2) & reg.INTC2_TP else False
        return istouched

    def touch_read(self):
        self.gfx_mode()
        tx = self.read_reg(reg.TPXH)
        ty = self.read_reg(reg.TPYH)
        temp = self.read_reg(reg.TPXYL)
        tx = tx << 2
        ty = ty << 2
        tx |= temp & 0x03
        ty |= (temp >> 2) & 0x03
        self.write_reg(reg.INTC2, reg.INTC2_TP)
        return [tx, ty]

    def gfx_mode(self):
        if self._mode == "gfx": return
        self.write_data(self.read_reg(reg.MWCR0) & ~reg.MWCR0_TXTMODE)
        self._mode = "gfx"

    def txt_mode(self):
        if self._mode == "txt": return
        self.write_data(self.read_reg(reg.MWCR0) | reg.MWCR0_TXTMODE)
        self.write_data(self.read_reg(reg.FNCR0) & ~((1<<7) | (1<<5)))
        self._mode = "txt"

    def txt_set_cursor(self, x, y):
        self.txt_mode()
        self.write_reg(0x2A, x & 0xFF)
        self.write_reg(0x2B, x >> 8)
        self.write_reg(0x2C, y & 0xFF)
        self.write_reg(0x2D, y >> 8)

    def txt_color(self, fgcolor, bgcolor):
        self._set_color(fgcolor)
        self._set_bg_color(bgcolor)
        self.write_data(self.read_reg(reg.FNCR1) & ~(1<<6))

    def txt_trans(self, color):
        self.txt_mode()
        self._set_color(color)
        self.write_data(self.read_reg(reg.FNCR1) | 1<<6)

    def txt_write(self, string):
        self.txt_mode()
        self.write_cmd(reg.MRWC)
        for c in string:
            self.write_data(c, True)
            if self._txt_scale > 0:
                time.sleep(0.001)

    def txt_size(self, scale):
        self.txt_mode()
        if scale > 3: scale = 3
        self.write_data((self.read_reg(reg.FNCR1) & ~(0xF)) | (scale << 2) | scale)
        self._txt_scale = scale;