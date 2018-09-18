Funny little project for my own amusement.
If everything goes well, this should work very similar to a darts scorer.

There are three devices which I would like to wire together:

1. MAX7219 7 segment display (8 digits wide)
2. LCD module 1602A (2 rows of 16 cells)
3. A very basic numeric keyboard from (Ctech, model KBN-01)
   (Linux assigned the device an id usb-SIGMACHIP_USB_Keyboard-event-kbd)

Installation
pip3 install max7219
pip3 install evdev
pip3 install luma.led_matrix
pip3 install pillow
sudo apt-get install libopenjp2-7