[![Build Status](https://travis-ci.org/zezulka/dart_scorer.svg?branch=master)](https://travis-ci.org/zezulka/dart_scorer)

Funny little project for my own amusement.
If everything goes well, this should work very similar to a darts scorer.

This Python script is to be primarily run on a Raspberry Pi 
(but you can port it to other devices of course). Tests can be run
on non-RPi devices, too (which can be beneficial for the application
development).

There are three devices which I would like to wire together:

1. MAX7219 7 segment display (8 digits wide)
2. LCD module 1602A (2 rows of 16 cells)
3. A very basic numeric keyboard from (Ctech, model KBN-01)
   (Linux assigned the device an id usb-SIGMACHIP_USB_Keyboard-event-kbd)

Prerequisites

Raspi
1. ```pip3 install max7219 evdev luma.led_matrix pillow```
2. ```sudo apt-get install libopenjp2-7```

Other (for development on non-Raspi devices)
1. sudo dnf install python3-devel
2. pip3 install max7219 evdev luma.led_matrix pillow

Installation and execution

1. ```git clone https://github.com/zezulka/dart_scorer```
2. ```cd dart_scorer```
3. ```. bin/dart_scorer.sh```
