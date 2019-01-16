# Quick test of RA8875 with Feather M4
import time
import random
import busio
import digitalio
import board

import adafruit_ra8875 as ra8875
from adafruit_ra8875 import color565

# Configuration for CS and RST pins:
cs_pin = digitalio.DigitalInOut(board.D9)
rst_pin = digitalio.DigitalInOut(board.D10)
#int_pin = digitalio.DigitalInOut(board.D11)

# Config for display baudrate (default max is 12mhz):
BAUDRATE = 8000000

# Setup SPI bus using hardware SPI:
spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Create and setup the RA8875 display:
display = ra8875.RA8875(spi, cs=cs_pin, rst=rst_pin, baudrate=BAUDRATE)
display.on(True)
display.gpiox(True)
display.pwm1_config(True, ra8875._PWM_CLK_DIV1024)
display.pwm1_out(255)
display.gfx_mode()

display.fill_screen(color565(255, 0, 0))
time.sleep(0.500)
display.fill_screen(color565(255, 255, 0))
time.sleep(0.500)
display.fill_screen(color565(0, 255, 0))
time.sleep(0.500)
display.fill_screen(color565(0, 255, 255))
time.sleep(0.500)
display.fill_screen(color565(255, 0, 255))
time.sleep(0.500)
display.fill_screen(color565(0, 0, 0))
time.sleep(0.500)
display.fill_screen(color565(255, 255, 255))
display.draw_circle(100, 100, 50, color565(0, 0, 0)) # 400 pixel circle centered
display.fill_circle(100, 100, 49, color565(0, 255, 0)) # 400 pixel circle centered

display.fill_rect(11, 11, 398, 198, color565(0, 0, 255))
display.draw_rect(10, 10, 400, 200, color565(0, 255, 0))
display.fill_round_rect(200, 10, 200, 100, 10, color565(255, 0, 0))
display.draw_round_rect(199, 9, 202, 102, 12, color565(0, 255, 0))

display.draw_ellipse(300, 100, 100, 40, color565(255, 0, 0))
display.fill_ellipse(300, 100, 98, 38, color565(0, 255, 0))


#display.fill_circle(int(display.width / 2) - 1, int(display.height / 2) - 1, 200, color565(255, 0, 0)) # 400 pixel circle centered
#display.draw_line(0, 0, display.width - 1, display.height - 1, color565(0, 0, 255))

# Main loop:
#while True:
# Fill the screen red, green, blue, then black:
#for color in ((255, 0, 0), (0, 255, 0), (0, 0, 255)):
#display.fill(color565((255, 0, 0)))
# Clear the display
#display.fill(0)
# Draw a red pixel in the center.
#display.pixel(display.width//2, display.height//2, color565(255, 0, 0))
# Pause 2 seconds.
#time.sleep(2)
# Clear the screen a random color
#display.fill(color565(random.randint(0, 255),
#                      random.randint(0, 255),
#                      random.randint(0, 255)))
# Pause 2 seconds.
#time.sleep(2)
