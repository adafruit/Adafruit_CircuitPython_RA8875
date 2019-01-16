# Quick test of RA8875 with Feather M4
import time
import random
import busio
import digitalio
import board

import adafruit_ra8875 as ra8875
from adafruit_ra8875 import color565

BLACK = color565(0, 0, 0)
RED = color565(255, 0, 0)
BLUE = color565(0, 255, 0)
GREEN = color565(0, 0, 255)
YELLOW = color565(255, 255, 0)
CYAN = color565(0, 255, 255)
MAGENTA = color565(255, 0, 255)
WHITE = color565(255, 255, 255)

# Configuration for CS and RST pins:
cs_pin = digitalio.DigitalInOut(board.D9)
rst_pin = digitalio.DigitalInOut(board.D10)
int_pin = digitalio.DigitalInOut(board.D11)

# Config for display baudrate (default max is 12mhz):
BAUDRATE = 8000000

# Setup SPI bus using hardware SPI:
spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI, MISO=board.MISO)

# Create and setup the RA8875 display:
display = ra8875.RA8875(spi, cs=cs_pin, rst=rst_pin, intr=int_pin, baudrate=BAUDRATE)
display.on(True)
display.gpiox(True)
display.pwm1_config(True, ra8875._PWM_CLK_DIV1024)
display.pwm1_out(255)
display.gfx_mode()

display.fill(RED)
time.sleep(0.500)
display.fill(YELLOW)
time.sleep(0.500)
display.fill(BLUE)
time.sleep(0.500)
display.fill(CYAN)
time.sleep(0.500)
display.fill(MAGENTA)
time.sleep(0.500)
display.fill(BLACK)
time.sleep(0.500)
display.fill(WHITE)
display.circle(100, 100, 50, BLACK)
display.fill_circle(100, 100, 49, BLUE)

display.fill_rect(11, 11, 398, 198, GREEN)
display.rect(10, 10, 400, 200, BLUE)
display.fill_round_rect(200, 10, 200, 100, 10, RED)
display.round_rect(199, 9, 202, 102, 12, BLUE)
display.pixel(10, 10, BLACK)
display.pixel(11, 11, BLACK)
display.line(10, 10, 200, 100, RED)
display.triangle(200, 15, 250, 100, 150, 125, BLACK)
display.fill_triangle(200, 16, 249, 99, 151, 124, YELLOW)
display.ellipse(300, 100, 100, 40, RED)
display.fill_ellipse(300, 100, 98, 38, BLUE)
display.curve(50, 100, 80, 40, 2, BLACK)
display.fill_curve(50, 100, 78, 38, 2, WHITE)

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
