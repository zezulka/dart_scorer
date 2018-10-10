#!/usr/bin/env python
# -*- coding: utf-8 -*-

from luma.led_matrix.device import max7219 as max7219_backend
from luma.core.interface.serial import spi, noop
from luma.core.virtual import sevensegment

class MAX7219:
    def __init__(self):
        serial = spi(port=0, device=0, gpio=noop())
        self.device = max7219_backend(serial, cascaded=1)
        self.seg = sevensegment(self.device)

    def show_message(self, text):
        self.seg.text = text

    def clean_up(self):
        self.device.contrast(0x7F)
