# SPDX-FileCopyrightText: 2019 Melissa LeBlanc-Williams for Adafruit Industries
#
# SPDX-License-Identifier: MIT
# pylint: disable=too-many-lines
"""
`adafruit_ra8875.ra8875`
====================================================

A Driver Library for the RA8875

* Author(s): Melissa LeBlanc-Williams

Implementation Notes
--------------------

**Hardware:**

* RA8875 Driver Board for 40-pin TFT Touch Displays - 800x480:
  https://www.adafruit.com/product/1590

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases
* Adafruit's Bus Device library:
  https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
"""

# imports
import struct
import time

from digitalio import Direction
from adafruit_bus_device import spi_device
from adafruit_ra8875 import registers as reg

try:
    from typing import Optional, Tuple, Union
    from digitalio import DigitalInOut  # pylint: disable=ungrouped-imports
    from busio import SPI
except ImportError:
    pass

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_RA8875.git"


# pylint: disable-msg=invalid-name
def color565(r: int, g: int = 0, b: int = 0) -> int:
    """Convert red, green and blue values (0-255) into a 16-bit 565 encoding."""
    try:
        r, g, b = r  # see if the first var is a tuple/list
    except TypeError:
        pass
    return (r & 0xF8) << 8 | (g & 0xFC) << 3 | b >> 3


# pylint: enable-msg=invalid-name


# pylint: disable-msg=invalid-name
def convert_555_to_565(color_555):
    """Convert 16-bit color from 5-5-5 to 5-6-5 format"""
    r = (color_555 & 0x1F) << 3
    g = ((color_555 >> 5) & 0x1F) << 2
    b = ((color_555 >> 10) & 0x1F) << 3
    return (r << 11) | (g << 5) | b


# pylint: enable-msg=invalid-name


class RA8875_Device:
    """
    Base Class for the Display. Contains all the low level stuff. As well
    as the touch functions. Valid display sizes are currently 800x480 and 480x272.

    :param SPI spi: The spi peripheral to use
    :param DigitalInOut cs: The chip-select pin to use (sometimes labeled "SS")
    :param DigitalInOut rst: (optional) The reset pin if it exists (default=None)
    :param int width: (optional) The width of the display in pixels (default=800)
    :param int height: (optional) The height of the display in pixels (default=480)
    :param int baudrate: (optional) The spi speed (default=6000000)
    :param int polarity: (optional) The spi polarity (default=0)
    :param int phase: (optional) The spi phase (default=0)
    """

    # pylint: disable-msg=invalid-name,too-many-arguments
    def __init__(
        self,
        spi: SPI,
        cs: DigitalInOut,
        rst: Optional[DigitalInOut] = None,
        width: int = 800,
        height: int = 480,
        baudrate: int = 6000000,
        polarity: int = 0,
        phase: int = 0,
    ) -> None:
        self.spi_device = spi_device.SPIDevice(
            spi, cs, baudrate=baudrate, polarity=polarity, phase=phase
        )
        # Display advertised as 480x80 is actually 480x82
        if width == 480 and height == 80:
            height = 82
        self.width = width
        self.height = height
        self._mode = None
        self._tpin = None
        self.rst = rst
        self.vert_offset = 0
        if self.rst:
            self.rst.switch_to_output(value=0)
            self.reset()
        if self._read_reg(0) == 0x75:
            return
        self._adc_clk = reg.TPCR0_ADCCLK_DIV16

    # pylint: enable-msg=invalid-name,too-many-arguments

    def init(self, start_on: bool = True) -> None:
        """
        Send the Init Commands for the selected Display Size

        :param bool start_on: (optional) If the display should start in an On State (default=True)
        """
        hw_init = True
        release_displays = True

        if self.width == 480 and self.height == 82:
            self.vert_offset = 190

        if self.width == 800 and self.height == 480:
            pixclk = reg.PCSR_PDATL | reg.PCSR_2CLK
            hsync_nondisp = 26
            hsync_start = 32
            hsync_pw = 96
            vsync_nondisp = 32
            vsync_start = 23
            vsync_pw = 2
        elif self.width == 480 and self.height in (272, 128, 82):
            pixclk = reg.PCSR_PDATL | reg.PCSR_4CLK
            hsync_nondisp = 10
            hsync_start = 8
            hsync_pw = 48
            vsync_nondisp = 3
            vsync_start = 8
            vsync_pw = 10
            self._adc_clk = reg.TPCR0_ADCCLK_DIV4
        else:
            raise ValueError("An invalid display size was specified.")

        self.pllinit()

        if hw_init:  # Bits Per Pixel: 16 | Bus: 8-Bit
            self._write_reg(reg.SYSR, reg.SYSR_16BPP | reg.SYSR_MCU8)
            self._write_reg(reg.PCSR, pixclk)
            time.sleep(0.001)

        if release_displays:  # equivilent to displayio release_displays()
            # Horizontal settings registers
            self._write_reg(reg.HDWR, self.width // 8 - 1)
            self._write_reg(reg.HNDFTR, reg.HNDFTR_DE_HIGH)
            self._write_reg(reg.HNDR, (hsync_nondisp - 2) // 8)
            self._write_reg(reg.HSTR, hsync_start // 8 - 1)
            self._write_reg(reg.HPWR, reg.HPWR_LOW + hsync_pw // 8 - 1)

            # Vertical settings registers
            self._write_reg16(reg.VDHR0, self.height - 1 + self.vert_offset)
            self._write_reg16(reg.VNDR0, vsync_nondisp - 1)
            self._write_reg16(reg.VSTR0, vsync_start - 1)
            self._write_reg(reg.VPWR, reg.VPWR_LOW + vsync_pw - 1)

            # Set active window X
            self._write_reg16(reg.HSAW0, 0)
            self._write_reg16(reg.HEAW0, self.width - 1)

            # Set active window Y
            self._write_reg16(reg.VSAW0, self.vert_offset)
            self._write_reg16(reg.VEAW0, self.height - 1 + self.vert_offset)

            # Clear the entire window
            self._write_reg(reg.MCLR, reg.MCLR_START | reg.MCLR_FULL)
            time.sleep(0.500)

            # Turn the display on, enable GPIO, and setup the backlight
            self.turn_on(start_on)
            self._gpiox(True)
            self._pwm1_config(True, reg.PWM_CLK_DIV1024)
            self.brightness(255)

    def pllinit(self) -> None:
        """Init the Controller PLL"""
        self._write_reg(reg.PLLC1, reg.PLLC1_PLLDIV1 + 11)
        time.sleep(0.001)
        self._write_reg(reg.PLLC2, reg.PLLC2_DIV4)
        time.sleep(0.001)

    def _write_reg(
        self, cmd: int, data: int, raw: bool = False, debug: bool = False
    ) -> None:
        """
        Select a Register and write a byte or push raw data out

        :param byte cmd: The register to select
        :param data: The byte to write to the register
        :type data: byte or bytearray
        :param bool raw: (optional) Is the data a raw bytearray (default=False)
        """
        if debug:
            print(f"_write_reg: cmd={cmd}, data={data}, raw={raw}")
        self._write_cmd(cmd)
        self._write_data(data, raw)

    def _write_reg16(
        self, cmd: int, data: Union[int, bytearray], debug: bool = False
    ) -> None:
        """
        Select a Register and write 2 bytes or push raw data out

        :param byte cmd: The register to select
        :param data: The byte to write to the register
        :type data: byte or bytearray
        """
        if debug:
            print(f"_write_reg16: cmd={cmd}, data={data}")
        self._write_cmd(cmd)
        self._write_data(data)
        self._write_cmd(cmd + 1)
        self._write_data(data >> 8)

    def _write_cmd(self, cmd: int, debug: bool = False) -> None:
        """
        Select a Register/Command

        :param byte cmd: The register to select
        """
        if debug:
            print(f"_write_cmd: cmd={cmd}")
        with self.spi_device as spi:
            spi.write(reg.CMDWR)  # pylint: disable=no-member
            spi.write(bytearray([cmd & 0xFF]))  # pylint: disable=no-member

    def _write_data(self, data: int, raw: bool = False, debug: bool = False) -> None:
        """
        Write a byte or push raw data out

        :param data: The byte to write to the register
        :type data: byte or bytearray
        :param bool raw: (optional) Is the data a raw bytearray (default=False)
        """
        if debug:
            print(f"_write_data: data={data}, raw={raw}")
        with self.spi_device as spi:
            spi.write(reg.DATWR)  # pylint: disable=no-member
            if raw and isinstance(data, str):
                data = bytes(data, "utf8")
            spi.write(
                data if raw else bytearray([data & 0xFF])
            )  # pylint: disable=no-member

    def _read_reg(self, cmd: int, debug: bool = False) -> int:
        """
        Select a Register and read a byte

        :param byte cmd: The register to select
        :return: The results of the register
        :rtype: byte
        """
        if debug:
            print(f"_read_reg: cmd={cmd}")
        self._write_cmd(cmd)
        return self._read_data()

    def _read_data(self, debug: bool = False) -> int:
        """
        Read the data of the previously selected register

        :return: The data of the register
        :rtype: byte
        """
        data = bytearray(1)
        if debug:
            print(f"_read_data: data={data}")
        with self.spi_device as spi:
            spi.write(reg.DATRD)  # pylint: disable=no-member
            spi.readinto(data)  # pylint: disable=no-member
            return struct.unpack(">B", data)[0]

    def _read_data16(self, debug: bool = False) -> int:
        """
        Read 16 bits of data from the previously selected register

        :return: The 16-bit data read from the register
        :rtype: int
        """
        # Allocate space for 2 bytes
        data = bytearray(2)

        if debug:
            print("_read_data16: Reading 16 bits of data")

        with self.spi_device as spi:
            spi.write(reg.DATRD)  # Write the data read command
            spi.readinto(data)  # Read 2 bytes of data
        if debug:
            print(
                f"_read_data16: (data[0]: {data[0] & 0xFF:08b} "
                + f"{(data[0] >> 8) & 0xFF:08b} data[1]: {data[1] & 0xFF:08b} "
                + f"{(data[1] >> 8) & 0xFF:08b})"
            )

        # Combine the two bytes into a single 16-bit integer
        result = (data[0] << 8) | data[1]

        if debug:
            print(f"_read_data16: Read data: {result:#06x} (Binary: {result:016b})")

        return result

    def _wait_poll(self, register: int, mask: int) -> bool:
        """
        Keep checking a status bit and wait for an operation to complete.
        After 20ms, a timeout will occur and the function will stop waiting.

        :param byte register: The status register to read
        :param byte mask: The masked bit to check
        :return: If the operation completed without a timeout
        :rtype: bool
        """
        start = int(round(time.time() * 1000))
        while True:
            time.sleep(0.001)
            regval = self._read_reg(register)
            if regval & mask == 0:
                return True
            millis = int(round(time.time() * 1000))
            if millis - start >= 20:
                return False

    def turn_on(self, display_on: bool) -> None:
        """
        Turn the display on or off

        :param bool start_on: If the display should turn on or off
        """
        self._write_reg(
            reg.PWRR,
            reg.PWRR_NORMAL | (reg.PWRR_DISPON if display_on else reg.PWRR_DISPOFF),
        )

    def reset(self) -> None:
        """Perform a hard reset"""
        self.rst.value = 0
        time.sleep(0.100)
        self.rst.value = 1
        time.sleep(0.100)

    def soft_reset(self) -> None:
        """Perform a soft reset"""
        self._write_reg(reg.PWRR, reg.PWRR_SOFTRESET)
        self._write_data(reg.PWRR_NORMAL)
        time.sleep(0.001)

    def sleep(self, sleep: bool) -> None:
        """
        Turn the display off with and set or remove the sleep state

        :param bool sleep: Should we enable sleep mode
        """
        self._write_reg(
            reg.PWRR, reg.PWRR_DISPOFF if sleep else (reg.PWRR_DISPOFF | reg.PWRR_SLEEP)
        )

    def _gpiox(self, gpio_on: bool) -> None:
        """Enable or Disable the RA8875 GPIOs"""
        self._write_reg(reg.GPIOX, 1 if gpio_on else 0)

    def _pwm1_config(self, pwm_on: bool, clock: int) -> None:
        """
        Configure the backlight PWM Clock Speed

        :param bool pwm_on: Should we enable the Backlight PWM
        :param byte clock: Clock Divider to use for PWM Speed
        """
        self._write_reg(
            reg.P1CR, (reg.P1CR_ENABLE if pwm_on else reg.P1CR_DISABLE) | (clock & 0xF)
        )

    def brightness(self, level: int):
        """
        Configure the backlight brightness (0-255)

        :param byte level: The PWM Duty Cycle
        """
        self._write_reg(reg.P1DCR, level)

    def touch_init(
        self, tpin: Optional[DigitalInOut] = None, enable: bool = True
    ) -> None:
        """
        Initialize the Touchscreen

        :param DigitalInOut tpin: (Optional) The Touch Screen Interrupt Pin (default=None)
        :param bool enable: Enable the Touch Functionality as well
        """
        if tpin is not None:
            tpin.direction = Direction.INPUT
        self._tpin = tpin
        self._write_reg(reg.INTC2, reg.INTC2_TP)
        self.touch_enable(enable)

    def touch_enable(self, touch_on: bool) -> None:
        """
        Enable touch functionality

        :param bool touch_on: Enable/Disable the Touch Functionality
        """
        if touch_on:
            self._write_reg(
                reg.TPCR0,
                reg.TPCR0_ENABLE
                | reg.TPCR0_WAIT_4096CLK
                | reg.TPCR0_WAKEENABLE
                | self._adc_clk,
            )
            self._write_reg(reg.TPCR1, reg.TPCR1_AUTO | reg.TPCR1_DEBOUNCE)
            self._write_data(self._read_reg(reg.INTC1) | reg.INTC1_TP)
        else:
            self._write_data(self._read_reg(reg.INTC1) & ~reg.INTC1_TP)
            self._write_reg(reg.TPCR0, reg.TPCR0_DISABLE)

    def touched(self) -> bool:
        """
        Check if the Screen is currently being touched. If a touch interrupt
        was specified, this is checked first.

        :return: Is screen is currently being touched
        :rtype: bool
        """
        if self._tpin is not None:
            self._gfx_mode()  # Hack that seems to work
            if self._tpin.value:
                return False
        istouched = self._read_reg(reg.INTC2) & reg.INTC2_TP
        return istouched

    def touch_read(self) -> Tuple[int, int]:
        """
        Read the X and Y Coordinates of the current Touch Position

        :return: The coordinate of the detected touch
        :rtype: tuple[int, int]
        """
        touch_x = self._read_reg(reg.TPXH)
        touch_y = self._read_reg(reg.TPYH)
        temp = self._read_reg(reg.TPXYL)
        touch_x = touch_x << 2
        touch_y = touch_y << 2
        touch_x |= temp & 0x03
        touch_y |= (temp >> 2) & 0x03
        self._write_reg(reg.INTC2, reg.INTC2_TP)
        return [touch_x, touch_y]

    def _gfx_mode(self) -> None:
        """Set to Graphics Mode"""
        if self._mode == "gfx":
            return
        self._write_data(self._read_reg(reg.MWCR0) & ~reg.MWCR0_TXTMODE)
        self._mode = "gfx"

    def _txt_mode(self) -> None:
        """Set to Text Mode"""
        if self._mode == "txt":
            return
        self._write_data(self._read_reg(reg.MWCR0) | reg.MWCR0_TXTMODE)
        self._write_data(self._read_reg(reg.FNCR0) & ~((1 << 7) | (1 << 5)))
        self._mode = "txt"


class RA8875Display(RA8875_Device):
    """
    Drawing Class for the Display. Contains all the basic drawing functionality as well
    as the text functions. Valid display sizes are currently 800x480 and 480x272.

    :param SPI spi: The spi peripheral to use
    :param DigitalInOut cs: The chip-select pin to use (sometimes labeled "SS")
    :param DigitalInOut rst: (optional) The reset pin if it exists (default=None)
    :param int width: (optional) The width of the display in pixels (default=800)
    :param int height: (optional) The height of the display in pixels (default=480)
    :param int baudrate: (optional) The spi speed (default=6000000)
    :param int phase: (optional) The spi phase (default=0)
    :param int polarity: (optional) The spi polarity (default=0)
    """

    # pylint: disable-msg=invalid-name,too-many-arguments
    def __init__(
        self,
        spi: SPI,
        cs: DigitalInOut,
        rst: Optional[DigitalInOut] = None,
        width: int = 800,
        height: int = 480,
        baudrate: int = 6000000,
        polarity: int = 0,
        phase: int = 0,
    ) -> None:
        self._txt_scale = 0
        super().__init__(spi, cs, rst, width, height, baudrate, polarity, phase)

    # pylint: disable=too-many-arguments

    def txt_set_cursor(self, x: int, y: int) -> None:
        """
        Set the X and Y coordinates of the Text Cursor

        :param int x: The X coordinate to set the cursor
        :param int y: The Y coordinate to set the cursor
        """
        self._txt_mode()
        self._write_reg16(0x2A, x)
        self._write_reg16(0x2C, y + self.vert_offset)

    # pylint: enable-msg=invalid-name

    def txt_color(self, fgcolor: int, bgcolor: int):
        """
        Set the text foreground and background colors

        :param int fgcolor: Foreground Color - The color of the text
        :param int bgcolor: Background Color - The color behind the text
        """
        self.set_color(fgcolor)
        self.set_bgcolor(bgcolor)
        self._write_data(self._read_reg(reg.FNCR1) & ~(1 << 6))

    def txt_trans(self, color: int) -> None:
        """
        Set the text foreground color with a transparent background

        :param int color: The color of the text
        """
        self._txt_mode()
        self.set_color(color)
        self._write_data(self._read_reg(reg.FNCR1) | 1 << 6)

    def txt_size(self, scale: int) -> None:
        """
        Set the Text Size (0-3)

        :param byte scale: The the size to scale the Text to
        """
        self._txt_mode()
        scale = min(scale, 3)
        self._write_data((self._read_reg(reg.FNCR1) & ~(0xF)) | (scale << 2) | scale)
        self._txt_scale = scale

    def txt_write(self, string: str) -> None:
        """
        Write text at the current cursor location using current settings

        :param str string: The text string to write
        """
        self._txt_mode()
        self._write_cmd(reg.MRWC)
        for char in string:
            self._write_data(char, True)
            if self._txt_scale > 0:
                time.sleep(0.001)

    # pylint: disable-msg=invalid-name
    def setxy(self, x: int, y: int) -> None:
        """
        Set the X and Y coordinates of the Graphic Cursor

        :param int x: The X coordinate to set the cursor
        :param int y: The Y coordinate to set the cursor
        """
        self._gfx_mode()
        self._write_reg16(reg.CURH0, x)
        self._write_reg16(reg.CURV0, y + self.vert_offset)

    # pylint: enable-msg=invalid-name

    def set_bgcolor(self, color: int) -> None:
        """
        Set the text background color

        :param int color: The color behind the text
        """
        self._write_reg(0x60, (color & 0xF800) >> 11)
        self._write_reg(0x61, (color & 0x07E0) >> 5)
        self._write_reg(0x62, (color & 0x001F))

    def set_color(self, color: int, debug: bool = False) -> None:
        """
        Set the foreground color for graphics/text

        :param int color: The of the text or graphics
        """
        r = (color & 0xF800) >> 11
        g = (color & 0x07E0) >> 5
        b = color & 0x001F
        if debug:
            print(f"set_color: {color} (R: {r}, G: {g}, B: {b})")
        self._write_reg(0x63, r)
        self._write_reg(0x64, g)
        self._write_reg(0x65, b)

    # pylint: disable-msg=invalid-name
    def pixel(self, x: int, y: int, color: int) -> None:
        """
        Draw a pixel at the X and Y coordinates of the specified color

        :param int x: The X coordinate to set the cursor
        :param int y: The Y coordinate to set the cursor
        :param int color: The color of the pixel
        """
        self.setxy(x, y + self.vert_offset)
        self._write_reg(reg.MRWC, struct.pack(">H", color), True)

    # pylint: enable-msg=invalid-name

    def push_pixels(self, pixel_data: bytearray) -> None:
        """
        Push a stream of pixel data to the screen.

        :param bytearray pixel_data: Raw pixel data to push
        """
        self._gfx_mode()
        self._write_reg(reg.MRWC, pixel_data, True)

    # pylint: disable-msg=invalid-name,too-many-arguments
    def set_window(
        self,
        x1: int,
        y1: int,
        win1_width: int,
        win1_height: int,
        color: int,
        filled: bool = True,
        debug: bool = False,
    ) -> None:
        """
        Set an Active Drawing Window, which can be used in
        conjuntion with push_pixels for faster drawing

        :param int x1: The X coordinate of the left side of the window
        :param int y1: The Y coordinate of the top side of the window
        :param int width: The width of the window
        :param int height: The height of the window
        :param Tuple[int, int, int] bg_color: The background color of the window as an RGB tuple
        """
        if x1 + win1_width >= self.width:
            win1_width = self.width - x1
        if y1 + win1_height >= self.height:
            win1_height = self.height - y1

        self._gfx_mode()

        # Set window coordinates
        self._write_reg16(reg.HSAW0, x1)
        self._write_reg16(reg.HEAW0, x1 + win1_width)
        self._write_reg16(reg.VSAW0, y1)
        self._write_reg16(reg.VEAW0, y1 + win1_height)

        # Set X and Y
        self._write_reg16(0x91, x1)
        self._write_reg16(0x93, y1 + self.vert_offset)

        # Set Width and Height
        self._write_reg16(0x95, win1_width)
        self._write_reg16(0x97, win1_height + self.vert_offset)

        self.set_color(color)
        if debug:
            print(f"Color: {color}")

        # Draw it
        self._write_reg(reg.DCR, 0xB0 if filled else 0x90)
        self._wait_poll(reg.DCR, reg.DCR_LNSQTR_STATUS)

    # pylint: enable-msg=invalid-name,too-many-arguments

    def lighten_mode(self):
        """Transparency Lighten"""
        self._gfx_mode()
        self._write_reg(0x52, 0b01010000, debug=False)

    # pylint: disable-msg=invalid-name,too-many-arguments
    def draw_cursor(self, x, y, inside_color, outline_color, debug: bool = False):
        """Draw 2-color crosshair cursor at x,y position"""
        # Draw the outline of the cursor
        for i in range(-4, 5):
            self.pixel(x + i, y - 4, outline_color)  # Top line
            self.pixel(x + i, y + 4, outline_color)  # Bottom line
            self.pixel(x - 4, y + i, outline_color)  # Left line
            self.pixel(x + 4, y + i, outline_color)  # Right line

        # Draw the inside of the cursor
        for i in range(-3, 4):
            self.pixel(x + i, y, inside_color)  # Horizontal line
            self.pixel(x, y + i, inside_color)  # Vertical line
        if debug:
            print(f"Drawing Cursor at: {x},{y}")


class RA8875(RA8875Display):
    """
    Graphics Library Class for the Display. Contains all the hardware accelerated geometry
    Functions. For full display functionality, use this class. Valid display sizes are
    currently 800x480 and 480x272.
    """

    def read_single_pixel(self, x: int, y: int, debug: bool = True) -> int:
        """
        Read the color of a single pixel from layer 0 of the display at x,y coordinates.

        :param int x: X coordinate of the pixel.
        :param int y: Y coordinate of the pixel.
        :param bool debug: Flag to enable debug printing.
        :return: Color of the pixel in RGB format (24-bit).
        :rtype: int
        """
        # Ensure x and y are within display bounds
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise ValueError(
                f"Coordinates ({x}, {y}) out of bounds for display size {self.width}x{self.height}"
            )
        if debug:
            print(f"Reading pixel at ({x}, {y})")

        # Set graphics mode
        self._gfx_mode()
        # Set read cursor position for layer0 (800x480 16-bit mode)
        self._write_reg16(reg.RCURH0, x, debug=False)
        self._write_reg16(reg.RCURV0, y + self.vert_offset, debug=False)
        # Set Memory Read/Write Control
        self._read_reg(reg.MRWC)
        # Read the color data
        dummy = self._read_data16(debug=False)  # Dummy read
        msb = self._read_data16(debug=False)  # MSB read

        # Extract color components from MSB
        green = (msb >> 8) & 0xFF  # Extracting 8 bits of green component
        blue = (msb >> 3) & 0xFF  # Extracting 8 bits of blue component
        red = (msb << 3) & 0xFF  # Extracting 8 bits of red component
        if debug:
            print(f"Dummy: {dummy} MSB: {msb}")
            print(f"Extracted Colors: {red}, {green}, {blue}")
            print(
                f"Binary values: Red: {red:08b}, Green: {green:08b}, Blue: {blue:08b}"
            )

        return red, green, blue

    # pylint: disable-msg=invalid-name,too-many-arguments
    def rect(
        self, x: int, y: int, width: int, height: int, color: int, filled: bool = False
    ) -> None:
        """
        Draw a rectangle (HW Accelerated)

        :param int x: The X coordinate of the left side of the rectangle
        :param int y: The Y coordinate of the top side of the rectangle
        :param int width: The width of the rectangle
        :param int height: The height of the rectangle
        :param int color: The color of the rectangle
        """
        self._rect_helper(x, y, x + width - 1, y + height - 1, color, filled=filled)

    def fill_rect(
        self, x: int, y: int, width: int, height: int, color: int, debug: bool = False
    ) -> None:
        """
        Draw a filled rectangle (HW Accelerated)

        :param int x: The X coordinate of the left side of the rectangle
        :param int y: The Y coordinate of the top side of the rectangle
        :param int width: The width of the rectangle
        :param int height: The height of the rectangle
        :param int color: The color of the rectangle
        """
        if debug:
            print(f"fill_rect color: {color}")
        self._rect_helper(x, y, x + width - 1, y + height - 1, color, True)

    def fill(self, color: int) -> None:
        """
        Fill the Entire Screen (HW Accelerated)

        :param int color: The color to Fill the screen
        """
        self._rect_helper(0, 0, self.width - 1, self.height - 1, color, True)

    def circle(self, x_center: int, y_center: int, radius: int, color: int) -> None:
        """
        Draw a circle (HW Accelerated)

        :param int x_center: The X coordinate of the center of the circle
        :param int y_center: The Y coordinate of the center of the circle
        :param int radius: The radius of the circle
        :param int color: The color of the circle
        """
        self._circle_helper(x_center, y_center, radius, color, False)

    def fill_circle(
        self, x_center: int, y_center: int, radius: int, color: int
    ) -> None:
        """
        Draw a filled circle (HW Accelerated)

        :param int x_center: The X coordinate of the center of the circle
        :param int y_center: The Y coordinate of the center of the circle
        :param int radius: The radius of the circle
        :param int color: The color of the circle
        """
        self._circle_helper(x_center, y_center, radius, color, True)

    def ellipse(
        self, x_center: int, y_center: int, h_axis: int, v_axis: int, color: int
    ) -> None:
        """
        Draw an ellipse (HW Accelerated)

        :param int x_center: The X coordinate of the center of the ellipse
        :param int y_center: The Y coordinate of the center of the ellipse
        :param int h_axis: The length of the horizontal axis
        :param int v_axis: The length of the vertical axis
        :param int color: The color of the ellipse
        """
        self._ellipse_helper(x_center, y_center, h_axis, v_axis, color, False)

    def fill_ellipse(
        self, x_center: int, y_center: int, h_axis: int, v_axis: int, color: int
    ) -> None:
        """
        Draw a Filled Ellipse (HW Accelerated)

        :param int x_center: The X coordinate of the center of the ellipse
        :param int y_center: The Y coordinate of the center of the ellipse
        :param int h_axis: The length of the horizontal axis
        :param int v_axis: The length of the vertical axis
        :param int color: The color of the ellipse
        """
        self._ellipse_helper(x_center, y_center, h_axis, v_axis, color, True)

    def curve(
        self,
        x_center: int,
        y_center: int,
        h_axis: int,
        v_axis: int,
        curve_part: int,
        color: int,
    ) -> None:
        """
        Draw a Curve (HW Accelerated)
        This is basically a quarter of an ellipse.

        :param int x_center: The X coordinate of the focal point of the curve
        :param int y_center: The Y coordinate of the focal point of the curve
        :param int h_axis: The length of the horizontal axis of the full ellipse
        :param int v_axis: The length of the vertical axis of the full ellipse
        :param byte curve_part: A number between 0-3 specifying the quarter section
        :param int color: The color of the curve
        """
        self._curve_helper(x_center, y_center, h_axis, v_axis, curve_part, color, False)

    def fill_curve(
        self,
        x_center: int,
        y_center: int,
        h_axis: int,
        v_axis: int,
        curve_part: int,
        color: int,
    ) -> None:
        """
        Draw a Filled Curve (HW Accelerated)
        This is basically a quarter of an ellipse.

        :param int x_center: The X coordinate of the focal point of the curve
        :param int y_center: The Y coordinate of the focal point of the curve
        :param int h_axis: The length of the horizontal axis of the full ellipse
        :param int v_axis: The length of the vertical axis of the full ellipse
        :param byte curve_part: A number between 0-3 specifying the quarter section
        :param int color: The color of the curve
        """
        self._curve_helper(x_center, y_center, h_axis, v_axis, curve_part, color, True)

    def triangle(
        self, x1: int, y1: int, x2: int, y2: int, x3: int, y3: int, color: int
    ) -> None:
        """
        Draw a Triangle (HW Accelerated)

        :param int x1: The X coordinate of the first point of the triangle
        :param int y1: The Y coordinate of the first point of the triangle
        :param int x2: The X coordinate of the second point of the triangle
        :param int y2: The Y coordinate of the second point of the triangle
        :param int x3: The X coordinate of the third point of the triangle
        :param int y3: The Y coordinate of the third point of the triangle
        :param int color: The color of the triangle
        """
        self._triangle_helper(x1, y1, x2, y2, x3, y3, color, False)

    def fill_triangle(
        self, x1: int, y1: int, x2: int, y2: int, x3: int, y3: int, color: int
    ) -> None:
        """
        Draw a Filled Triangle (HW Accelerated)

        :param int x1: The X coordinate of the first point of the triangle
        :param int y1: The Y coordinate of the first point of the triangle
        :param int x2: The X coordinate of the second point of the triangle
        :param int y2: The Y coordinate of the second point of the triangle
        :param int x3: The X coordinate of the third point of the triangle
        :param int y3: The Y coordinate of the third point of the triangle
        :param int color: The color of the triangle
        """
        self._triangle_helper(x1, y1, x2, y2, x3, y3, color, True)

    def hline(self, x: int, y: int, width: int, color: int) -> None:
        """
        Draw a Horizontal Line (HW Accelerated)

        :param int x: The X coordinate of the beginning point of the line
        :param int y: The Y coordinate of the beginning point of the line
        :param int width: The width of the line
        :param int color: The color of the line
        """
        self.line(x, y, x + width - 1, y, color)

    def vline(self, x: int, y: int, height: int, color: int) -> None:
        """
        Draw a Vertical Line (HW Accelerated)

        :param int x: The X coordinate of the beginning point of the line
        :param int y: The Y coordinate of the beginning point of the line
        :param int height: The height of the line
        :param int color: The color of the line
        """
        self.line(x, y, x, y + height - 1, color)

    def line(self, x1: int, y1: int, x2: int, y2: int, color: int) -> None:
        """
        Draw a Line (HW Accelerated)

        :param int x1: The X coordinate of the beginning point of the line
        :param int y1: The Y coordinate of the beginning point of the line
        :param int x2: The X coordinate of the end point of the line
        :param int y2: The Y coordinate of the end point of the line
        :param int color: The color of the line
        """
        self._gfx_mode()

        # Set Start Point
        self._write_reg16(0x91, x1)
        self._write_reg16(0x93, y1 + self.vert_offset)

        # Set End Point
        self._write_reg16(0x95, x2)
        self._write_reg16(0x97, y2 + self.vert_offset)

        self.set_color(color)

        # Draw it
        self._write_reg(reg.DCR, 0x80)
        self._wait_poll(reg.DCR, reg.DCR_LNSQTR_STATUS)

    def round_rect(
        self, x: int, y: int, width: int, height: int, radius: int, color: int
    ) -> None:
        """
        Draw a rounded rectangle

        :param int x: The X coordinate of the left side of the rectangle
        :param int y: The Y coordinate of the top side of the rectangle
        :param int width: The width of the rectangle
        :param int height: The height of the rectangle
        :param int radius: The radius of the corners
        :param int color: The color of the rectangle
        """
        self._gfx_mode()
        self._curve_helper(x + radius, y + radius, radius, radius, 1, color, False)
        self._curve_helper(
            x + width - radius - 1, y + radius, radius, radius, 2, color, False
        )
        self._curve_helper(
            x + radius, y + height - radius, radius, radius, 0, color, False
        )
        self._curve_helper(
            x + width - radius - 1, y + height - radius, radius, radius, 3, color, False
        )
        self.hline(x + radius, y, width - (radius * 2) - 1, color)
        self.hline(x + radius, y + height, width - (radius * 2) - 1, color)
        self.vline(x, y + radius, height - (radius * 2), color)
        self.vline(x + width - 1, y + radius, height - (radius * 2), color)

    def fill_round_rect(
        self, x: int, y: int, width: int, height: int, radius: int, color: int
    ) -> None:
        """
        Draw a filled rounded rectangle

        :param int x: The X coordinate of the left side of the rectangle
        :param int y: The Y coordinate of the top side of the rectangle
        :param int width: The width of the rectangle
        :param int height: The height of the rectangle
        :param int radius: The radius of the corners
        :param int color: The color of the rectangle
        """
        self._gfx_mode()
        self._curve_helper(x + radius, y + radius, radius, radius, 1, color, True)
        self._curve_helper(
            x + width - radius - 1, y + radius, radius, radius, 2, color, True
        )
        self._curve_helper(
            x + radius, y + height - radius, radius, radius, 0, color, True
        )
        self._curve_helper(
            x + width - radius - 1, y + height - radius, radius, radius, 3, color, True
        )
        self._rect_helper(
            x + radius, y, x + width - radius - 1, y + height - 1, color, True
        )
        self._rect_helper(
            x, y + radius, x + width - 1, y + height - radius - 1, color, True
        )

    def _circle_helper(
        self, x: int, y: int, radius: int, color: int, filled: bool
    ) -> None:
        """General Circle Drawing Helper"""
        self._gfx_mode()

        # Set X, Y, and Radius
        self._write_reg16(0x99, x)
        self._write_reg16(0x9B, y + self.vert_offset)
        self._write_reg(0x9D, radius)

        self.set_color(color)

        # Draw it
        self._write_reg(
            reg.DCR, reg.DCR_CIRC_START | (reg.DCR_FILL if filled else reg.DCR_NOFILL)
        )
        self._wait_poll(reg.DCR, reg.DCR_CIRC_STATUS)

    def _rect_helper(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        color: int,
        filled: bool,
        debug: bool = False,
    ) -> None:
        """General Rectangle Drawing Helper"""
        self._gfx_mode()

        # Set X and Y
        self._write_reg16(0x91, x1)
        self._write_reg16(0x93, y1 + self.vert_offset)

        # Set Width and Height
        self._write_reg16(0x95, x2)
        self._write_reg16(0x97, y2 + self.vert_offset)
        if debug:
            print(f"_rect_helper: color={color}")
        self.set_color(color)

        # Draw it
        self._write_reg(reg.DCR, 0xB0 if filled else 0x90)
        self._wait_poll(reg.DCR, reg.DCR_LNSQTR_STATUS)

    def _triangle_helper(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        x3: int,
        y3: int,
        color: int,
        filled: bool,
    ) -> None:
        """General Triangle Drawing Helper"""
        self._gfx_mode()

        # Set Point Coordinates
        self._write_reg16(0x91, x1)
        self._write_reg16(0x93, y1 + self.vert_offset)
        self._write_reg16(0x95, x2)
        self._write_reg16(0x97, y2 + self.vert_offset)
        self._write_reg16(0xA9, x3)
        self._write_reg16(0xAB, y3 + self.vert_offset)

        self.set_color(color)

        # Draw it
        self._write_reg(reg.DCR, 0xA1 if filled else 0x81)
        self._wait_poll(reg.DCR, reg.DCR_LNSQTR_STATUS)

    def _curve_helper(
        self,
        x_center: int,
        y_center: int,
        h_axis: int,
        v_axis: int,
        curve_part: int,
        color: int,
        filled: bool,
    ) -> None:
        """General Curve Drawing Helper"""
        self._gfx_mode()

        # Set X and Y Center
        self._write_reg16(0xA5, x_center)
        self._write_reg16(0xA7, y_center + self.vert_offset)

        # Set Long and Short Axis
        self._write_reg16(0xA1, h_axis)
        self._write_reg16(0xA3, v_axis)

        self.set_color(color)

        # Draw it
        self._write_reg(reg.ELLIPSE, (0xD0 if filled else 0x90) | (curve_part & 0x03))
        self._wait_poll(reg.ELLIPSE, reg.ELLIPSE_STATUS)

    def _ellipse_helper(
        self,
        x_center: int,
        y_center: int,
        h_axis: int,
        v_axis: int,
        color: int,
        filled: bool,
    ) -> None:
        """General Ellipse Drawing Helper"""
        self._gfx_mode()

        # Set X and Y  Center
        self._write_reg16(0xA5, x_center)
        self._write_reg16(0xA7, y_center + self.vert_offset)

        # Set Long and Short Axis
        self._write_reg16(0xA1, h_axis)
        self._write_reg16(0xA3, v_axis)

        self.set_color(color)

        # Draw it
        self._write_reg(reg.ELLIPSE, 0xC0 if filled else 0x80)
        self._wait_poll(reg.ELLIPSE, reg.ELLIPSE_STATUS)
