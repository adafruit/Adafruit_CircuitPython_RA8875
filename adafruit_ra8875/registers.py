# SPDX-FileCopyrightText: 2019 Melissa LeBlanc-Williams for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`adafruit_ra8875.registers`
====================================================

A useful index of RA8875 Registers

* Author(s): Melissa LeBlanc-Williams
"""

# Command/Data for SPI
DATWR = b"\x00"  # Data Write
DATRD = b"\x40"  # Data Read
CMDWR = b"\x80"  # Command Write
CMDRD = b"\xC0"  # Status Read

# Registers and Bits
PWRR = 0x01  # Power Register
PWRR_DISPON = 0x80  # Display on
PWRR_DISPOFF = 0x00  # Display off
PWRR_SLEEP = 0x02  # Sleep mode
PWRR_NORMAL = 0x00  # Normal mode
PWRR_SOFTRESET = 0x01  # Software reset

MRWC = 0x02  # Memory Read/Write Control

GPIOX = 0xC7  # GPIOX

PLLC1 = 0x88  # PLL Control 1
PLLC1_PLLDIV1 = 0x00  # PLLDIV1

PLLC2 = 0x89  # PLL Control 2
PLLC2_DIV4 = 0x02  # PLLDIV4

SYSR = 0x10  # System Configuration

SYSR_8BPP = 0x00  # 8 bits per pixel
SYSR_16BPP = 0x0C  # 16 bits per pixel
SYSR_MCU8 = 0x00  # MCU 8-bit bus
SYSR_MCU16 = 0x03  # MCU 16-bit bus

PCSR = 0x04  # PWM and Clock Control

PCSR_PDATR = 0x00  # PWM: Data from PWM pin
PCSR_PDATL = 0x80  # PWM: Data from PWM register
PCSR_CLK = 0x00  # PWM: System clock
PCSR_2CLK = 0x01  # PWM: 2 System clocks
PCSR_4CLK = 0x02  # PWM: 4 System clocks
PCSR_8CLK = 0x03  # PWM: 8 System clocks

HDWR = 0x14  # Hardware Width

HNDFTR = 0x15  # Non-Display Area Start

HNDFTR_DE_HIGH = 0x00  # DE signal high
HNDFTR_DE_LOW = 0x80  # DE signal low

HNDR = 0x16  # Non-Display Area End
HSTR = 0x17  # HSYNC Start
HPWR = 0x18  # HSYNC Pulse Width
HPWR_LOW = 0x00  # HSYNC Low
HPWR_HIGH = 0x80  # HSYNC High

VDHR0 = 0x19  # Vertical Start
VDHR1 = 0x1A
VNDR0 = 0x1B  # Vertical End
VNDR1 = 0x1C
VSTR0 = 0x1D  # VSYNC Start
VSTR1 = 0x1E

VPWR = 0x1F  # VSYNC Pulse Width
VPWR_LOW = 0x00  # VSYNC Low
VPWR_HIGH = 0x80  # VSYNC High

FNCR0 = 0x21  # Font Control 0
FNCR1 = 0x22  # Font Control 1

HSAW0 = 0x30  # Horizontal Start Point 0 of Active Window
HSAW1 = 0x31  # Horizontal Start Point 1 of Active Window
VSAW0 = 0x32  # Vertical Start Point 0 of Active Window
VSAW1 = 0x33  # Vertical Start Point 1 of Active Window

HEAW0 = 0x34  # Horizontal End Point 0 of Active Window
HEAW1 = 0x35  # Horizontal End Point 1 of Active Window
VEAW0 = 0x36  # Vertical End Point of Active Window 0
VEAW1 = 0x37  # Vertical End Point of Active Window 1

MCLR = 0x8E  # Memory Clear Control

MCLR_START = 0x80  # Start Clearing Memory
MCLR_STOP = 0x00  # Stop Clearing Memory
MCLR_READSTATUS = 0x80  # Read Status
MCLR_FULL = 0x00  # Full Clear
MCLR_ACTIVE = 0x40  # Clear Active

DCR = 0x90  # Drawing Control
DCR_LNSQTR_START = 0x80  # Line / Square / Triangle Drawing Start
DCR_LNSQTR_STOP = 0x00  # Line / Square / Triangle Drawing Stop
DCR_LNSQTR_STATUS = 0x80  # Line / Square / Triangle Drawing Status
DCR_CIRC_START = 0x40  # Circle Drawing Start
DCR_CIRC_STATUS = 0x40  # Circle Drawing Status
DCR_CIRC_STOP = 0x00  # Circle Drawing Stop
DCR_FILL = 0x20  # Fill Shape
DCR_NOFILL = 0x00  # Do Not Fill Shape
DCR_DRAWLN = 0x00  # Draw Line
DCR_DRAWTRI = 0x01  # Draw Triangle
DCR_DRAWSQU = 0x10  # Draw Square

ELLIPSE = 0xA0  # Ellipse Setup
ELLIPSE_STATUS = 0x80  # Ellipse Setup Status

MWCR0 = 0x40  # Memory Write Control
MWCR0_GFXMODE = 0x00  # Graphics Mode
MWCR0_TXTMODE = 0x80  # Text Mode

MRCD = 0x45  # Memory Read Cursor Direction

CURH0 = 0x46  # Memory Write Cursor Horizontal Position Register 0
CURH1 = 0x47  # Memory Write Cursor Horizontal Position Register 1
CURV0 = 0x48  # Memory Write Cursor Vertical Position Register 0
CURV1 = 0x49  # Memory Write Cursor Vertical Position Register 1

RCURH0 = 0x4A  # Memory Read Cursor Horizontal Position Register 0
RCURH1 = 0x4B  # Memory Read Cursor Horizontal Position Register 1
RCURV0 = 0x4C  # Memory Read Cursor Vertical Position Register 0
RCURV1 = 0x4D  # Memory Read Cursor Vertical Position Register 1

P1CR = 0x8A  # Pointer 1 Control Register
P1CR_ENABLE = 0x80  # Enable Pointer 1
P1CR_DISABLE = 0x00  # Disable Pointer 1
P1CR_CLKOUT = 0x10  # Clock out Pointer 1
P1CR_PWMOUT = 0x00  # PWM out Pointer 1

P1DCR = 0x8B  # Pointer 1 Default Color Register

P2CR = 0x8C  # Pointer 2 Control Register
P2CR_ENABLE = 0x80  # Enable Pointer 2
P2CR_DISABLE = 0x00  # Disable Pointer 2
P2CR_CLKOUT = 0x10  # Clock out Pointer 2
P2CR_PWMOUT = 0x00  # PWM out Pointer 2

P2DCR = 0x8D  # Pointer 2 Default Color Register

PWM_CLK_DIV1024 = 0x0A  # PWM Clock Divider

TPCR0 = 0x70  # Touch Panel Control Register 0
TPCR0_ENABLE = 0x80  # Enable Touch Panel
TPCR0_DISABLE = 0x00  # Disable Touch Panel
TPCR0_WAIT_512CLK = 0x00  # Wait 512 clocks
TPCR0_WAIT_1024CLK = 0x10  # Wait 1024 clocks
TPCR0_WAIT_2048CLK = 0x20  # Wait 2048 clocks
TPCR0_WAIT_4096CLK = 0x30  # Wait 4096 clocks
TPCR0_WAIT_8192CLK = 0x40  # Wait 8192 clocks
TPCR0_WAIT_16384CLK = 0x50  # Wait 16384 clocks
TPCR0_WAIT_32768CLK = 0x60  # Wait 32768 clocks
TPCR0_WAIT_65536CLK = 0x70  # Wait 65536 clocks
TPCR0_WAKEENABLE = 0x08  # Wake Enable
TPCR0_WAKEDISABLE = 0x00  # Wake Disable
TPCR0_ADCCLK_DIV4 = 0x02  # ADC Clock Divider 4
TPCR0_ADCCLK_DIV8 = 0x03  # ADC Clock Divider 8
TPCR0_ADCCLK_DIV16 = 0x04  # ADC Clock Divider 16
TPCR0_ADCCLK_DIV32 = 0x05  # ADC Clock Divider 32
TPCR0_ADCCLK_DIV64 = 0x06  # ADC Clock Divider 64
TPCR0_ADCCLK_DIV128 = 0x07  # ADC Clock Divider 128

TPCR1 = 0x71  # Touch Panel Control Register 1
TPCR1_AUTO = 0x00  # Automatic Mode
TPCR1_MANUAL = 0x40  # Manual Mode
TPCR1_DEBOUNCE = 0x04  # Debounce
TPCR1_NODEBOUNCE = 0x00  # No Debounce

TPXH = 0x72  # Touch Panel X High Register
TPYH = 0x73  # Touch Panel Y High Register
TPXYL = 0x74  # Touch Panel XY Low Register

INTC1 = 0xF0  # Interrupt Control Register 1
INTC1_KEY = 0x10  # Interrupt: Key
INTC1_DMA = 0x08  # Interrupt: DMA
INTC1_TP = 0x04  # Interrupt: Touch Panel
INTC1_BTE = 0x02  # Interrupt: BTE

INTC2 = 0xF1  # Interrupt Control Register 2
INTC2_KEY = 0x10  # Interrupt: Key
INTC2_DMA = 0x08  # Interrupt: DMA
INTC2_TP = 0x04  # Interrupt: Touch Panel
INTC2_BTE = 0x02  # Interrupt: BTE

WAITTIME_LUT = {
    TPCR0_ADCCLK_DIV4: TPCR0_WAIT_512CLK,
    TPCR0_ADCCLK_DIV8: TPCR0_WAIT_1024CLK,
    TPCR0_ADCCLK_DIV16: TPCR0_WAIT_2048CLK,
    TPCR0_ADCCLK_DIV32: TPCR0_WAIT_4096CLK,
    TPCR0_ADCCLK_DIV64: TPCR0_WAIT_8192CLK,
    TPCR0_ADCCLK_DIV128: TPCR0_WAIT_16384CLK,
}
