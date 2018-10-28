#!/usr/bin/python
# This script is a rewrite from a Matt Hawkins' script.
# 1 : GND
# 2 : 5V
# 3 : Contrast (0-5V)*
# 4 : RS (Register Select)
# 5 : R/W (Read Write)       - GROUND THIS PIN
# 6 : Enable or Strobe
# 7 : Data Bit 0             - NOT USED
# 8 : Data Bit 1             - NOT USED
# 9 : Data Bit 2             - NOT USED
# 10: Data Bit 3             - NOT USED
# 11: Data Bit 4
# 12: Data Bit 5
# 13: Data Bit 6
# 14: Data Bit 7
# 15: LCD Backlight +5V**
# 16: LCD Backlight GND
import RPi.GPIO as GPIO
import time

# Define GPIO to LCD mapping
LCD_RS = 21
LCD_E = 20
LCD_D4 = 26
LCD_D5 = 19
LCD_D6 = 13
LCD_D7 = 6
# Define some device constants
LCD_WIDTH = 16  # Maximum characters per line
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80  # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0  # LCD RAM address for the 2nd line
# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005


class LcdDisplay:
    def __init__(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)  # Use BCM GPIO numbers
        GPIO.setup(LCD_E, GPIO.OUT)  # E
        GPIO.setup(LCD_RS, GPIO.OUT)  # RS
        GPIO.setup(LCD_D4, GPIO.OUT)  # DB4
        GPIO.setup(LCD_D5, GPIO.OUT)  # DB5
        GPIO.setup(LCD_D6, GPIO.OUT)  # DB6
        GPIO.setup(LCD_D7, GPIO.OUT)  # DB7
        self.lcd_init()

    def clear(self):
        self.lcd_string("", LCD_LINE_1)
        self.lcd_string("", LCD_LINE_2)

    # To be used with resource cleaning.
    def clean_up(self):
        lcd_byte(0x01, LCD_CMD)
        self.clear()
        GPIO.cleanup()

    def lcd_init(self):
        # Initialise display
        lcd_byte(0x33, LCD_CMD)  # 110011 Initialise
        lcd_byte(0x32, LCD_CMD)  # 110010 Initialise
        lcd_byte(0x06, LCD_CMD)  # 000110 Cursor move direction
        lcd_byte(0x0C, LCD_CMD)  # 001100 Display On,Cursor Off, Blink Off
        lcd_byte(0x28, LCD_CMD)  # 101000 Data length, number of lines, font size
        lcd_byte(0x01, LCD_CMD)  # 000001 Clear display
        time.sleep(E_DELAY)

    def lcd_string(self, message, line):
        message = message.ljust(LCD_WIDTH, " ")
        lcd_byte(line, LCD_CMD)
        for i in range(LCD_WIDTH):
            lcd_byte(ord(message[i]), LCD_CHR)

    def first_line(self, message):
        self.lcd_string(message, LCD_LINE_1)

    def second_line(self, message):
        self.lcd_string(message, LCD_LINE_2)


# And now... a bit of magic!
def lcd_byte(bits, mode):
    # Send byte to data pins
    # bits = data
    # mode = True  for character
    #        False for command
    GPIO.output(LCD_RS, mode)  # RS

    # High bits
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)
    if bits & 0x10 == 0x10:
        GPIO.output(LCD_D4, True)
    if bits & 0x20 == 0x20:
        GPIO.output(LCD_D5, True)
    if bits & 0x40 == 0x40:
        GPIO.output(LCD_D6, True)
    if bits & 0x80 == 0x80:
        GPIO.output(LCD_D7, True)

    lcd_toggle_enable()
    # Low bits
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)
    if bits & 0x01 == 0x01:
        GPIO.output(LCD_D4, True)
    if bits & 0x02 == 0x02:
        GPIO.output(LCD_D5, True)
    if bits & 0x04 == 0x04:
        GPIO.output(LCD_D6, True)
    if bits & 0x08 == 0x08:
        GPIO.output(LCD_D7, True)

    lcd_toggle_enable()


def lcd_toggle_enable():
    time.sleep(E_DELAY)
    GPIO.output(LCD_E, True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_E, False)
    time.sleep(E_DELAY)
